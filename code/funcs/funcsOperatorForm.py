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
# модули для работы с операционной системой
import os
import shutil
# копирование текста в буфер обмена
import pyperclip

# дата и время
from datetime import datetime, timedelta
import time

# библиотека для построения графика
import matplotlib.pyplot as plt
import pylab
# import cryptography

# библиотеки для создания отчетов
from docxtpl import DocxTemplate
import cryptography

# библиотека для работы с изображениями
from PIL import ImageTk, Image  # pip install pillow

# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts

# библиотеки AI
import requests
from openai import OpenAI
from dotenv import load_dotenv

# сортировка данных в таблице
def sortData(col, reverse, table):
    # получаем все значения столбцов в виде отдельного списка
    l = [(table.set(k, col), k) for k in table.get_children("")]
    # сортируем список
    l.sort(reverse=reverse)
    # переупорядочиваем значения в отсортированном порядке
    for index,  (_, k) in enumerate(l):
        table.move(k, "", index)
    # в следующий раз выполняем сортировку в обратном порядке
    table.heading(col, command=lambda: sortData(col, not reverse, table))

# получаем номер рейса по таблице
def getTableItemData(table, itemNum):
    # если есть выделенные строки
    if (len(table.selection()) != 0):
        # получаем список выделенных строк, берем первую
        selected_item = table.selection()[0]
        # выделенный элемент
        item = table.item(selected_item)
        # получаем номер рейса
        flyNum = item["values"][itemNum]
    else:
        # по умолчанию берем первую строку и из нее нужный номер рейса
        flyNum = table.item(0)["values"][itemNum]

    return flyNum

# функция для фильтрации данных
def filterData(df, key, filter, componentsVal):
    fData = []

    # не всегда передаются компоненты
    if (len(componentsVal) != 0):
        # разбираю по переменным ссылки на объекты
        dateFrom, dateUntil, timeFrom, timeUntil, hotel = componentsVal

    for index, row in df.iterrows():
        # не всегда передаются компоненты
        if (len(componentsVal) != 0):
            # 2026-2-30 10:20:00
            dt = str(row["dateArrival"]).split()[0]
            tm = str(row["dateArrival"]).split()[1][:-3]
        # обходим DF, берем только подходящие по дате и времени строки
        if (len(componentsVal) == 0) or (dt >= dateFrom) and (dt <= dateUntil):
            if (len(componentsVal) == 0) or (tm >= timeFrom) and (tm <= timeUntil):
                flag = True
                # пробегаемся по всем фильтрам
                for j in range(len(filter)):
                    # проверяем что пассажир с выбранного рейса и гостиницы соответствуют выбранной
                    if not ((row[key[j]] == filter[j]) or (filter[j] == "Все гостиницы")):
                        flag = False
                if (flag):
                    fData.append(row)

    return fData

# ищем рейс по компании или по номеру
def getFlight(db, filter, cbx):
    # загружаем список полетов для построения таблицы
    df = loadFlyList(db)
    # фильтруем данные таблицы пользователей по рейсу, или имени, или фамилии
    filterData = df.query(f"(company == '{filter}' or flyNum == '{filter}') and status == 'Отменен'", inplace=False)

    # если нашли таковых
    if (not filterData.empty):
        # получаем данные по фамилиям и именам в виде списков
        company = filterData["company"].tolist()
        flyNum = filterData["flyNum"].tolist()
        # склеиваем компанию и рейс и добавляем этот массив в комбо-бокс
        cbx["values"] = [c + " - " + f for c, f in zip(company, flyNum)][:]
    else:
        cbx["values"] = ["Рейсов не найдено"]

    # устанавливаем значение по умолчанию
    cbx.current(0)

