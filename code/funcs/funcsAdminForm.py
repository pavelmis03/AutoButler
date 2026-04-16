# библиотека графических элементов для
from tkinter import *
# дополнительные виджеты
from tkinter import ttk
# шрифты
from tkinter import font
# сообщения
from tkinter.messagebox import showerror, showwarning, showinfo, askyesno, askokcancel, askretrycancel
# бибиблиотека для работы с ini файлами
import configparser

# библиотека для sql-запросов
import pymysql as sql
import pandas as pd
import numpy as np
# модули для работы с операционной системой
import os
import shutil
from datetime import datetime, timedelta

# библиотека для построения графика
import matplotlib.pyplot as plt
import pylab
# import cryptography

# библиотеки для создания отчетов
from docxtpl import DocxTemplate
from docx import Document, table
import cryptography

# библиотека для работы с изображениями
from PIL import ImageTk, Image  # pip install pillow

# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts

# библиотеки AI
# библиотека обмена запросами
import requests
# для работы с нейронкой
from openai import OpenAI
# для работы с файлами окружения
from dotenv import load_dotenv

# проверка и изменение данных даты и времени, если у них остались значения по умолчанию
def processComponents(components):
    componentsVal = components[:]
    # получаем данные по компонентам
    for i in range(len(componentsVal)):
        componentsVal[i] = componentsVal[i].get()

    # дату и время выставляем по умолчанию
    if ((componentsVal[0] == "YYYY-MM-DD") or (componentsVal[0] == "")):
        componentsVal[0] = "2025-01-01"
    if ((componentsVal[1] == "YYYY-MM-DD") or (componentsVal[1] == "")):
        componentsVal[1] = "2026-12-31"
    if (componentsVal[2] == ""):
        componentsVal[2] = "00:00"
    if (componentsVal[3] == ""):
        componentsVal[3] = "23:59"
    # прибавляю секунды ко времени
    componentsVal[2] += ":00"
    componentsVal[3] += ":00"
    return componentsVal

# функция для фильтрации данных по параметрам
def filterData(df, componentsVal):

    fData = []
    # разбираю по переменным ссылки на объекты
    dateFrom, dateUntil, timeFrom, timeUntil, actType, status = componentsVal

    for index, row in df.iterrows():
        # 2026-2-30 10:20:00
        dt = str(row["date"])
        tm = str(row["time"]).split()[2]
        # обходим DF, берем только подходящие по дате и времени строки
        if (dt >= dateFrom) and (dt <= dateUntil):
            if ((tm + ":00") >= timeFrom) and ((tm + ":00") <= timeUntil):
                # проверяем тип действия
                if ((actType == "Не указан") or (actType == row["type"])):
                    # проверяем статус
                    if ((status == "Не указан") or (status == row["status"])):
                        fData.append(row)

    return fData

