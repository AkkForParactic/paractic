import sqlite3
import telebot
from telebot import types
import datetime
import secrets
import string
import UI_Boss
import multiprocessing
import os


  

os.system('C:/Leave_and_Chill_FILES/UI_Boss.py')







# Параметры для ограничения длительности отпуска
current_year = datetime.date.today().year
max_vacation_duration = datetime.timedelta(days=14)

bot_token = "6265697228:AAHqLh8jhd0lCiZvj0JaJdTKYgjSpzRWq00"
conn = sqlite3.connect('C:/DB_leave_and_chill/dbshka.db', check_same_thread=False)
cursor = conn.cursor()

global login, first_name, last_name, patronymic, phone_number, position

# Создаем таблицу для хранения пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS Users
                  (user_id INTEGER PRIMARY KEY,
                   username TEXT,
                   password TEXT,
                   first_name TEXT,
                   last_name TEXT,
                   patronymic TEXT,
                   birthdate TEXT,
                   phone_number TEXT,
                   position TEXT)''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS Holidays
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER,
                   approved INTEGER,
                   start_date TEXT,
                   finish_date TEXT)''')
conn.commit()


# 2. Генерируем уникальный идентификатор для каждого отпуска
def generate_holiday_id():
    cursor.execute("SELECT MAX(id) FROM Holidays")
    max_id = cursor.fetchone()[0]
    return max_id + 1 if max_id else 1









bot = telebot.TeleBot(bot_token)

# Словарь для хранения данных пользователя
user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    boss = types.InlineKeyboardButton(text='Начальник', callback_data="Начальник")
    sotr = types.InlineKeyboardButton(text='Сотрудник', callback_data="Сотрудник")
    markup.add(boss, sotr)
    msg = bot.send_message(message.chat.id, 'Выбери свою касту', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: (call.data == "Начальник" or call.data == "Сотрудник" or call.data == "Войти" or call.data == "Зарегистрироваться") or call.data.startswith("view_vacation_"))
def callback_worker(call):
    if call.data == "Начальник" or call.data == "Сотрудник":
        markup = types.InlineKeyboardMarkup()
        login_btn = types.InlineKeyboardButton(text='Войти', callback_data="Войти")
        register_btn = types.InlineKeyboardButton(text='Зарегистрироваться', callback_data="Зарегистрироваться")
        markup.add(login_btn, register_btn)
        bot.send_message(call.message.chat.id, 'Что выберешь?', reply_markup=markup)

    elif call.data == "Войти":
        bot.send_message(call.message.chat.id, 'Введите свой логин')
        bot.register_next_step_handler(call.message, enter_login)

    elif call.data == "Зарегистрироваться":
        bot.send_message(call.message.chat.id, 'Сейчас будем проходить регистрацию. Как вас зовут?')
        bot.register_next_step_handler(call.message, register_name)

# Обработка кнопок "view_vacation_<vacation_id>"
    elif call.data.startswith("view_vacation_"):
        vacation_id = int(call.data.split("_")[2])
        
        # Получаем данные выбранного отпуска из базы данных
        cursor.execute("SELECT id, start_date, finish_date, approved FROM Holidays WHERE id=?", (vacation_id,))
        vacation = cursor.fetchone()
        
        if vacation:
            vacation_id, start_date_str, finish_date_str, approved = vacation
            
            # Преобразуем строки в даты
            start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
            finish_date = datetime.datetime.strptime(finish_date_str, '%d.%m.%Y')
            
            duration = (finish_date - start_date).days
            status = "Утвержден" if approved else "Не утвержден"
            
            # Сохраняем информацию о выбранном отпуске в данных пользователя
            user_data[call.message.chat.id] = {"vacation_id": vacation_id}

            # Отправляем сообщение о выбранном отпуске и кнопки управления
            bot.send_message(call.message.chat.id, f"Выбран отпуск:\n"
                                                   f"{duration} дней с {start_date.strftime('%d.%m.%Y')} по {finish_date.strftime('%d.%m.%Y')} – {status}")
            
            # Создаем кнопки управления для выбранного отпуска
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Утвердить")
            item2 = types.KeyboardButton("Отменить")
            item3 = types.KeyboardButton("Редактировать даты")
            markup.add(item1, item2, item3)
            bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=markup)
            
            # Сохраняем информацию о выбранном отпуске в данных пользователя
            user_data[call.message.chat.id] = {"vacation_id": vacation_id}



def enter_login(message):
    global login
    login = message.text
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, check_login_password)

def check_login_password(message):
    global login, user_id, login_attempts

    cursor.execute("SELECT user_id FROM Users WHERE username=?", (login,))
    user = cursor.fetchone()

    if user is None:
        login_attempts += 1
        if login_attempts >= 3:
            markup = types.InlineKeyboardMarkup()
            register_btn = types.InlineKeyboardButton(text='Зарегистрироваться', callback_data="Зарегистрироваться")
            markup.add(register_btn)
            bot.send_message(message.chat.id, 'Логин не найден. Попробуйте еще раз или зарегистрируйтесь.', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Логин не найден. Попробуйте еще раз.')
            bot.register_next_step_handler(message, enter_login)
    else:
        login_attempts = 0
        user_id = user[0]
        password = message.text

        login = user_id

        cursor.execute("SELECT password FROM Users WHERE user_id=?", (user_id,))
        stored_password = cursor.fetchone()[0]

        if password == stored_password:
            bot.send_message(message.chat.id, 'Вход выполнен успешно!')
            show_main_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Неверный пароль. Попробуйте еще раз.')

def register_name(message):
    global user_id, login, first_name
    first_name = message.text
    bot.send_message(message.chat.id, 'Введите вашу фамилию')
    bot.register_next_step_handler(message, register_surname)

def register_surname(message):
    global user_id, login, first_name, last_name
    last_name = message.text
    bot.send_message(message.chat.id, 'Сколько вам лет?')
    bot.register_next_step_handler(message, register_age)

def register_age(message):
    global user_id, login, first_name, last_name, age
    age = message.text
    bot.send_message(message.chat.id, 'Введите ваше отчество')
    bot.register_next_step_handler(message, register_patronymic)

def register_patronymic(message):
    global user_id, login, first_name, last_name, age, patronymic
    patronymic = message.text
    bot.send_message(message.chat.id, 'Введите ваш номер телефона')
    bot.register_next_step_handler(message, register_phone)

def register_phone(message):     
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Бухгалтер")
    item2 = types.KeyboardButton("Программист")
    item3 = types.KeyboardButton("Сисадмин")
    item4 = types.KeyboardButton("Менеджер")
    item5 = types.KeyboardButton("По знакомству")
    markup.add(item1, item2, item3, item4, item5) 

    global user_id, login, first_name, last_name, age, patronymic, phone_number
    phone_number = message.text
    bot.send_message(message.chat.id, 'Выберите вашу должность', reply_markup=markup)
    bot.register_next_step_handler(message, register_position)

def register_position(message):
    
    global user_id, login, first_name, last_name, age, patronymic, phone_number, position
    position = message.text
    bot.send_message(message.chat.id, 'Введите вашу дату рождения в формате ДД.ММ.ГГГГ')
    bot.register_next_step_handler(message, register_birthdate)


def generate_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(12))  # 12 символов в пароле
    return password

def register_birthdate(message):
    global user_id, first_name, last_name, patronymic, birthdate, phone_number, position
    birthdate = message.text
    user_id = message.from_user.id
    password = generate_password()  # Генерируем пароль
    
    cursor.execute('''INSERT INTO Users (username, password, first_name, last_name, patronymic, birthdate, phone_number, position)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (user_id, password, first_name, last_name, patronymic, birthdate, phone_number, position))
    conn.commit()
    
    # Отправляем пароль пользователю
    bot.send_message(message.chat.id, f'Регистрация успешно завершена! Ваш пароль: {password}')
    
    show_main_menu(message.chat.id)


