![gosling_for_bot](https://github.com/AkkForParactic/paractic/assets/147721446/154120f1-4c47-45a7-9ad0-30894a073cea)

Это телеграм-бот для планирования отпусков. Простой, а главное эффективный способ оформить отпуск, не выходя из любимого мессенджера.
# Как его запустить?
1. `/start` - команда для запуска бота.

# Использование
Начало использования бота выглядит следующим образом:

Бот предлагает выбрать роль - начальник или сотрудник.

![image](https://github.com/AkkForParactic/paractic/assets/147721446/c8a8b1af-ae7c-43e0-bc33-aee8cb3e182e)

# Если выбрана роль Сотрудника:

![image](https://github.com/AkkForParactic/paractic/assets/147721446/bac6d321-0041-4b2b-b78f-c309d46bfa9a)

Бот предлагает войти или зарегистрироваться.

![image](https://github.com/AkkForParactic/paractic/assets/147721446/3a4134c5-6f8d-4971-ba08-a279c7463657)

При регистрации бот запрашивает ФИО, возраст, должность, номер телефона, дату рождения пользователя.

![image](https://github.com/AkkForParactic/paractic/assets/147721446/d3682d21-fee3-4494-9d81-3fc48448d630)

После регистрации бот генерирует и отправляет пользователю пароль.

![image](https://github.com/AkkForParactic/paractic/assets/147721446/d5f5a4e3-92b1-446b-85ac-c5dcb29cf30b)

После входа открывается главное меню.

# Меню
![image](https://github.com/AkkForParactic/paractic/assets/147721446/6dcac150-e5b9-4b5d-8f4d-fce191746e49)

В главном меню доступны пункты:
<b>"Запланировать отпуск"</b> - позволяет запланировать новый отпуск, указав даты начала и окончания.
<b>"Мои отпуска"</b> - показывает список запланированных отпусков пользователя.

![image](https://github.com/AkkForParactic/paractic/assets/147721446/6798b481-29ea-483a-a75a-5d624998d40c)
 

При планировании нового отпуска можно выбрать действия:

![image](https://github.com/AkkForParactic/paractic/assets/147721446/6efd56a9-3d56-42f3-9e7c-e26819c4e4f0)

Добавить в список отпусков:

![image](https://github.com/AkkForParactic/paractic/assets/147721446/7e0419eb-91f4-437b-a075-3665f75b7fc1)

Отредактировать даты:

![image](https://github.com/AkkForParactic/paractic/assets/147721446/1f1e111e-a370-465d-ba4c-cc74339391fb)


![image](https://github.com/AkkForParactic/paractic/assets/147721446/7b20a6e7-dbd7-4d34-9c7f-0919748ea3ae)

Отменить запланированный отпуск:

![image](https://github.com/AkkForParactic/paractic/assets/147721446/857cb15c-ec56-457b-8ef1-dab73d70746e)


# Просмотр отпусков

Просмотреть отпуска можно нажав кнопку <b>"Мои отпуска"</b>:

![image](https://github.com/AkkForParactic/paractic/assets/147721446/f7e0e8cf-e0b3-454c-a0cc-49298e918d72)


# Если выбрана роль Начальника:

Бот выводит клавиатуру с двумя кнопками: "Заявки на отпуска сотрудников" и "Мои отпуска": 

![image](https://github.com/AkkForParactic/paractic/assets/147721446/d91ca077-945c-4366-a43e-2393d630d07d)

Если нажата кнопка "Заявки на отпуска сотрудников":

Бот выводит клавиатуру с кнопками "Подтвержденные заявки" и "Неподтвержденные заявки":

![image](https://github.com/AkkForParactic/paractic/assets/147721446/4a4e370e-9ff0-4ab3-9559-d4fd0a560d6b)

При нажатии на эти кнопки бот выводит список соответствующих заявок на отпуска от сотрудников, для каждой заявки выводится ФИО и должность сотрудника, даты отпуска, статус:

![image](https://github.com/AkkForParactic/paractic/assets/147721446/cc963aba-32ce-4d9f-bb09-caa9da7bfaaf)



![image](https://github.com/AkkForParactic/paractic/assets/147721446/301033ea-bc6d-420d-86d2-989fb3bd94eb)


При нажатии на кнопки "Утвердить"/"Отменить":
  
· Меняется статус заявки в базе данных

· Пользователю выводится уведомление об изменении статуса

· Обновляется список заявок на отпуска

![image](https://github.com/AkkForParactic/paractic/assets/147721446/f566ba93-fcd4-4b5b-93e5-df9424165096)


![image](https://github.com/AkkForParactic/paractic/assets/147721446/cc5c09c6-4299-4d62-8132-c6e3abca6fb4)


Таким образом реализуется удобный интерфейс для работы с заявками на отпуска внутри компании.






