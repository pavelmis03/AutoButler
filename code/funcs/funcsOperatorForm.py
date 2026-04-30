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
# копирование текста в буфер обмена
import pyperclip

# дата и время
from datetime import datetime, timedelta
import time
# random
import random

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
import openai
# для работы с файлами окружения
from dotenv import load_dotenv

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

# получаем данные из выделенной строки в таблице (по умолчанию берем 1 элемент, если itemCnt = -1 - всю строку
def getTableItemData(table, itemNum, itemCnt=1):
    # если есть выделенные строки
    if (len(table.selection()) != 0):
        # получаем список выделенных строк, берем первую
        selected_item = table.selection()[0]
        # выделенный элемент
        item = table.item(selected_item)
        # список значений строки
        flyNum = item["values"]
    else:
        # по умолчанию берем первую строку и из нее нужный номер рейса
        flyNum = table.item(0)["values"]
        # выделяем первую строку
        table.selection_add(0)

    # если нужен конктретный элемент, иначе получаем всю строку
    if (itemCnt == 1):
        # получаем номер рейса
        flyNum = flyNum[itemNum]

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
            if (len(componentsVal) == 0) or ((tm + ":00") >= timeFrom) and ((tm + ":00") <= timeUntil):
                flag = True
                # пробегаемся по всем фильтрам
                for j in range(len(filter)):
                    # проверяем что пассажир с выбранного рейса и гостиницы соответствуют выбранной
                    if ((len(key) != 0) and not ((row[key[j]] == filter[j]) or (filter[j] == "Все гостиницы"))):
                        flag = False
                if (flag):
                    fData.append(row)

    return fData

# ищем рейс по компании или по номеру
def getFlight(db, filter, cbx):
    # загружаем список полетов для построения таблицы
    df = loadFlyList(db)
    filter = filter.upper()
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

