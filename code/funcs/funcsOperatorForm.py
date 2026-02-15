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
def filterData(df, key, filter):
    fData = []

    for index, row in df.iterrows():
        # проверяем что пассажир с выбранного рейса
        if (row[key] == filter):
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
            fDataFlight = filterData(dfFlight, "status", "Отменен")

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
        fDataPass = filterData(dfPass, "flyNum", flyNum)

        i = 0
        # добавляем данные по пассажирам в таблицу
        for row in fDataPass:
            # разбираем дату и время на отдельные составляющие
            tablePass.insert("", END, i, values=tuple([*row]))
            i += 1

# закрепить гостиницу за человеком
def chooseHotel():
    pass

# получить список гостиниц от нейронки
def getHotels():
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







