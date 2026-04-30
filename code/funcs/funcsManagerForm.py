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
from packaging import tags


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

# загружает список заявок из БД
def loadReqList(db):
    # запрос на получение данных о заявках
    qr = """SELECT hotels_order.NUM_ORDER AS id,
                hotels_order.DATE_CREATE AS dateCreate,
                hotels_order.PASSENGER AS pass,
                hotels_order.GUEST_COUNT AS guestCnt,
                hotels_order.PROBLEM_FLIGHT_NAME AS flight,
                hotels_order.EXECUTANT AS oper,
                hotels_order.HOTEL AS hotel,
                hotels_order.ROOM AS room,
                hotels_order.ROOM_COST AS cost,
                hotels_order.CHECK_IN_DATE AS dateIn,
                hotels_order.CHECK_OUT_DATE AS dateOut,
                hotels_order.LINK AS link,
                hotels_order.IS_APPROVE AS approved
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

# загружает список менеджеров из БД
def loadOperList(db):
    return pd.DataFrame()
    # запрос на получение данных о полетах
    # qr = """SELECT users.ID AS id,
    #             users.FLIGHT_NUMBER AS flyNum,
    #             users.FLIGHT_NUMBER AS flyNum,
    #             users.FLIGHT_NUMBER AS flyNum,
    #             users.FLIGHT_NUMBER AS flyNum,
    #             users.FLIGHT_NUMBER AS flyNum,
    #     FROM db.users
    #     """
    #
    # # пробуем прочитать данные
    # try:
    #     # чтение данных из БД с помощью query запроса
    #     df = pd.read_sql(qr, con=db)
    #
    #     return df
    #
    # except Exception as e:
    # # отладочный
    # print(e)
    #     showinfo(title="Загрузка рейсов", message="При выгрузке рейсов из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
    #     return pd.DataFrame()

# заполнение таблицы данными на форме подтверждения заявок из БД
def insertDataToTable(db, tableReq, tableOper):
    # загружаем список заявок для построения таблицы
    dfReq = loadReqList(db)

    # загружаем список менеджеров для построения таблицы
    dfOper = loadOperList(db)

    # очищаем таблицу заявок
    for item in tableReq.get_children():
        tableReq.delete(item)


    # очищаем таблицу операторов
    for item in tableOper.get_children():
        tablePass.delete(item)

    # если не был прочитан фрейм, не делаем разбор его строк
    if (not dfReq.empty):

        # отфильтрованный список данных
        fDataReq = filterData(dfReq, [], [], [])

        i = 0
        # добавляем данные по рейсам в таблицу
        for row in fDataReq:
            # проверяем, принята заявка или нет
            checked = "unchecked"
            if (row[-1]):
                checked = "checked"
            # разбираем дату и время на отдельные составляющие
            tableReq.insert("", END, i, values=tuple([*row[0:-1]]), tags=checked)
            i += 1

    # если не был прочитан фрейм, не делаем разбор его строк
    if (not dfOper.empty):
        # отфильтрованный список данных
        fDataOper = filterData(dfOper, [], [], [])

        i = 0
        # добавляем данные по операторам в таблицу
        for row in fDataOper:
            # разбираем дату и время на отдельные составляющие
            tableOper.insert("", END, i, values=tuple([*row]))
            i += 1

        # выделяем первую строку в таблице пассажиров
        tableOper.selection_add(0)

# функция изменения статуса заявки (принята/непринята)
def toggleCheck(table, event):
    # получаем список выделенных строк, берем первую
    rowid = table.selection()[0]
    # выделенный элемент
    tag = table.item(rowid, "tags")[0]
    tags = list(table.item(rowid, "tags"))
    tags.remove(tag)
    table.item(rowid, tags=tags)
    if (tag == "checked"):
        table.item(rowid, tags="unchecked")
    else:
        table.item(rowid, tags="checked")