def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Запланировать отпуск")
    item2 = types.KeyboardButton("Мои отпуска")
    markup.add(item1, item2)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

# Обработчики для планирования отпуска
@bot.message_handler(func=lambda message: message.text == "Запланировать отпуск")
def plan_vacation(message):
    current_date = datetime.date.today()  
    
    if current_date.year > current_year or (current_date.year == current_year and current_date.month < 12):
        bot.send_message(message.chat.id, f'Помните: Запланировать отпуск можно только в текущем и следующем году, в прошлом году нельзя')
        user_data[message.chat.id] = {}        
        bot.send_message(message.chat.id, 'Введите дату Начала отпуска (ДД.ММ.ГГГГ):')
        bot.register_next_step_handler(message, validate_start_date)


# Обработчик для кнопки "Мои отпуска"


@bot.message_handler(func=lambda message: message.text == "Мои отпуска")
def my_vacations(message):
    # Получаем отпуска сотрудника по его user_id
    cursor.execute("SELECT id, start_date, finish_date, approved FROM Holidays WHERE user_id=? ORDER BY start_date", (message.chat.id,))
    vacations = cursor.fetchall()

    if vacations:
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for vacation in vacations:
            vacation_id, start_date_str, finish_date_str, approved = vacation
            
            # Преобразуем строки в даты
            start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
            finish_date = datetime.datetime.strptime(finish_date_str, '%d.%m.%Y')
            
            # Вычисляем продолжительность отпуска
            duration = (finish_date - start_date).days
            
            status = "Утвержден" if approved else "Не утвержден"
            
            # Создаем кнопку для каждого отпуска и добавляем ее в разметку
            button_text = f"{duration} дней с {start_date.strftime('%d.%m.%Y')} по {finish_date.strftime('%d.%m.%Y')} – {status}"
            button = types.InlineKeyboardButton(text=button_text, callback_data=f"view_vacation_{vacation_id}")
            markup.add(button)
        
        bot.send_message(message.chat.id, "Выберите отпуск:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас пока нет отпусков.")






