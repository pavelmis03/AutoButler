# библиотека для sql-запросов
import pymysql as sql
import pandas as pd
# библиотека для построения графика
import matplotlib.pyplot as plt

# основные формы
from forms.formMain import *
# формы авторизации
import forms.formAuth as fAuth
# формы для админа
from forms.formAdmin import createAdminMainForm
# формы для аналитика
from forms.formAnalyst import createAnalystMainForm
# формы для оператора
from forms.formOperator import createOperatorMainForm
# формы для менеджера
from forms.formManager import createManagerMainForm

# функция проверки логина и пароля при входе
def checkSignInData(event, db, login, pwd, role, lblErr, etrPwd, root):
    # запрос на получение данных о пользователях из БД
    qr = '''SELECT users.id_user AS id,
            users.user_login AS login,
            users.user_pass AS pwd,
            users.user_role AS role,
            users.user_email AS email,
            users.user_phone AS phone,
            users.user_name AS name,
            users.user_surname AS surname,
            users.user_patronymic AS patr,
            users.user_description AS descr
            FROM db.users
    '''
    # чтение данных из БД с помощью query запроса
    df = pd.read_sql(qr, con=db)
    # фильтруем данные таблицы users для поиска соответствий введенным данным
    filterData = df.query(f"login == '{ login }' and pwd == '{ pwd }' and role == '{ role }'", inplace=False)

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

    # функция определения вызываемого окна в зависимости от роли
    chooseNextForm(db, filterData, root)

# функция выхода из программы
def logOut(db, root):
    # создаем форму для работы с БД
    fAuth.createSignInForm(db, root)

# функция определения вызываемого окна в зависимости от роли
def chooseNextForm(db, df, root):
    # упрощаем датафрейм до обычного словаря с нужными полями
    userData = {
        "login": df["login"][0],
        "pwd": df["pwd"][0],
        "role": df["role"][0],
        "email": df["email"][0],
        "phone": df["phone"][0],
        "name": df["name"][0],
        "surname": df["surname"][0],
        "patr": df["patr"][0],
        "descr": df["descr"][0],
    }
    # меняем роли на более удобные названия и вызываем функции стартовых окон
    if (userData["role"] == consts.ROLELIST[0][0]):
        userData["role"] = consts.ROLELIST[1][0]   # "admin"
        createAdminMainForm(db, root, userData)
    elif (userData["role"] == consts.ROLELIST[0][1]):
        userData["role"] = consts.ROLELIST[1][1]   # "analyst"
        createAnalystMainForm(db, root, userData)
    elif (userData["role"] == consts.ROLELIST[0][2]):
        userData["role"] = consts.ROLELIST[1][2]   # "operator"
        createOperatorMainForm(db, root, userData)
    elif (userData["role"] == consts.ROLELIST[0][3]):
        userData["role"] = consts.ROLELIST[1][3]   # "manager"
        createManagerMainForm(db, root, userData)
