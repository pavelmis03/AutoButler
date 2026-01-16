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

# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts

# изменение пользователя
def changeUser(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass, userData, findData, cbxFindUserRes):
    # сначала проверяем правильность заполнения данных
    flag = checkNewUserData(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass, False)
    # если мы успешно добавили нового пользователя, нужно удалить старого
    if (flag):
        flag = delUser(db, userData, findData, cbxFindUserRes, False)
        # если успешно удалили
        if (flag):
            showinfo(title="Изменение пользователя", message="Пользователь был успешно изменен!")
            return True
        else:
            showerror(title="Изменение пользователя",
                      message="Произошла ошибка (delOldUser) при изменении пользователя, скорее всего, вы не выбрали пользователя для изменения, попробуйте еще раз")
    else:
        showerror(title="Удаление пользователя",
                  message="Произошла ошибка (addNewUser) при изменении пользователя, попробуйте еще раз")

    return False

# удалить пользователя, если выбран
def delUser(db, userData, findData, cbxFindUserRes, message=True):
    # если пользователи были ныйдены и выбраны
    if (userData != "Нет совпадений"):
        # разбираем строку на имя, фамилию и логин name surname (login)
        name, surname, login = userData.split()
        # убираем скобки
        login = login[1:-1]
        qr = f'''DELETE FROM users
                WHERE user_name = '{name}' AND user_surname = '{surname}' AND user_login = '{login}';
              '''
        try:
            # создаем объект курсора для выбора нужной строки
            cur = db.cursor()
            # выполняем query-запрос
            cur.execute(qr)
            # сохраняем изменения в БД
            db.commit()
            if (message):
                showinfo(title="Удаление пользователя", message="Пользователь успешно удален!")

            # вызываем снова функцию поиска, чтобы обновить список пользователей, доступных для удаления
            findUser(db, findData, cbxFindUserRes)

            return True
        except Exception as e:
            if (message):
                showerror(title="Удаление пользователя",
                      message="Произошла непредвиденная ошибка при удалении пользователя, попробуйте еще раз")
        # except:
        #     if (message):
        #         showerror(title="Удаление пользователя",
        #               message="Произошла непредвиденная ошибка при удалении пользователя, попробуйте еще раз")
    else:
        if (message):
            showinfo(title="Удаление пользователя", message="Найдите и выберите пользователя для удаления")
    return False

# поиск пользователя по фрагменту данных
def findUser(db, findData, cbxFindUserRes):
    # запрос на получение данных о пользователях из БД
    qr = '''SELECT
                users.user_role AS role, 
                users.user_login AS login,
                users.user_email AS email,
                users.user_phone AS phone,
                users.user_name AS name,
                users.user_surname AS surname,
                users.user_patronymic AS patr
                FROM db.users
        '''
    # чтение данных из БД с помощью query запроса
    df = pd.read_sql(qr, con=db)
    # фильтруем данные таблицы users для поиска соответствий введенным данным
    filterData = df.query(f"login == '{findData}' or phone == '{findData}' or surname == '{findData}'", inplace=False)

    # если ничего не найдено - сообщаем об этом
    if (filterData.empty):
        showinfo(title="Поиск пользователя", message="Пользователь с такими данными не найден")
        # и очищаем данные выпадающего списка
        cbxFindUserRes["values"] = ["Нет совпадений"]
        cbxFindUserRes.current(0)
    else:
        arr = []
        # проходим по найденным пользователям
        for i in range(len(filterData)):
            # добавляем в выпадающий список
            str = filterData.iloc[i]["name"] + " " + filterData.iloc[i]["surname"] + " (" + filterData.iloc[i]["login"] + ")"
            arr.append(str)
        cbxFindUserRes["values"] = arr[:]
        cbxFindUserRes.current(0)