def validate_start_date(message):
    try:
        # Попытка преобразовать введенную строку в дату
        start_date = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        
        # Записываем начальную дату в данные пользователя
        user_data[message.chat.id] = {'start_date': start_date}
        
        # Ожидаем окончание отпуска
        bot.send_message(message.chat.id, f'Введите дату Окончания отпуска ({start_date.strftime("%d.%m.%Y")}):')
        bot.register_next_step_handler(message, validate_finish_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите дату в формате ДД.ММ.ГГГГ')

def validate_finish_date(message):
    try:
        # Попытка преобразовать введенную строку в дату
        finish_date = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        
        # Проверяем, что дата окончания больше даты начала
        if finish_date > user_data[message.chat.id]['start_date']:
            # Записываем дату окончания в данные пользователя
            user_data[message.chat.id]['finish_date'] = finish_date
            
            # Рассчитываем количество дней между началом и окончанием отпуска
            vacation_duration = (finish_date - user_data[message.chat.id]['start_date']).days
            
            # Отправляем сообщение о планировании отпуска
            bot.send_message(message.chat.id, f'Планирование отпуска:\n'
                                              f'Начало отпуска: {user_data[message.chat.id]["start_date"].strftime("%d.%m.%Y")}\n'
                                              f'Окончание отпуска: {user_data[message.chat.id]["finish_date"].strftime("%d.%m.%Y")}\n'
                                              f'Продолжительность отпуска: {vacation_duration} дней')
            
            # Изменяем клавиатуру под текстовым полем
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Добавить в мои отпуска")
            item2 = types.KeyboardButton("Утвердить")
            item3 = types.KeyboardButton("Отменить")
            item4 = types.KeyboardButton("Редактировать даты")
            markup.add(item1, item2, item3, item4)
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Дата окончания отпуска должна быть позже даты начала. Попробуйте еще раз.')
            bot.register_next_step_handler(message, validate_finish_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите дату в формате ДД.ММ.ГГГГ')
        


# Обработчики для кнопок "Добавить в мои отпуска", "Утвердить", "Отменить", "Редактировать даты"
@bot.message_handler(func=lambda message: message.text in ["Добавить в мои отпуска"])
def handle_action(message):
    if message.text == "Добавить в мои отпуска":
        user_id = message.chat.id
        start_date = user_data[message.chat.id]['start_date']
        finish_date = user_data[message.chat.id]['finish_date']
        vacation_duration = (finish_date - start_date).days

        if vacation_duration <= 14:
            cursor.execute("INSERT INTO Holidays (user_id, approved, start_date, finish_date) VALUES (?, ?, ?, ?)",
               (user_id, 0, start_date.strftime('%d.%m.%Y'), finish_date.strftime('%d.%m.%Y')))
            conn.commit()



            bot.send_message(message.chat.id, f'Отпуск на {vacation_duration} дней с {start_date.strftime("%d.%m.%Y")} по {finish_date.strftime("%d.%m.%Y")} сохранен в «Мои отпуска»')

        else:
            bot.send_message(message.chat.id, 'Отпуск можно запланировать не более чем на 14 дней. Попробуйте еще раз.')

    
    # Возвращаем кнопки под строкой набора текста
    show_main_menu(message.chat.id)

# Добавьте обработчики для кнопок "Утвердить", "Отменить", "Редактировать даты" и логику для этих действий
# ...


@bot.message_handler(func=lambda message: message.text in ["Утвердить", "Отменить", "Редактировать даты", "Отменить изменения", "Сохранить"])
def handle_vacation_action(message):
    user_id = message.chat.id
    vacation_id = user_data.get(user_id, {}).get("vacation_id")
    
    if vacation_id is None:
        bot.send_message(user_id, "Не выбран отпуск. Выберите отпуск из списка.")
        return
    
    # Получаем данные выбранного отпуска из базы данных
    cursor.execute("SELECT id, start_date, finish_date, approved FROM Holidays WHERE id=?", (vacation_id,))
    vacation = cursor.fetchone()
    
    if vacation:
        if message.text == "Утвердить":
            # Отмечаем отпуск как утвержденный
            cursor.execute("UPDATE Holidays SET approved=1 WHERE id=?", (vacation_id,))
            conn.commit()
            bot.send_message(user_id, "Отпуск утвержден.")

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Запланировать отпуск")
            item2 = types.KeyboardButton("Мои отпуска")
            markup.add(item1, item2)
            bot.send_message(user_id, "Выберите действие:", reply_markup=markup)
        
        elif message.text == "Отменить":
            # Удаляем отпуск из базы данных
            cursor.execute("DELETE FROM Holidays WHERE id=?", (vacation_id,))
            conn.commit()
            bot.send_message(user_id, "Отпуск отменен.")

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Запланировать отпуск")
            item2 = types.KeyboardButton("Мои отпуска")
            markup.add(item1, item2)
            bot.send_message(user_id, "Выберите действие:", reply_markup=markup)
        
        elif message.text == "Редактировать даты":
            # Удаляем кнопку "Редактировать даты"
            markup = types.ReplyKeyboardRemove()
            bot.send_message(user_id, "Планирование отпуска:\n"
                                      "Введите новую дату Начала отпуска (ДД.ММ.ГГГГ):", reply_markup=markup)
            bot.register_next_step_handler(message, edit_vacation_start_date)
        
        elif message.text == "Отменить изменения":
            # Отменяем редактирование, не сохраняем изменения
            del user_data[user_id]
            bot.send_message(user_id, "Изменения отменены.")

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Запланировать отпуск")
            item2 = types.KeyboardButton("Мои отпуска")
            markup.add(item1, item2)
            bot.send_message(user_id, "Выберите действие:", reply_markup=markup)
        
        elif message.text == "Сохранить":
            # Сохраняем новые даты отпуска
            new_start_date = user_data.get(user_id, {}).get("new_start_date")
            new_finish_date = user_data.get(user_id, {}).get("new_finish_date")
            
            if new_start_date and new_finish_date:
                cursor.execute("UPDATE Holidays SET start_date=?, finish_date=? WHERE id=?", (new_start_date, new_finish_date, vacation_id))
                conn.commit()
                markup = types.ReplyKeyboardRemove(selective=False)  # Удаляем клавиатуру
                bot.send_message(user_id, f"Отпуск отредактирован и сохранен: {new_start_date} - {new_finish_date}", reply_markup=markup)
                
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("Запланировать отпуск")
                item2 = types.KeyboardButton("Мои отпуска")
                markup.add(item1, item2)
                bot.send_message(user_id, "Выберите действие:", reply_markup=markup)
                
            
            else:
                bot.send_message(user_id, "Не удалось сохранить изменения. Пожалуйста, укажите новые даты отпуска.")
            
            # Удаляем данные о редактировании
            del user_data[user_id]

# Обработчики для редактирования дат
def edit_vacation_start_date(message):
    user_id = message.chat.id
    new_start_date_str = message.text
    
    try:
        new_start_date = datetime.datetime.strptime(new_start_date_str, '%d.%m.%Y')
        user_data[user_id]["new_start_date"] = new_start_date_str
        
        bot.send_message(user_id, f"Введите новую дату окончания отпуска (ДД.ММ.ГГГГ):")
        bot.register_next_step_handler(message, edit_vacation_finish_date)
    
    except ValueError:
        bot.send_message(user_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")

def edit_vacation_finish_date(message):
    user_id = message.chat.id
    new_finish_date_str = message.text

    try:
        # Получаем данные о редактируемом отпуске из пользовательских данных
        vacation_data = user_data.get(user_id, {})
        vacation_id = vacation_data.get("vacation_id")

        if vacation_id:
            cursor.execute("SELECT start_date, finish_date FROM Holidays WHERE id=?", (vacation_id,))
            vacation = cursor.fetchone()

            if vacation:
                start_date_str, finish_date_str = vacation

                user_data[user_id]["new_finish_date"] = new_finish_date_str

                bot.send_message(user_id, f"Планирование отпуска:\n"
                                          f"Начало отпуска: {start_date_str}\n"
                                          f"Окончание отпуска: {finish_date_str}")

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("Сохранить")
                item2 = types.KeyboardButton("Отменить изменения")
                markup.add(item1, item2)
                bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

            else:
                bot.send_message(user_id, 'Отпуск не найден.')

        else:
            bot.send_message(user_id, 'Отпуск не выбран.')

    except ValueError:
        bot.send_message(user_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")

    user_id = message.chat.id
    new_finish_date_str = message.text



    try:
        # Получаем данные о редактируемом отпуске из пользовательских данных
        vacation_data = user_data.get(user_id, {})
        vacation_id = vacation_data.get("vacation_id")

        
        # Выводим информацию о редактируемом отпуске и кнопки "Сохранить" и "Отменить изменения"
        vacation_id = user_data.get(user_id, {}).get("vacation_id")
        cursor.execute("SELECT id, start_date, finish_date FROM Holidays WHERE id=?", (vacation_id,))
        vacation = cursor.fetchone()

        if vacation_id:
            cursor.execute("SELECT start_date, finish_date FROM Holidays WHERE id=?", (vacation_id,))
            vacation = cursor.fetchone()

            if vacation:
                start_date_str, finish_date_str = vacation
                start_date_obj = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
                finish_date_obj = datetime.datetime.strptime(finish_date_str, '%d.%m.%Y')
                vacation_duration = (finish_date_obj - start_date_obj).days

                user_data[user_id]["new_finish_date"] = new_finish_date_str
        
                if vacation:
                    vacation_id, start_date_str, finish_date_str = vacation
                    bot.send_message(user_id, f"Планирование отпуска:\n"
                                              f"Начало отпуска: {start_date_str}\n"
                                              f"Окончание отпуска: {finish_date_str}\n"
                                              f"Продолжительность отпуска: {vacation_duration} дней")

                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("Сохранить")
                    item2 = types.KeyboardButton("Отменить изменения")
                    markup.add(item1, item2)
                    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)
                    
                else:
                    bot.send_message(message.chat.id, 'Отпуск не найден.')
        else:
            bot.send_message(user_id, 'Отпуск не выбран.')
        

    except ValueError:
        bot.send_message(user_id, "Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")
    



if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
