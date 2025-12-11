# библиотека для sql-запросов
import pymysql as sql
import pandas as pd
# библиотека для построения графика
import matplotlib.pyplot as plt

# основные формы
from formMain import *

# функция проверки логина и пароля при входе
def checkSignInData(event, db, login, pwd, role, lblErr, etrPwd, root):
    # запрос на получение данных о пользователях из БД
    qr = '''SELECT users.id_user AS id,
            users.user_login AS login,
            users.user_pass AS pwd,
            users.user_role AS role,
            users.user_description AS descr
            FROM db.users
    '''
    # чтение данных из БД с помощью query запроса
    df = pd.read_sql(qr, con=db)
    # фильтруем данные таблицы users для поиска соответствий введенным данным
    filterData = df.query(f"login == '{ login }' and pwd == '{ pwd }' and role == '{ role }'", inplace=False)
    # заглушка
    # filterData = ["Иван Васильевич",
    #               [["Reno Logan", "01.05.2025", "Андрей", "Шиномонтаж; Полировка дисков"],
    #                ["Reno Logan", "22.06.2025", "Андрей", "Плановое ТО"],
    #                ["Audi A7", "06.07.2025", "Сергей", "Сход-развал"]
    #                ],
    #               [["Reno Logan", 4, 2011, 192392, "Ирина Евгеньевна"], ["Audi A7", 2, 2018, 67821, "Иван Васильевич"]]]

    # если ничего не найдено - данные для авторизации неверны
    if (filterData.empty):
    # заглушка
    #if (login != "User" and pwd != "12345"):
        # сообщаем об ошибке
        lblErr.config(text="Ошибка авторизации. Проверьте данные для входа!")
        # запускаем функцию, которая уберет предупреждение через 4 секунды
        root.after(4000, lambda: lblErr.config(text=""))
        # очищаем окно ввода пароля
        etrPwd.delete(0, END)
        # выходим из функции
        return
    # удаляем старое окно
    root.destroy()
    # создаем форму главного экрана
    createMainForm(db, filterData)