# функция изменения режима работы с пользователями: добавление, удаление, редактирование
def changeWorkMode(workMode, btnAddUser, btnChangeUser, btnDelUser, btnFindUser):
    if (workMode.get() == "addUser"):
        btnAddUser["state"] = "normal"
        btnChangeUser["state"] = "disabled"
        btnDelUser["state"] = "disabled"
        btnFindUser["state"] = "disabled"

    if (workMode.get() == "changeUser"):
        btnAddUser["state"] = "disabled"
        btnChangeUser["state"] = "normal"
        btnDelUser["state"] = "disabled"
        btnFindUser["state"] = "normal"

    if (workMode.get() == "delUser"):
        btnAddUser["state"] = "disabled"
        btnChangeUser["state"] = "disabled"
        btnDelUser["state"] = "normal"
        btnFindUser["state"] = "normal"


# добавление нового пользователя
def addNewUserData(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass, message=True):
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
        if (message):
            showinfo(title="Добавление пользователя", message="Пользователь успешно добавлен!")

        return True
    except Exception as e:
        if (message):
            showerror(title="Добавление пользователя",
                  message="Произошла непредвиденная ошибка при добавлении пользователя, попробуйте еще раз")
    except:
        if (message):
            showerror(title="Добавление пользователя", message="Произошла непредвиденная ошибка при добавлении пользователя, попробуйте еще раз")

    return False

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

def checkNewUserData(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass, message=True):
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
    if (message):   # не проверяем, если это изменение пользователя
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
        # сообщаем, что данные заполнены неверно
        return False
    else:
        addNewUserData(db, root, etrName, etrSurname, etrPatr, cbxRole, etrPhone, etrEmail, tbComm, etrLogin, etrPass, message)
        # сообщаем, что операция успешна
        return True


# загружает список логов из БД
def loadLogList():
    # запрос на получение данных о системе
    qr = '''SELECT system_log.id_log AS id,
                    system_log.action_caption AS caption,
                    system_log.action_type AS type,
                    system_log.action_status AS status,
                    system_log.description AS descr,
                    system_log.date_time AS date_time
                    FROM db.system_log
            '''

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)
        # фильтруем данные таблицы users для поиска соответствий введенным данным
        # filterData = df.query(f"login == '{login}' and pwd == '{pwd}' and role == '{role}'", inplace=False)

        # список логов
        # заголовки таблицы
        # cols = list(df.columns)
        # logList = df.to_dict()

    except Exception as e:
        showinfo(title="Загрузка логов",
                 message="При выгрузке логов из БД произошла непредвиденная ошибка! Проверьте БД и попробйте снова.")

# заполнение таблицы данными на форме управления системой из БД
def insertDataToTable(table, df):
    # загружаем список логов для построения таблицы
    df = loadLodList()

    # добавляем данные в таблицу из dataFrame
    for index, row in df.iterrows():
        # разбираем дату и время на отдельные составляющие
        tstr = row[-1].strftime("%Y-%m-%d %H:%M:%S")
        date = tstr.split()[0]
        time = tstr.split()[1][:-3]
        table.insert("", END, values=tuple([*row[:-1], date, time]))

# очистка всех логов в БД
def clearLogList(db, table):
    # запрос на удаление всех записей
    qr = f'''DELETE FROM system_log
                    WHERE system_log.id_log != 0;
                  '''
    ans = showwarning(title="Очистка логов", message="Вы действительно хотите удалить ВСЕ записи логов?")
    if ans:
        try:
            # создаем объект курсора для выбора нужной строки
            cur = db.cursor()
            # выполняем query-запрос
            cur.execute(qr)
            # сохраняем изменения в БД
            db.commit()
            showinfo(title="Очистка логов", message="Очистка логов прошла успешно!")

            # обновляем данные в таблице
            insertDataToTable(logList, df)

            return True
        except Exception as e:
            if (message):
                showerror(title="Удаление пользователя",
                          message="Произошла непредвиденная ошибка при удалении пользователя, попробуйте еще раз")

# удаление записи лога
def delRecord(db, selectRow):
    pass

# создание отчета по логам от до даты и времени
def createReport(db, etrDateFrom, dateUntil, timeFrom, timeUntil):
    pass