# ищем отели - получаем список отелей
def getHotel(db):
    # запрос на получение данных
    qr = '''SELECT hotels_order.HOTEL AS hotel
                        FROM db.hotels_order
                     '''

    # список гостиниц
    hotels = []

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)
        hotels = df['hotel'].tolist()
        # избавляемся от повторов с помощью множества
        hotels = set(hotels)
        # возвращаемся к списку
        hotels = list(hotels)

    except Exception as e:
        showinfo(title="Получение гостиниц",
                 message="При выгрузке данных из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

    return hotels

# вывести данные по выбранному рейсу
def selectPass(cbx, tableFlight, tablePass, labels, type):
    # получаем ссылки на лэйблы в виде отдельных переменных
    fio, flight, fClass = labels
    # если вызвали функцию, когда кликнули на комбо-бокс
    if (type == "cbx"):
        fio["text"] = "ФИО: " + cbx.get()
    else:
        # если вызвали функцию, когда кликнули на строку таблицы
        # получаем данные по имени и фамилии пассажира и склеиваем
        fio["text"] = "ФИО: " + getTableItemData(tablePass, 2) + " " + getTableItemData(tablePass, 3)
    flight["text"] = "Рейс№: " + getTableItemData(tableFlight, 1)
    # класс рейса
    fClass["text"] = "Класс рейса: " + getTableItemData(tableFlight, 7)

# ищем пассажиров по фио или рейсу
def getPass(db, tableFlight, tablePass, filter, cbx, components):
    # загружаем список полетов для построения таблицы
    dfPass = loadPassengerList(db)
    # получаем номер рейса по таблице
    flyNum = getTableItemData(tableFlight, 1)
    # фильтруем данные таблицы пользователей по рейсу, или имени, или фамилии
    filterData = dfPass.query(f"(name == '{filter}' or surname == '{filter}') and flyNum == '{flyNum}'", inplace=False)

    # если нашли таковых
    if (not filterData.empty):
        # получаем данные по фамилиям и именам в виде списков
        surnames = filterData["surname"].tolist()
        names = filterData["name"].tolist()
        # склеиваем имя и фамилию и добавляем этот массив в комбо-бокс
        cbx["values"] = [s + " " + n for s, n in zip(surnames, names)][:]
        # устанавливаем значение по умолчанию
        cbx.current(0)
        # автоматически подставляем данные по пассажиру
        selectPass(cbx, tableFlight, tablePass, components, "cbx")
    else:
        cbx["values"] =  ["Пассажиров не найдено"]
        # очищаем данные лэйблов
        for lbl, val in zip(components, ["ФИО: ", "Рейс№: ", "Класс рейса: "]):
            lbl["text"] = val
    # устанавливаем значение по умолчанию
    cbx.current(0)

# вывести данные по выбранному пассажиру
def selectPass(cbx, tableFlight, tablePass, labels, type):
    # получаем ссылки на лэйблы в виде отдельных переменных
    fio, flight, fClass = labels
    # если вызвали функцию, когда кликнули на комбо-бокс
    if (type == "cbx"):
        fio["text"] = "ФИО: " + cbx.get()
    else:
        # если вызвали функцию, когда кликнули на строку таблицы
        # получаем данные по имени и фамилии пассажира и склеиваем
        fio["text"] = "ФИО: " + getTableItemData(tablePass, 2) + " " + getTableItemData(tablePass, 3)
    flight["text"] = "Рейс№: " + getTableItemData(tableFlight, 1)
    # класс рейса
    fClass["text"] = "Класс рейса: " + getTableItemData(tableFlight, 7)

# загружает список рейсов из БД
def loadFlyList(db):
    # запрос на получение данных о полетах
    qr = '''SELECT flights.ID AS id,
                flights.FLIGHT_NUMBER AS flyNum,
                flights.AIRLINE AS company,
                flights.DEP_AIRPORT AS airportDep,
                flights.ARR_AIRPORT AS airportArr,
                flights.STATUS as status,
                flights.CANCELLATION_REASON AS reason,
                flights.FLIGHTS_TYPE AS type,
                flights.PASSENGERS_COUNT AS passCnt
        FROM db.flights
        '''

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        return df

    except Exception as e:
        showinfo(title="Загрузка рейсов", message="При выгрузке рейсов из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
        return False

# загружает список записей по отелям из БД
def loadOrdersList(db):
    # запрос на получение данных о проживании гостей
    qr = '''SELECT hotels_order.NUM_ORDER AS reservNum,
                hotels_order.DATE_CREATE AS dateCreate,
                hotels_order.EXECUTANT AS operator,
                hotels_order.PROBLEM_FLIGHT_NAME as flyNum,
                hotels_order.PASSENGER AS pass,
                hotels_order.GUEST_COUNT AS guestCnt,
                hotels_order.HOTEL AS hotel,
                hotels_order.ROOM AS room,
                hotels_order.CHECK_IN_DATE AS dateArrival,
                hotels_order.CHECK_OUT_DATE AS dateDeparture,
                hotels_order.ROOM_COST AS roomCost
        FROM db.hotels_order
        '''

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        return df

    except Exception as e:
        showinfo(title="Загрузка заявок", message="При выгрузке заявок из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
        return False

# загружает список пассажиров из БД
def loadPassengerList(db):
    # запрос на получение данных о полетах
    qr = '''SELECT passengers.ID AS id,
                passengers.FLIGHT_NUMBER AS flyNum,
                passengers.FIRST_NAME AS name,
                passengers.LAST_NAME AS surname,
                passengers.BOOKING_REF AS ref,
                passengers.TICKET_NUMBER AS ticket,
                passengers.TICKET_PRICE AS price
        FROM db.passengers
        '''

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        return df

    except Exception as e:
        showinfo(title="Загрузка пассажиров", message="При выгрузке пассажиров из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
        return False

# заполнение таблицы данными на форме анализа рейсов из БД
def insertDataToTable(db, tableFlight, tablePass, insertType, cbx=""):
    # загружаем список полетов для построения таблицы
    dfFlight = loadFlyList(db)

    # загружаем список полетов для построения таблицы
    dfPass = loadPassengerList(db)

    # при повторной загрузке нужно загрузить только пассажиров
    if (insertType == "first"):
        # очищаем таблицу
        for item in tableFlight.get_children():
            tableFlight.delete(item)
    # очищаем таблицу
    for item in tablePass.get_children():
        tablePass.delete(item)

    # если не был прочитан фрейм, не делаем разбор его строк
    if (not dfFlight.empty):
        # при повторной загрузке нужно загрузить только пассажиров
        if (insertType == "first"):
            # отфильтрованный список данных
            fDataFlight = filterData(dfFlight, ["status"], ["Отменен"], [])

            i = 0
            # добавляем данные по рейсам в таблицу
            for row in fDataFlight:
                # разбираем дату и время на отдельные составляющие
                tableFlight.insert("", END, i, values=tuple([*row]))
                i += 1

        # если мы НЕ выбирали рейс через поиск
        if (insertType != "chooseFlight"):
            # получаем номер рейса по таблице
            flyNum = getTableItemData(tableFlight, 1)
        else:
            # получаем номер рейса по комбо-боксу, формат данных: "авиакомпания - рейс"
            flyNum = cbx.get()
            # если рейсов не нашли, выводим предупреждение и загружаем пассажиров по выделенной строке
            if (flyNum == "Рейсов не найдено"):
                showerror(title="Ошибка!", message="Не найдено рейсов по указанным параметрам!")
                showinfo(title="Внимание", message="Пассажиры будут отображены по последнему выбранному рейсу")
                flyNum = getTableItemData(tableFlight, 1)
            else:
                # снимаем выделение с таблицы, чтобы не путать пользователя
                for select_item in tableFlight.selection():
                    tableFlight.selection_remove(select_item)
                # получаем именно номер рейса
                flyNum = flyNum.split(" - ")[1]

        # отфильтрованный список данных - фильтруем по заданному номеру рейса
        fDataPass = filterData(dfPass, ["flyNum"], [flyNum], [])

        i = 0
        # добавляем данные по пассажирам в таблицу
        for row in fDataPass:
            # разбираем дату и время на отдельные составляющие
            tablePass.insert("", END, i, values=tuple([*row]))
            i += 1

# проверка и изменение данных даты и времени, если у них остались значения по умолчанию
def processComponents(components, startInd):
    componentsVal = components[startInd:]
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

# считаем общее количество пассажиров
def calcPass(df):
    res = 0
    for row in df:
        res += 1 + row["guestCnt"]
    return str(res)

# считаем общую сумму затрат
def calcSummary(df):
    res = 0

    for row in df:
        # Получаем количество дней
        days = abs(row["dateDeparture"] - row["dateArrival"])
        res += row["roomCost"] * max(days.days, 1)

    return str(res)

# заполнение таблицы данными на форме создания отчетов из БД
def insertDataHotelToTable(db, table, components, role):
    # загружаем список заявок для построения таблицы
    df = loadOrdersList(db)
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
        if (len(components) == 7):
            # получаем значения по ссылкам на компоненты и меняем дату и время, если они имеют значения по умолчанию
            componentsVal = processComponents(components, 2)
            # получаем данные по фильтру - отели и по оператору
            fData = filterData(df, ["hotel", "operator"], [componentsVal[4], role], componentsVal)
        else:
            for index, row in df.iterrows():
                fData.append(row)

        # добавляем данные в таблицу из fData
        for row in fData:
            # разбираем дату и время на отдельные составляющие
            table.insert("", END, values=tuple([*row]))

        # считаем общую сумму затрат и отображаем в лэйбле
        components[0]["text"] = calcSummary(fData)
        # считаем общее количество пассажиров и отображаем в лэйбле
        components[1]["text"] = calcPass(fData)

# закрепить гостиницу за человеком
def chooseHotel():
    pass

# получить список гостиниц от нейронки
def getHotelList(db):
    pass

# отправить сообщение
def addMessage():
    pass

# копирует в буфер обмена ссылку на отель
def copyHotelLink(link):
    # "Ссылка: https://..."
    link = link.lower()
    # получаем именно ссылку
    link = link.split()[1]
    # проверяем, что это действительно ссылка
    if (link.startswith("http")):
        pyperclip.copy(link)
        showinfo(title="Успешно!",
                 message="Ссылка на номер в гостинице успешно скопирована в буфер обмена!")
    else:
        showwarning(title="Внимание!", message="Сначала выберите номер, ссылку на который хотите скопировать!")

# проверяет правильность даты или времени, сохраненных в виде строки
def checkDateTime(data, isTime, str):
    # если проверяем время:
    if (isTime):
        # проверяем правильную длину и то, что формат соответствует
        # возвращаем ошибки
        # if len(data.split(':')) == 2:
        try:
            datetime.strptime(data, '%H:%M:%S')
            return ""
        except Exception:
            return f"Неправильный формат времени в поле \"{str}\". Запишите в виде: HH:MM, например 09:12"
        # else:
        #     return "Неправильный формат времени. Запишите в виде: HH:MM, например 09:12"
    else: # проверяем дату
        # if len(data.split('-')) == 3:
        try:
            datetime.strptime(data, '%Y-%m-%d')
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

# создание отчета по рейсам от и до даты и времени
def createReport(db, components, role):
    # получаем значения по ссылкам на компоненты и меняем дату и время, если они имеют значения по умолчанию
    componentsVal = processComponents(components, 2)

    # разбираю по переменным ссылки на объекты
    dateFrom, dateUntil, timeFrom, timeUntil, hotel = componentsVal

    # проверяем, что все данные верны, если нет, выходим из функции
    if (not checkDataReport(dateFrom, dateUntil, timeFrom, timeUntil)):
        return False

    # загружаем список заявок для построения таблицы
    df = loadOrdersList(db)

    # фильтруем данные
    fData = filterData(df, ["hotel", "operator"], [componentsVal[4], role], componentsVal)

    if (not os.path.exists("reports/hotelsReport")):
        # создаем папку для отчетов
        os.mkdir("reports/hotelsReport")

    # создаем папку с указанием текущей даты и времени
    folderName = datetime.now()
    folderName = folderName.strftime("%d") + "." + folderName.strftime("%m") + "." + folderName.strftime("%Y") + "_" + folderName.strftime("%H") + "-" + folderName.strftime("%M")
    # в названии папки указываем дату
    os.mkdir(f"reports/hotelsReport/report_{folderName}")
    # загружаем шаблон отчета
    doc = DocxTemplate("reports/hotelsReport.docx")

    dateFrom = dateFrom.split("-")
    dateUntil = dateUntil.split("-")
    # словарь подстановки данных в шаблон
    context = {
        "reportDate": folderName,
        "dateFrom": dateFrom[-1] + "." + dateFrom[-2] + "." + dateFrom[-3],
        "timeFrom": timeFrom,
        "dateUntil": dateUntil[-1] + "." + dateUntil[-2] + "." + dateUntil[-3],
        "timeUntil": timeUntil,
        "idRecord": "",
        "dateCreate": "",
        "flight": "",
        "passenger": "",
        "guestCount": "",
        "hotel": "",
        "room": "",
        "dateIn": "",
        "dateOut": "",
        "cost": "",
        "passengerCount": str(calcPass(fData)),
        "summaryCost": str(calcSummary(fData)),
        "operator": role,
    }

    # заполняем словарь данными из БД
    # здесь row - строка вида [(column_caption, value), (..), ..]
    for row in fData:
        context["idRecord"] += str(row[0]) + "\n\n"
        context["dateCreate"] += str(row[1]) + "\n"
        # row[2] - operator
        context["flight"] += row[3] + "\n\n"
        context["passenger"] += str(row[4]) + "\n"
        context["guestCount"] += str(row[5]) + "\n"
        context["hotel"] += str(row[6]) + "\n"
        context["room"] += row[7] + "\n"
        context["dateIn"] += str(row[8]) + "\n"
        context["dateOut"] += str(row[9]) + "\n"
        context["cost"] += str(row[10]) + "\n\n"

    # загружаем данные из контекста в шаблон
    doc.render(context)
    # сохраняем отчет в конкретную папку
    doc.save(f"reports/hotelsReport/report_{folderName}/отчет_по_размещенным_гостям.docx")
    showinfo(title="Создание отчета", message="Отчет успешно сформирован!")