# ищем отели в БД - получаем список отелей
def getHotel(db):
    # запрос на получение данных
    qr = """SELECT hotels_order.HOTEL AS hotel
                        FROM db.hotels_order
                     """

    # список гостиниц
    hotels = []

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)
        hotels = df["hotel"].tolist()
        # избавляемся от повторов с помощью множества
        hotels = set(hotels)
        # возвращаемся к списку
        hotels = list(hotels)

    except Exception as e:
        # отладочный
        print(e)
        showinfo(title="Получение гостиниц",
                 message="При выгрузке данных из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

    return hotels

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
        # for lbl, val in zip(components, ["ФИО: ", "Рейс№: ", "Класс рейса: "]):
        #    lbl["text"] = val
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

# вывести данные по выбранному номеру
def selectHotel(hotelList, labels):
    # получаем ссылки на лэйблы в виде отдельных переменных
    # название, удаленность, стоимость комнаты, питание, ссылка, дополнительно
    name, dist, cost, meals, link, addit = labels
    #
    # получаем константную часть надписи + данные по таблице
    name["text"] = name["text"].split()[0] + " " + getTableItemData(hotelList, 2)
    dist["text"] = dist["text"].split()[0] + " " + str(getTableItemData(hotelList, 3))
    cost["text"] = cost["text"].split()[0] + " " + str(getTableItemData(hotelList, 5))
    meals["text"] = meals["text"].split()[0] + " " + getTableItemData(hotelList, 6)
    tlink = getTableItemData(hotelList, 1)
    if (len(tlink) > 25):
        tlink = tlink[:25] + "..."
    link["text"] = link["text"].split()[0] + " " + tlink
    addit["text"] = addit["text"].split()[0] + " " + str(getTableItemData(hotelList, 4)) + " класс гостинницы"

# загружает список рейсов из БД
def loadFlyList(db):
    # запрос на получение данных о полетах
    qr = """SELECT flights.ID AS id,
                flights.FLIGHT_NUMBER AS flyNum,
                flights.AIRLINE AS company,
                flights.DEP_AIRPORT AS airportDep,
                flights.ARR_AIRPORT AS airportArr,
                flights.STATUS as status,
                flights.CANCELLATION_REASON AS reason,
                flights.FLIGHTS_TYPE AS type,
                flights.PASSENGERS_COUNT AS passCnt
        FROM db.flights
        """

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        return df

    except Exception as e:
        # отладочный
        print(e)
        showinfo(title="Загрузка рейсов", message="При выгрузке рейсов из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
        return pd.DataFrame()

# загружает список записей по отелям из БД
def loadOrdersList(db):
    # запрос на получение данных о проживании гостей
    qr = """SELECT hotels_order.NUM_ORDER AS reservNum,
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
        """

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        return df

    except Exception as e:
        # отладочный
        print(e)
        showinfo(title="Загрузка заявок", message="При выгрузке заявок из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
        return pd.DataFrame()

# загружает список пассажиров из БД
def loadPassengerList(db):
    # запрос на получение данных о полетах
    qr = """SELECT passengers.ID AS id,
                passengers.FLIGHT_NUMBER AS flyNum,
                passengers.FIRST_NAME AS name,
                passengers.LAST_NAME AS surname,
                passengers.BOOKING_REF AS ref,
                passengers.TICKET_NUMBER AS ticket,
                passengers.TICKET_PRICE AS price
        FROM db.passengers
        """

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        return df

    except Exception as e:
        # отладочный
        print(e)
        showinfo(title="Загрузка пассажиров", message="При выгрузке пассажиров из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
        return pd.DataFrame()

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

    # если не выбирали пассажира через поиск
    if (insertType != "choosePass"):
        # очищаем таблицу пассажиров
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
        if ((insertType != "chooseFlight") and (insertType != "choosePass")):
            # получаем номер рейса по таблице
            flyNum = getTableItemData(tableFlight, 1)
        elif (insertType == "chooseFlight"):
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
                # ищем в таблице рейс и выделяем его
                for k in tableFlight.get_children(""):
                    ind = tableFlight.item(k)
                    # если в этой строке нужный нам рейс
                    if (ind["values"][1].upper() == flyNum.upper()):
                        # выделяем его
                        tableFlight.selection_add(k)
                        showinfo(title="Поиск рейса", message=f"Выбран рейс {flyNum}")
        elif (insertType == "choosePass"):
            # получаем пассажира по комбо-боксу, формат данных: имя или фамилия
            passData = cbx.get()
            # если пассажиров не нашли, выводим предупреждение
            if (passData == "Пассажиров не найдено"):
                showerror(title="Ошибка!", message="Не найдено пассажиров по указанным параметрам!")
            else:
                # снимаем выделение с таблицы, чтобы не путать пользователя
                for select_item in tablePass.selection():
                    tablePass.selection_remove(select_item)

                # получаем именно фамилию
                passData = passData.split(" ")[1]
                # ищем в таблице пассажира и выделяем его
                for k in tablePass.get_children(""):
                    ind = tablePass.item(k)
                    # если в этой строке нужный нам человек (совпадает имя или фамилия)
                    if ((ind["values"][2] == passData) or (ind["values"][3] == passData)):
                        # выделяем его
                        tablePass.selection_add(k)
                        showinfo(title="Поиск пассжира", message=f"Выбран пассажир {passData}")

        # если не выбирали пассажира через поиск
        if (insertType != "choosePass"):
            # отфильтрованный список данных - фильтруем по заданному номеру рейса
            fDataPass = filterData(dfPass, ["flyNum"], [flyNum], [])

            i = 0
            # добавляем данные по пассажирам в таблицу
            for row in fDataPass:
                # разбираем дату и время на отдельные составляющие
                tablePass.insert("", END, i, values=tuple([*row]))
                i += 1

            # выделяем первую строку в таблице пассажиров
            tablePass.selection_add(0)



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

# закрепить гостиницу за человеком и отметить это в бд
def chooseHotel(db, hotelList, passList, flyList, guestCnt, usrName):
    # если не выбран номер
    if (len(hotelList.selection()) == 0):
        showerror(title="Ошибка!", message="Сначала выберите номер в таблице подобранных номеров!")
        return

    # текущие дата и время
    currDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # следующий день
    depDate = datetime.now() + timedelta(days=1)
    depDate = depDate.strftime("%Y-%m-%d %H:%M:%S")

    # получаем данные из таблиц для передачи в БД
    num = getTableItemData(hotelList, 0)
    pasN = getTableItemData(passList, 2)
    pasS = getTableItemData(passList, 3)
    pas = pasN + " " + pasS
    # guestCnt - параметр функции
    # usrName - параметр функции
    flyName = getTableItemData(passList, 1)
    hotel = getTableItemData(hotelList, 2)
    room = getTableItemData(hotelList, 7)
    passLink = getTableItemData(passList, 4)
    link = getTableItemData(hotelList, 1)
    tcost = str(getTableItemData(hotelList, 5)).split()
    cost = ""
    # превращаем сумму именно в число
    for el in tcost:
        if (el.isdigit()):
            cost += el
    nutr = getTableItemData(hotelList, 6)
    # формируем запрос к бд

    qr = f"""INSERT INTO db.hotels_order 
                    (NUM_ORDER, DATE_CREATE, PASSENGER, GUEST_COUNT, EXECUTANT, PROBLEM_FLIGHT_NAME, HOTEL, ROOM, ROOM_COST, CHECK_IN_DATE, CHECK_OUT_DATE, NUTRITION, PRIM, LINK) 
                    VALUES ({int(num)}, "{currDate}", "{pas}", {int(guestCnt)}, "{usrName}", "{flyName}", "{hotel}", "{room}", {int(cost)}, "{currDate}", "{depDate}", "{nutr}", "Нет", "{link}");
                    """
    ans = "None"
    # если ссылка уже закреплена
    if (passLink.startswith("https://")):
        # сообщение с подтверждением
        ans = askyesno(title="Подтвердите закрепление номера",
                       message=f"У этого пассажира уже есть закрепление, хотите его изменить?")
    if (ans):
        # сообщение с подтверждением
        ans = askyesno(title="Подтвердите закрепление номера", message=f"Закрепить за пассажиром '{pas}' номер '{room}' в отеле '{hotel}'?")
        if (ans):
            try:
                # создаем объект курсора для выбора нужной строки
                cur = db.cursor()
                # выполняем query-запрос
                cur.execute(qr)
                # сохраняем изменения в БД
                db.commit()

                # закрепляем ссылку за пассажиром
                try:
                    qr = f"""UPDATE db.passengers
                            SET BOOKING_REF = '{link}'
                            WHERE FIRST_NAME = '{pasN}' AND LAST_NAME = '{pasS}' AND FLIGHT_NUMBER = '{flyName}';
                            """
                    # создаем объект курсора для выбора нужной строки
                    cur = db.cursor()
                    # выполняем query-запрос
                    cur.execute(qr)
                    # сохраняем изменения в БД
                    db.commit()

                    showinfo(title="Закрепление номера", message="Номер успешно закреплен за пассажиром!")
                    # удаляем строку с закрепленным номером
                    hotelList.delete(hotelList.selection()[0])
                    # обновляем инфу по пассажиру
                    insertDataToTable(db, flyList, passList, "second")

                    # создаем заявку на бронирование
                    if (not os.path.exists("code/reports/hotelReserv")):
                        # создаем папку для отчетов
                        os.mkdir("code/reports/hotelReserv")

                    # создаем папку с указанием текущей даты и времени
                    folderName = datetime.now()
                    folderName = folderName.strftime("%d") + "." + folderName.strftime(
                        "%m") + "." + folderName.strftime("%Y") + "_" + folderName.strftime(
                        "%H") + "-" + folderName.strftime("%M")
                    # в названии папки указываем дату
                    os.mkdir(f"code/reports/hotelReserv/report_{folderName}")
                    # загружаем шаблон отчета
                    doc = DocxTemplate(f"code/reports/hotelReserv.docx")
                    # словарь подстановки данных в шаблон
                    context = {
                        "reservNum": str(random.randint(100, 10000)),
                        "dateReserv": currDate,
                        "room": room,
                        "hotel": hotel,
                        "dateArrival": currDate,
                        "dateDeparture": depDate,
                        "fullName": pas,
                        "ticketNumber": getTableItemData(passList, 5),
                        "flight": flyName,
                        "passengerCount": guestCnt,
                        "operator": usrName,
                    }
                    # загружаем данные из контекста в шаблон
                    doc.render(context)
                    # сохраняем отчет в конкретную папку
                    doc.save(f"code/reports/hotelReserv/report_{folderName}/Заявка_на_бронирование_номера.docx")
                    showinfo(title="Закрепление номера", message=f"Заявка на бронирование создана и лежит в папке\n\"reports/hotelReserv/report_{folderName}/Заявка_на_бронирование_номера.docx\"")
                except Exception as e:
                    # отладочный
                    print(e)
                    showerror(title="Обновление ссылки",
                              message="Произошла непредвиденная ошибка при закреплении, попробуйте еще раз")

            except Exception as e:
                # отладочный
                print(e)
                showerror(title="Закрепление номера", message="Произошла непредвиденная ошибка при закреплении, попробуйте еще раз")
        else:
            showinfo(title="Закрепление номера", message="Закрепление отменено")

# функция наполнения таблицы по данным, найденным нейронкой
def fillHotelList(hotelList, content):
    # очищаем таблицу перед наполнением
    for col in hotelList['columns']:
        hotelList.heading(col, text='')
    hotelList.delete(*hotelList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "     Ссылка     ", "   Название   ", "Удаленность", "Класс гостиницы", "Стоимость", "Питание", "  Номер  "]
    # строим таблицу по полученным данным
    hotelList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        hotelList.heading(col, text=col, anchor=CENTER,
                          # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
                          command=(lambda tree, i, f: (lambda: columnSort(tree, i, f)))(hotelList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        hotelList.column(f"#{i}", width=len(col) * 9, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # убираю лишние символы (8239 - пробелы nnbsp)
    arrDelSymb = [chr(8239), chr(8209), "—", "₽", "★", "  "]
    for el in arrDelSymb:
        content = content.replace(el, " ")

    # временный массив
    arr = content.split("\n")
    tarr = []
    # список отелей для таблицы
    hotels = []
    # считаем количество параметров
    i = 0

    for el in arr:
        # если новая запись (начинаются со ссылки всегда)
        if ("https" in el.strip()):
            # проверяем, что собрали данные по очередному отелю
            if (len(tarr) == 8):
                hotels.append(tarr)
            # отладочный
            print(tarr)
            # номер записи генерируем
            tarr = [random.randint(100, 10000)]
            # добавляем ссылку
            tarr.append(str(el).strip())
        else:
            # убираем пустые строки
            if (len(el) >= 1):
                tarr.append(str(el).strip())
                i += 1
    # последний отель
    # проверяем, что собрали данные по очередному отелю
    if (len(tarr) == 8):
        hotels.append(tarr)

    i = 0
    # добавляем данные по ответу нейронки в таблицу
    for row in hotels:
        # разбираем дату и время на отдельные составляющие
        hotelList.insert("", END, i, values=tuple([*row]))
        i += 1

# получить список гостиниц от нейронки
def getHotelList(table, familyMember, tbOutput, hotelList, message=""):
    # получаем список выделенных строк, берем первую
    selected_item = table.selection()[0]
    # получаем элементы выделенной строки в виде списка
    items = table.item(selected_item)["values"]
    # получаем отдельные значения
    #   0          1              2                    3                 4           5          6                  7             8
    # ["№", "Номер рейса", "Авиакомпания", "Аэропорт вылета", "Аэропорт прибытия", Статус, "Причина отмены", "Класс рейса", "Количество пассажиров"]
    company = items[2]
    airport = items[3]
    reason = items[6]
    type = items[7]
    passCnt = 1 + int(familyMember)

    try:
        # получаем переменные из окружения
        load_dotenv()
        # создаем объект клиента
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        # массив сообщений для нейронки
        messageData = [
            {   # промпт
                "role": "system",
                "content": """Ты специалист по подбору гостиничных номеров на одну ночь для людей с отмененного авиарейса.
                                            Ты должен прислать ответ в виде списка из 3-5 ссылок на конкретные номера в разных отелях или гостиницах 
                                            с краткой его характеристикой по трем параметрам, каждый параметр выводи обоязательно на отдельной строке без лишних символов и названия самого параметра:
                                            1) ссылка
                                            2) название гостиницы
                                            3) удаленность от аэропорта
                                            4) количество звезд гостиницы
                                            5) стоимость найденного номера в рублях
                                            6) входит ли в стоимость питание и какое
                                            7) какой это номер (класс номера и количество комнат)
                                            8) пустая строка-разделитель
                                             При выборе гостиницы и номера ты должен опираться на параметры, которые будут переданы в 
                                             последующих запросах - это аэропорт (гостиница должна быть недалеко от него), класс рейса
                                             (пассажиры из бизнес класса должны заселяться в элитные гостиницы), количество человек на номер: 
                                             больше 5 человек - номер должен быть трехкомнатный;
                                             Пиши на русском языке все, кроме оригинальных названий отелей;
                                             """
            },
        ]
        # сам наш запрос
        request = f"Подбери номер для { passCnt } человек с отмененного рейса класса { type }, рядом с аэропортом { airport }."
        # добавляем запрос пользователя
        messageData.append(
            {
                "role": "user",
                "content": request
            }
        )
        # если было передано доп сообщение
        if (len(message) > 15):
            messageData.append(
                {
                    "role": "user",
                    "content": message
                }
            )

        # создаем чат и настраиваем модель, потом задаем ей вопрос
        completion = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messageData
        )
        # выводим промпт
        tbOutput.insert(END, "role: system\n" + messageData[0]["content"] + "\n\n")
        # выводим запрос
        tbOutput.insert(END, "role: user\n" + request + "\n\n")
        if (len(message) > 15):
            # выводим сообщение
            tbOutput.insert(END, "role: user\n" + message + "\n\n")
        # выводим ответ нейронки в текстбокс
        tbOutput.insert(END, completion.choices[0].message.content + "\n----------------------\n")
        # обновляю вид текстбокса
        tbOutput.update()

        # отладочный
        # print(completion.choices[0].message.content)

        # функция наполнения таблицы по данным, найденным нейронкой
        fillHotelList(hotelList, completion.choices[0].message.content)

    # обрабатываем возможные исключения
    # except requests.exceptions.Timeout:
    except openai.APITimeoutError:
        showwarning(title="Внимание!", message="Время ожидания ответа истекло")
    except openai.APIConnectionError:
        showwarning(title="Внимание!", message="Произошла ошибка сети")
    except openai.InternalServerError:
        showwarning(title="Внимание!", message="Произошла ошибка на стороне сервера")
    except openai.RateLimitError:
        showwarning(title="Внимание!", message="Превышено количество запросов к модели")
    except Exception as e:
        # отладочный
        print(e)
        showwarning(title="Внимание!", message="Неизвестная ошибка при обработке запроса к модели")


# отправить сообщение
def addMessage(table, familyMember, tbOutput, hotelList, message=""):
    if (len(message) < 15):
        showwarning(title="Сообщение для модели", message="Введите сообщение не менее 15 символов!")
        return

    getHotelList(table, familyMember, tbOutput, hotelList, message)

# копирует в буфер обмена ссылку на отель
def copyHotelLink(hotelList):
    link = getTableItemData(hotelList, 1)
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

    if (not os.path.exists("code/reports/hotelsReport")):
        # создаем папку для отчетов
        os.mkdir("code/reports/hotelsReport")

    # создаем папку с указанием текущей даты и времени
    folderName = datetime.now()
    folderName = folderName.strftime("%d") + "." + folderName.strftime("%m") + "." + folderName.strftime("%Y") + "_" + folderName.strftime("%H") + "-" + folderName.strftime("%M")
    # в названии папки указываем дату
    os.mkdir(f"code/reports/hotelsReport/report_{folderName}")
    # создаем документ
    doc = Document("code/reports/hotelsReport.docx")

    dateFrom = dateFrom.split("-")
    dateUntil = dateUntil.split("-")
    # словарь подстановки данных в шаблон
    context = {
        "reportDate": folderName,
        "dateFrom": dateFrom[-1] + "." + dateFrom[-2] + "." + dateFrom[-3],
        "timeFrom": timeFrom,
        "dateUntil": dateUntil[-1] + "." + dateUntil[-2] + "." + dateUntil[-3],
        "timeUntil": timeUntil,
        "passengerCount": str(calcPass(fData)),
        "summaryCost": str(calcSummary(fData)),
        "operator": role,
    }

    # создаем таблицу
    table = doc.add_table(1, cols=10)
    header = table.rows[0].cells
    # задаем заголовки столбцов
    header[0].text = '№'
    header[1].text = 'Дата создания заявки'
    header[2].text = 'Рейс'
    header[3].text = 'Пассажир'
    header[4].text = 'Кол-во гостей'
    header[5].text = 'Гостиница'
    header[6].text = 'Номер'
    header[7].text = 'Дата заезда'
    header[8].text = 'Дата выезда'
    header[9].text = 'Расходы на размещение(руб)'

    # добавляем строки
    # заполняем словарь данными из БД
    # здесь row - строка вида [(column_caption, value), (..), ..]
    for row in fData:
        rowTable = table.add_row().cells
        rowTable[0].text = str(row.iloc[0])
        rowTable[1].text = str(row.iloc[1])
        rowTable[2].text = str(row.iloc[3])
        rowTable[3].text = str(row.iloc[4])
        rowTable[4].text = str(int(row.iloc[5]) + 1)
        rowTable[5].text = str(row.iloc[6])
        rowTable[6].text = str(row.iloc[7])
        rowTable[7].text = str(row.iloc[8])
        rowTable[8].text = str(row.iloc[9])
        rowTable[9].text = str(row.iloc[10])

    # сохраняем отчет в конкретную папку
    doc.save(f"code/reports/hotelsReport/report_{folderName}/отчет_по_размещенным_гостям.docx")

    # загружаем шаблон отчета
    doc = DocxTemplate(f"code/reports/hotelsReport/report_{folderName}/отчет_по_размещенным_гостям.docx")
    # загружаем данные из контекста в шаблон
    doc.render(context)
    # сохраняем отчет в конкретную папку
    doc.save(f"code/reports/hotelsReport/report_{folderName}/отчет_по_размещенным_гостям.docx")

    showinfo(title="Создание отчета", message="Отчет успешно сформирован!")

# создаем граф по опоздавшим, отмененным и вылетевшим рейсам
def createGraph(db, components, needSave, isHist=False):
    # загружаем список заявок для построения таблицы
    df = loadOrdersList(db)

    # получаем значения по ссылкам на компоненты и меняем дату и время, если они имеют значения по умолчанию
    componentsVal = processComponents(components, 2)
    # отфильтрованные значения
    # fData = filterData(df, componentsVal)
    # разбираю по переменным ссылки на объекты
    dateFrom, dateUntil, timeFrom, timeUntil, hotel = componentsVal

    # деления
    names = []
    # значения в этих делениях
    # заявки
    reserves = []
    # с опозданием
    # valuesDelay = []

    # начало и конец рассматриваемого промежутка
    # dtStart = datetime.strptime(dateFrom, "%Y-%m-%d")
    # dtEnd = datetime.strptime(dateUntil, "%Y-%m-%d")
    # считаем, сколько дней в промежутке
    # delta = dtEnd - dtStart
    # daysStep = abs(round(delta.days / 30))

    """
    while (dtStart < dtEnd):
        # добавляем дату - подпись метки на оси X
        names.append(str(dtStart).split()[0])

        # конец очередного временного промежутка
        dtTmpEnd = dtStart + timedelta(days=daysStep)

        # настраиваем дату от
        componentsVal[0] = str(dtStart).split()[0]
        # настраиваем дату до
        componentsVal[1] = str(dtTmpEnd).split()[0]
        # настраиваем status рейсов
        # componentsVal[7] = "Прибыл по расписанию"
        tData = filterData(df, [], [0], componentsVal)
        # количество рейсов, прибывших вовремя
        reserves.append(len(tData))

        # настраиваем status рейсов
        # componentsVal[7] = "Прибыл с задержкой"
        # tData = filterData(df, componentsVal)
        # количество рейсов с задержкой
        # valuesDelay.append(len(tData))

        # прибавляем по n дней за раз
        dtStart += timedelta(days=daysStep)
    """
    # получаем отфильтрованные данные
    tData = filterData(df, [], [0], componentsVal)
    for row in tData:
        s = row["hotel"]
        # если название слишком длинное, сокращаем его
        if (len(s) > 15):
            s = s[:16] + "..."
        # добавляем номер заявки - подпись метки на оси X
        names.append(s)
        reserves.append(row["roomCost"])

    try:
        # настройка шрифта
        plt.rcParams.update({"font.size": 10})
        # настраиваем размеры окна
        plt.figure(figsize=(10, 6))
        # настраиваем заголовок графика
        plt.title("Распределение цен по заявкам")
        # настраиваем заголовки осей
        plt.xlabel("ID заявки")
        plt.ylabel("Стоимость номера")

        # метки на оси Х, которые будут подписаны, как даты
        x = np.arange(len(names))

        # если нужно сделать гистограмму
        if (isHist):
            # plt.bar(x - 0.2, valuesDelay, width=0.2, label="С задержкой")
            plt.bar(x, reserves, width=0.4, label="Стоимость номера")
        else:
            # если нужно сделать график
            # plt.plot(x, valuesOnTime, color="green", label="Без опозданий")
            # plt.plot(x, valuesDelay, color="yellow", label="С задержкой")
            # plt.plot(x, valuesCansel, color="red", label="Отмененные")
            pass

        # Поворачиваем подписи осей
        plt.xticks(x, names, rotation=89)
        # устанавливаем легенду
        plt.legend(loc='best')
        plt.tight_layout()  # Автоматически регулирует размеры для избегания перекрытий

        # если надо сохранить
        if (needSave):
            # создаем папку с указанием текущей даты и времени
            folderName = datetime.now()
            folderName = folderName.strftime("%d") + "." + folderName.strftime("%m") + "." + folderName.strftime(
                "%Y") + "_" + folderName.strftime("%H") + "-" + folderName.strftime("%M")
            if (isHist):
                if (not os.path.exists("code/reports/reservesHistReport")):
                    # создаем папку для графиков
                    os.mkdir("code/reports/reservesHistReport")
                # в названии папки указываем дату
                os.mkdir(f"code/reports/reservesHistReport/report_{folderName}")
                # сохранение графика в виде изображения
                plt.savefig(f"code/reports/reservesHistReport/report_{folderName}/hist.jpg")
            else:
                if (not os.path.exists("code/reports/reservesGraphReport")):
                    # создаем папку для графиков
                    os.mkdir("code/reports/reservesGraphReport")
                # в названии папки указываем дату
                os.mkdir(f"code/reports/reservesGraphReport/report_{folderName}")
                plt.savefig(f"code/reports/reservesGraphReport/report_{folderName}/graph.jpg")
            showinfo(title="Соханение графика", message="График успешно сохранен!")
        # показываем график
        plt.show()
    except Exception as e:
        # отладочный
        print(e)
        showinfo(title="Соханение графика", message="Возникла неожиданная ошибка при создании графика!")