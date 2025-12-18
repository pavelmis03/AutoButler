# библиотека графических элементов для
from tkinter import *
# дополнительные виджеты
from tkinter import ttk
# шрифты
from tkinter import font
# сообщения
from tkinter.messagebox import showerror, showwarning, showinfo
# бибиблиотека для работы с ini файлами
import configparser

# библиотека для sql-запросов
import pymysql as sql
import pandas as pd
# модули для работы с операционной системой
import os
import shutil

# библиотека для работы с изображениями
from PIL import ImageTk, Image  # pip install pillow

# формы для админа
from forms.formAdmin import *

# подключаем файл с функциями обработки данных, получаемых от форм
from funcs.funcsAuth import *
# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts

# поиск пользователя
def findUser(db, etrName, etrSurname, etrPatr, etrPhone, etrEmail, etrLogin):
    pass

# функция изменения режима работы с пользователями: добавление, удаление, редактирование
def changeWorkMode(workMode, btnAddUser, btnChangeUser, btnDelUser):
    if (workMode.get() == "addUser"):
        btnAddUser.state = "enabled"
        btnChangeUser.state = "disabled"
        btnDelUser.state = "disabled"
        btnFindUser.state = "disabled"

    if (workMode.get() == "changeUser"):
        btnAddUser.state = "disabled"
        btnChangeUser.state = "enabled"
        btnDelUser.state = "disabled"
        btnFindUser.state = "enabled"

    if (workMode.get() == "delUser"):
        btnAddUser.state = "disabled"
        btnChangeUser.state = "disabled"
        btnDelUser.state = "enabled"
        btnFindUser.state = "enabled"


# добавление нового пользователя
def addNewUserData(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass):
    qr = f'''INSERT INTO db.users 
            (user_name, user_surname, user_patronymic, user_description, user_email, user_phone, user_login, user_pass, user_role) 
            VALUES ('{ etrName }', '{ etrSurname }', '{ etrPatr }', '{ tbComm }', '{ etrEmail }', '{ etrPhone }', '{ etrLogin }', '{ etrPass }', '{ cbxRole }');
            '''
    try:
        # создаем объект курсора для выбора нужной строки
        cur = db.cursor()
        # выполняем query-запрос
        cur.execute(qr)
        # сохраняем изменения в БД
        db.commit()
        showinfo(title="Добавление пользователя", message="Пользователь успешно добавлен!")
    except Exception as e:
        showerror(title="Добавление пользователя",
                  message="Произошла непредвиденная ошибка при добавлении пользователя, попробуйте еще раз")
    except:
        showerror(title="Добавление пользователя", message="Произошла непредвиденная ошибка при добавлении пользователя, попробуйте еще раз")

# проверка телефона
def checkPhone(etrPhone):
    phoneErr = False
    # список ошибок
    err = []
    # проверяем, что поле заполнено
    if ((etrPhone == "") or (etrPhone == "79991112233")):
        err.append("Заполните поле 'Телефон'")
    else: # нет смысла в остальных проверках, если поле не заполнено
        # проверяем, что номер телефона записан правильно
        for num in etrPhone:
            # если в номере есть что-то, кроме цифр
            if (not num in "0123456789"):
                phoneErr = True
        if (phoneErr):
            err.append("Телефон должен состоять только из цифр")
        # проверяем, что телефон начинается с 7
        if (etrPhone[0] != "7"):
            err.append("Телефон должен начинаться с 7")
        # проверяем длину телефона
        if (len(etrPhone) != 11):
            err.append("Телефон состоять из 11 цифр")

    return err

# проверка почты
def checkEmail(etrEmail):
    # список ошибок
    err = []
    # проверяем, что поле заполнено
    if ((etrEmail == "") or (etrEmail == "post@gmail.com")):
        err.append("Заполните поле 'Почта'")
    else: # нет смысла в остальных проверках, если поле не заполнено
        # проверка на наличие собачки
        if (not "@" in etrEmail):
            err.append("Не обнаружен значок '@'")
        # проверка на наличие точки
        if (not "." in etrEmail):
            err.append("Не обнаружен значок '.'")
        # список почтовых сервисов
        serv = ["gmail", "yandex", "ya", "mail", "yahoo", "bsdmail", "outlook", "hotmail", "protonmail", "web"]
        # список доменов для почтовых адресов
        dom = ["com", "ru", "edu", "de", "by", "kz", "ua", "de", "fr", "re", "online", "net", "io", "info", "org", "gov", "biz", "me"]
        # флаг проверки на то, что у нас правильный сервис и домен
        flag = True
        for el in serv:
            # если сервис встретился, значит, все правильно
            if (el in etrEmail):
                flag = False
        # если мы не встретили ни одного известного сервиса
        if (flag):
            err.append("Неправильный почтовый сервис")
        # флаг проверки на то, что у нас правильный сервис и домен
        flag = True
        for el in dom:
            # если сервис встретился, значит, все правильно
            if (el in etrEmail):
                flag = False
        # если мы не встретили ни одного известного сервиса
        if (flag):
            err.append("Неправильный почтовый домен")

    return err

def checkLogin(db, etrLogin):
    # запрос на получение данных о пользователях из БД
    qr = '''SELECT users.user_login AS login
                FROM db.users
        '''
    # чтение данных из БД с помощью query запроса
    df = pd.read_sql(qr, con=db)
    # фильтруем данные таблицы users для поиска соответствий введенным данным
    filterData = df.query(f"login == '{etrLogin}'", inplace=False)

    # список ошибок
    err = []
    # проверяем, что поле заполнено
    if ((etrLogin == "") or (etrLogin == "Введите логин")):
        err.append("Заполните поле 'Логин'")
    else:  # нет смысла в остальных проверках, если поле не заполнено
        # если мы нашли пользователя с таким логином
        if (not filterData.empty):
            err.append("Пользователь с таким логином уже существует, выберите другой логин")

    return err

def checkNewUserData(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass):
    # список ошибок, допущенных при заполнении формы
    err = []
    # проверяем заполнение основных полей
    if ((etrName == "") or (etrName == "Введите имя")):
        err.append("Заполните поле 'Имя'")
    if ((etrSurname == "") or (etrSurname == "Введите фамилию")):
        err.append("Заполните поле 'Фамилия'")
    if ((etrPatr == "") or (etrPatr == "Введите отчество")):
        err.append("Заполните поле 'Отчество'")
    if ((cbxRole == "") or (cbxRole == "Выберите роль")):
        err.append("Выберите роль")
    # проверяем телефон
    tmpErr = checkPhone(etrPhone)
    # если ошибки в телефоне есть
    if (len(tmpErr) != 0):
        # добавляем их к основному списку ошибок
        err = err + tmpErr
    # проверяем почту
    tmpErr = checkEmail(etrEmail)
    # если ошибки в почте есть
    if (len(tmpErr) != 0):
        # добавляем их к основному списку ошибок
        err = err + tmpErr
    # проверяем логин
    tmpErr = checkLogin(db, etrLogin)
    # если ошибки в логине есть
    if (len(tmpErr) != 0):
        # добавляем их к основному списку ошибок
        err = err + tmpErr

    if (etrPass == ""):
        err.append("Заполните поле 'Пароль'")

    # если были обнаружены ошибки в заполнении формы
    if (len(err) != 0):
        # выводим не больше 5 ошибок
        for i in range(min(5, len(err))):
            showerror(title="Данные заполнены неверно!", message=err[i])
    else:
        addNewUserData(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass)