# сортировка по нажатию на столбец
def columnSort(tree, col, reverse):
    # получаем все значения столбцов в виде отдельного списка
    l = [(tree.set(k, col), k) for k in tree.get_children("")]
    # сортируем список
    l.sort(reverse=reverse)
    # переупорядочиваем значения в отсортированном порядке
    for index,  (_, k) in enumerate(l):
        tree.move(k, "", index)
    # в следующий раз выполняем сортировку в обратном порядке
    tree.heading(col, command=lambda: columnSort(tree, col, not reverse))

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
        qr = f"""DELETE FROM users
                WHERE user_name = "{name}" AND user_surname = "{surname}" AND user_login = "{login}";
              """
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
    qr = """SELECT
                users.user_role AS role, 
                users.user_login AS login,
                users.user_email AS email,
                users.user_phone AS phone,
                users.user_name AS name,
                users.user_surname AS surname,
                users.user_patronymic AS patr
                FROM db.users
        """
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
    qr = f"""INSERT INTO db.users 
            (user_name, user_surname, user_patronymic, user_description, user_email, user_phone, user_login, user_pass, user_role) 
            VALUES ("{ etrName }", "{ etrSurname }", "{ etrPatr }", "{ tbComm }", "{ etrEmail }", "{ etrPhone }", "{ etrLogin }", "{ etrPass }", "{ cbxRole }");
            """
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
        err.append("Заполните поле \"Телефон\"")
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
        err.append("Заполните поле \"Почта\"")
    else: # нет смысла в остальных проверках, если поле не заполнено
        # проверка на наличие собачки
        if (not "@" in etrEmail):
            err.append("Не обнаружен значок \"@\"")
        # проверка на наличие точки
        if (not "." in etrEmail):
            err.append("Не обнаружен значок \".\"")
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
    qr = """SELECT users.user_login AS login
                FROM db.users
        """
    # чтение данных из БД с помощью query запроса
    df = pd.read_sql(qr, con=db)
    # фильтруем данные таблицы users для поиска соответствий введенным данным
    filterData = df.query(f"login == '{etrLogin}'", inplace=False)

    # список ошибок
    err = []
    # проверяем, что поле заполнено
    if ((etrLogin == "") or (etrLogin == "Введите логин")):
        err.append("Заполните поле \"Логин\"")
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
        err.append("Заполните поле \"Имя\"")
    if ((etrSurname == "") or (etrSurname == "Введите фамилию")):
        err.append("Заполните поле \"Фамилия\"")
    if ((etrPatr == "") or (etrPatr == "Введите отчество")):
        err.append("Заполните поле \"Отчество\"")
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
        err.append("Заполните поле \"Пароль\"")

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
def loadLogList(db):
    # запрос на получение данных о системе
    qr = """SELECT system_log.id_log AS id,
                    system_log.action_caption AS caption,
                    system_log.action_type AS type,
                    system_log.action_status AS status,
                    system_log.description AS descr,
                    system_log.action_date AS date,
                    system_log.action_time AS time
                    FROM db.system_log
            """

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

        return df

    except Exception as e:
        showinfo(title="Загрузка логов",
                 message="При выгрузке логов из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

        return False

# заполнение таблицы данными на форме управления системой из БД
def insertDataToTable(db, table, components, componentsCnt=6):
    # загружаем список логов для построения таблицы
    df = loadLogList(db)
    # отфильтрованный список данных
    fData = []

    # очищаем таблицу
    for item in table.get_children():
        table.delete(item)

    # если не был прочитан фрейм, не делаем разбор его строк
    if (not df.empty):

        # если это не первый запрос, когда нам нужны все данные,
        # а запрос при изменении какого-либо параметра,
        # фильтруем данные, которые попадут в таблицу
        if (len(components) == componentsCnt):
            # получаем значения по ссылкам на компоненты и меняем дату и время, если они имеют значения по умолчанию
            componentsVal = processComponents(components)
            fData = filterData(df, componentsVal)
        else:
            for index, row in df.iterrows():
                fData.append(row)

        # добавляем данные в таблицу из fData
        for row in fData:
            # разбираем дату и время на отдельные составляющие
            table.insert("", END, values=tuple([*row[:-1], str(row[-1]).split()[2]]))

# очистка всех логов в БД
def clearLogList(db, table):
    # запрос на удаление всех записей
    qr = f"""DELETE FROM system_log"""
    ans = askyesno(title="Очистка логов", message="Вы действительно хотите удалить ВСЕ записи логов?")
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
            insertDataToTable(db, table, [])

            return True
        except Exception as e:
            showerror(title="Удаление пользователя",
                          message="Произошла непредвиденная ошибка при очистке логов, попробуйте еще раз")

# удаление записи лога
def delRecord(db, table, components):
    # получаем список выделенных строк - берем первую из них
    selectRow = table.selection()
    # если ничего не выделено
    if (len(selectRow) == 0):
        showinfo(title="Удаление записи лога", message="Выберите запись для удаления!")
        return
    # получаем список элементов выделенной строки
    item = table.item(selectRow[0])
    # значения полей строки в виде массива
    vals = item["values"]
    # id записи лога
    id_log = vals[0]

    # запрос на удаление всех записей
    qr = f"""DELETE FROM system_log
                        WHERE system_log.id_log = { id_log };
                      """
    try:
        # создаем объект курсора для выбора нужной строки
        cur = db.cursor()
        # выполняем query-запрос
        cur.execute(qr)
        # сохраняем изменения в БД
        db.commit()
        showinfo(title="Удаление записи лога", message="Удаление записи лога прошло успешно!")

        # обновляем данные в таблице
        insertDataToTable(db, table, components)

        return True
    except Exception as e:
        showerror(title="Удаление записи лога",
                      message="Произошла непредвиденная ошибка при удалении записи лога, попробуйте еще раз")

# проверяет правильность даты или времени, сохраненных в виде строки
def checkDateTime(data, isTime, str):
    # если проверяем время:
    if (isTime):
        # проверяем правильную длину и то, что формат соответствует
        # возвращаем ошибки
        # if len(data.split(":")) == 2:
        try:
            datetime.strptime(data, "%H:%M:%S")
            return ""
        except Exception:
            return f"Неправильный формат времени в поле \"{str}\". Запишите в виде: HH:MM, например 09:12"
        # else:
        #     return "Неправильный формат времени. Запишите в виде: HH:MM, например 09:12"
    else: # проверяем дату
        # if len(data.split("-")) == 3:
        try:
            datetime.strptime(data, "%Y-%m-%d")
            return ""
        except Exception:
            return f"Неправильный формат даты в поле \"{str}\". Запишите в виде: YYYY-MM-DD, например 2026-06-29"
        # else:
        #     return 2

# функция проверки правильности заполнения полей для генерации отчета
def checkDataReport(dateFrom, dateUntil, timeFrom, timeUntil):
    # список ошибок
    err = []

    # проверяем поля даты и времени
    err.append(checkDateTime(dateFrom, False, "Дата от"))
    err.append(checkDateTime(dateUntil, False, "Дата до"))
    err.append(checkDateTime(timeFrom, True, "Время от"))
    err.append(checkDateTime(timeUntil, True, "Время до"))

    flag = True
    # если были обнаружены ошибки в заполнении формы
    if (len(err) != 0):
        # выводим не больше 5 ошибок
        for i in range(min(5, len(err))):
            # ошибки может и не быть
            if (err[i] != ""):
                showerror(title="Данные заполнены неверно!", message=err[i])
                # сообщаем, что данные заполнены неверно
                flag = False

    return flag

# создание отчета по логам от и до даты и времени
def createReport(db, dateFrom, dateUntil, timeFrom, timeUntil):
    # дату и время выставляем по умолчанию
    if ((dateFrom == "YYYY-MM-DD") or (dateFrom == "")):
        dateFrom = "2025-01-01"
    if ((dateUntil == "YYYY-MM-DD") or (dateUntil == "")):
        dateUntil = "2026-12-31"
    if (timeFrom == ""):
        timeFrom = "00:00"
    if (timeUntil == ""):
        timeUntil = "23:59"

    timeFrom += ":00"
    timeUntil += ":00"

    # проверяем, что все данные верны, если нет, выходим из функции
    if (not checkDataReport(dateFrom, dateUntil, timeFrom, timeUntil)):
        return False

    # запрос на получение данных о системе
    qr = """SELECT system_log.id_log AS id,
                system_log.action_caption AS caption,
                system_log.action_type AS type,
                system_log.action_status AS status,
                system_log.description AS descr,
                system_log.action_date AS date,
                system_log.action_time AS time
                FROM db.system_log
        """

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        # сортируем df по дате и затем по времени
        # sorted_df = df.sort_values(by=["date", "time"])

        filterData = []
        # обходим DF, берем только подходящие по дате и времени строки
        for index, row in df.iterrows():
            if (str(row["date"]) >= dateFrom) and (str(row["date"]) <= dateUntil):
                if (str(row["time"]).split()[-1] >= timeFrom) and (str(row["time"]).split()[-1] <= timeUntil):
                    filterData.append(row)

        if (not os.path.exists("code/reports/logReports")):
            # создаем папку для отчетов
            os.mkdir("code/reports/logReports")

        # создаем папку с указанием текущей даты и времени
        folderName = datetime.now()
        folderName = (folderName.strftime("%d") + "." + folderName.strftime("%m") + "." + folderName.strftime("%Y") + "_" +
                      folderName.strftime("%H") + "-" + folderName.strftime("%M"))
        # в названии папки указываем фамилию и дату
        os.mkdir(f"code/reports/logReports/report_{folderName}")
        # создаем документ
        doc = Document("code/reports/logReport.docx")

        dateFrom = dateFrom.split("-")
        dateUntil = dateUntil.split("-")
        # словарь подстановки данных в шаблон
        context = {
            "reportDate": folderName,
            "dateFrom": dateFrom[-1] + "." + dateFrom[-2] + "." + dateFrom[-3],
            "timeFrom": timeFrom,
            "dateUntil": dateUntil[-1] + "." + dateUntil[-2] + "." + dateUntil[-3],
            "timeUntil": timeUntil,
        }

        # создаем таблицу
        table = doc.add_table(1, cols=7)
        header = table.rows[0].cells
        # задаем заголовки столбцов
        header[0].text = '№'
        header[1].text = 'Название'
        header[2].text = 'Тип'
        header[3].text = 'Статус'
        header[4].text = 'Описание'
        header[5].text = 'Дата'
        header[6].text = 'Время'

        # добавляем строки
        # заполняем словарь данными из БД
        # здесь row - строка вида [(column_caption, value), (..), ..]
        for row in filterData:
            rowTable = table.add_row().cells
            rowTable[0].text = str(row.iloc[0])
            rowTable[1].text = str(row.iloc[1])
            rowTable[2].text = str(row.iloc[2])
            rowTable[3].text = str(row.iloc[3])
            rowTable[4].text = str(row.iloc[4])
            rowTable[5].text = row.iloc[5].strftime("%d") + "." + row.iloc[5].strftime("%m") + "." + row.iloc[5].strftime("%Y")
            rowTable[6].text = str(row.iloc[6]).split()[-1]

        # сохраняем отчет в конкретную папку
        doc.save(f"code/reports/logReports/report_{folderName}/отчет_по_логам.docx")

        # загружаем шаблон отчета, в котором только что сделали таблицу, чтобы закинуть туда переменные
        doc = DocxTemplate(f"code/reports/logReports/report_{folderName}/отчет_по_логам.docx")
        # загружаем данные из контекста в шаблон
        doc.render(context)
        # сохраняем отчет в конкретную папку
        doc.save(f"code/reports/logReports/report_{folderName}/отчет_по_логам.docx")

        showinfo(title="Создание отчета", message="Отчет успешно сформирован!")

    except Exception as e:
        showinfo(title="Создание отчета",
                 message="При создании отчета произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

btnCreateHist