import telebot
from telebot import types
import sqlite3
import datetime

# Подключение к базе данных
conn = sqlite3.connect('C:/DB_leave_and_chill/dbshka.db', check_same_thread=False)
cursor = conn.cursor()

# Создание объекта бота
bot = telebot.TeleBot('6265697228:AAHqLh8jhd0lCiZvj0JaJdTKYgjSpzRWq00')

# Словарь для хранения данных пользователя
user_data = {}


# Функция для получения информации о сотруднике из базы данных
def get_user_info(user_id):
    cursor.execute("SELECT first_name, last_name, patronymic, position FROM Users WHERE user_id=?", (user_id,))
    user_info = cursor.fetchone()
    if user_info:
        first_name, last_name, patronymic, position = user_info
        return f"{first_name} {last_name} {patronymic}\nДолжность: {position}"
    return "Информация о сотруднике не найдена"


# Функция для вывода заявок на отпуска
def display_vacations(chat_id, approved):
    cursor.execute("SELECT * FROM Holidays WHERE approved=?", (approved,))
    vacations = cursor.fetchall()

    if not vacations:
        bot.send_message(chat_id, f"{'Подтвержденных' if approved else 'Неподтвержденных'} заявок нет.")
    else:
        for vacation in vacations:
            user_id, start_date, finish_date, approved, vacation_id = vacation
            user_info = get_user_info(user_id)
            status_text = "Не утвержден" if approved else "Утвержден"
            message_text = f"{user_info}\n{start_date} - {finish_date} – {status_text}"
            send_vacation_message(chat_id, message_text, vacation_id)


# Функция для отправки сообщения о заявке
def send_vacation_message(chat_id, message_text, vacation_id):
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton(text='Утвердить', callback_data=f"approve_vacation_{vacation_id}")
    cancel_btn = types.InlineKeyboardButton(text='Отменить', callback_data=f"cancel_vacation_{vacation_id}")
    markup.add(approve_btn, cancel_btn)
    bot.send_message(chat_id, message_text, reply_markup=markup)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Заявки на отпуска сотрудников")
    item2 = types.KeyboardButton("Мои отпуска")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)


# Обработчик кнопок "Заявки на отпуска сотрудников" и "Мои отпуска"
@bot.message_handler(func=lambda message: message.text in ["Заявки на отпуска сотрудников", "Мои отпуска"])
def handle_menu(message):
    chat_id = message.chat.id

    if message.text == "Заявки на отпуска сотрудников":
        bot.send_message(chat_id, "Выберите опцию:", reply_markup=get_vacation_menu_markup())
    elif message.text == "Мои отпуска":
        display_my_vacations(chat_id)


# Функция для вывода меню заявок начальника
def get_vacation_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Подтвержденные заявки")
    item2 = types.KeyboardButton("Неподтвержденные заявки")
    markup.add(item1, item2)
    return markup


# Функция для вывода заявок текущего пользователя
def display_my_vacations(chat_id):
    user_id = chat_id
    cursor.execute("SELECT id, start_date, finish_date, approved FROM Holidays WHERE user_id=?", (user_id,))
    vacations = cursor.fetchall()

    if not vacations:
        bot.send_message(chat_id, "У вас нет заявок на отпуск.")
    else:
        for vacation in vacations:
            vacation_id, start_date_str, finish_date_str, approved = vacation

            start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
            finish_date = datetime.datetime.strptime(finish_date_str, '%d.%m.%Y')

            duration = (finish_date - start_date).days
            status = "Утвержден" if approved else "Не утвержден"

            bot.send_message(
                chat_id,
                f"Отпуск с {start_date.strftime('%d.%m.%Y')} по {finish_date.strftime('%d.%m.%Y')} – {status}"
            )


# Обработчик кнопок "Подтвержденные заявки" и "Неподтвержденные заявки"
@bot.message_handler(func=lambda message: message.text in ["Подтвержденные заявки", "Неподтвержденные заявки"])
def handle_vacation_approval(message):
    chat_id = message.chat.id
    approved = 1 if message.text == "Подтвержденные заявки" else 0
    display_vacations(chat_id, approved)


# Обработчик команды "Утвердить" или "Отменить" заявки
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_vacation_") or call.data.startswith("cancel_vacation_"))
def handle_vacation_action(call):
    chat_id = call.message.chat.id
    user_id = chat_id
    parts = call.data.split("_")
    if len(parts) == 3:
        vacation_id = parts[2]

    if call.data.startswith("approve_vacation_"):
        vacation_id = call.data.split("_")[2]
    
        # Обновляем статус отпуска в базе данных
        cursor.execute("UPDATE Holidays SET approved = 1 WHERE id = ?", (vacation_id,))
        conn.commit()    
        # Отправляем уведомление о том, что отпуск утвержден
        bot.send_message(call.message.chat.id, "Отпуск утвержден.")

    elif call.data.startswith("cancel_vacation_"):
        # Отменяем отпуск и удаляем его из базы данных
        cursor.execute("DELETE FROM Holidays WHERE id=?", (vacation_id,))
        conn.commit()
        bot.send_message(chat_id, "Отпуск отменен.")

    # Обновляем меню заявок начальника
    bot.send_message(chat_id, "Выберите опцию:", reply_markup=get_vacation_menu_markup())


if __name__ == "__main__":
    bot.polling()
