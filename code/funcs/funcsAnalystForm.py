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
from datetime import datetime

# библиотеки для создания отчетов
from docxtpl import DocxTemplate
import cryptography

# библиотека для работы с изображениями
from PIL import ImageTk, Image  # pip install pillow

# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts

# получает список авиакомпаний из БД
def getCompany(db):
    # запрос на получение данных о системе
    qr = '''SELECT flights.AIRLINE AS company
            FROM db.flights
         '''

    # список авиакомпаний
    company = []

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)
        company = df['company'].tolist()

    except Exception as e:
        showinfo(title="Получение авиакомпаний",
                 message="При выгрузке данных из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

    return company

# получает список аэропортов отправления и прибытия из БД
def getAirport(db, dest):
    # по умолчанию берем данные по аэропорту вылета
    destination = "DEP_AIRPORT"
    # если нужны данные по аэропортам посадки
    if (dest == "arr"):
        destination = "ARR_AIRPORT"

    # запрос на получение данных о системе
    qr = f'''SELECT flights.{destination} AS airport
            FROM db.flights
         '''

    # список аэропортов
    airport = []

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)
        airport = df['airport'].tolist()

    except Exception as e:
        showinfo(title="Получение авиакомпаний",
                 message="При выгрузке данных из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

    return airport

# функция изменения режима поиска данных по радио-кнопкам
def changeWorkMode(workMode):
    pass

# функция сброса настроек формирования графика и отчета
def resetSettings(dateFrom, dateUntil, timeFrom, timeUntil, workModeDep, workModeArr, cbxArr):
    # сбрасываем настройки даты и времени
    dateFrom.delete(0, END)
    dateFrom.insert(0, "YYYY-MM-DD")
    dateUntil.delete(0, END)
    dateUntil.insert(0, "YYYY-MM-DD")
    timeFrom.delete(0, END)
    timeFrom.insert(0, "00:01")
    timeUntil.delete(0, END)
    timeUntil.insert(0, "23:59")

    # сбрасываем настройки радио-кнопок
    # for i in range(len(radioBtnArr)) / 2:
    #     radioBtnArr[i]["variable"] = StringVar(value="allArr")
    workModeDep.set("allDep")
    workModeArr.set("allArr")

    # сбрасываем настройки комбобоксов
    for i in range(len(cbxArr)):
        cbxArr[i].current(0)


# загружает список рейсов из БД
def loadFlyList(db):
    # запрос на получение данных о полетах
    qr = '''SELECT flights.ID AS id,
                    flights.FLIGHT_NUMBER AS fly_num,
                    flights.AIRLINE AS company,
                    flights.DEP_AIRPORT AS dep_air,
                    flights.ARR_AIRPORT AS arr_air,
                    flights.SCHEDULED_DEP AS sch_dep,
                    flights.SCHEDULED_ARR AS sch_arr,
                    flights.ACTUAL_DEP AS act_dep,
                    flights.ACTUAL_ARR AS act_arr,
                    flights.STATUS AS status,
                    flights.DELAY_MINUTES AS delay,
                    flights.CANCELLATION_REASON AS reason
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

# заполнение таблицы данными на форме анализа рейсов из БД
def insertDataToTable(db, table):
    # загружаем список логов для построения таблицы
    df = loadFlyList(db)

    # очищаем таблицу
    for item in table.get_children():
        table.delete(item)

    # если не был прочитан фрейм, не делаем разбор его строк
    if (not df.empty):
        # добавляем данные в таблицу из dataFrame
        for index, row in df.iterrows():
            # разбираем дату и время на отдельные составляющие
            table.insert("", END, values=tuple([*row]))

# функция для фильтрации данных по параметрам
def filterData(dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr):
    filterData = []

    # обходим DF, берем только подходящие по дате и времени строки
    for index, row in df.iterrows():
        if (str(row["date"]) >= dateFrom) and (str(row["date"]) <= dateUntil):
            if (str(row["time"]).split()[-1] >= timeFrom) and (str(row["time"]).split()[-1] <= timeUntil):
                filterData.append(row)

    return filterData

# проверяет правильность даты или времени, сохраненных в виде строки
def checkDateTime(data, isTime, str):
    # если проверяем время:
    if (isTime):
        # проверяем правильную длину и то, что формат соответствует
        # возвращаем ошибки
        # if len(data.split(':')) == 2:
        try:
            datetime.datetime.strptime(data, '%Y.%m.%d')
            return ""
        except Exception:
            return f"Неправильный формат времени в поле \"{str}\". Запишите в виде: HH:MM, например 09:12"
        # else:
        #     return "Неправильный формат времени. Запишите в виде: HH:MM, например 09:12"
    else: # проверяем дату
        # if len(data.split('-')) == 3:
        try:
            datetime.datetime.strptime(data, '%Y-%m-%d')
            return ""
        except Exception:
            return f"Неправильный формат даты в поле \"{str}\". Запишите в виде: YYYY-MM-DD, например 2026-06-29"
        # else:
        #     return 2

# функция проверки правильности заполнения полей для генерации отчета
def checkDataReport(dateFrom, dateUntil, timeFrom, timeUntil):
    # список ошибок
    err = []

    # дату и время выставляем по умолчанию
    if ((dateFrom == "YYYY-MM-DD") or (dateFrom == "")):
        dateFrom = "1900-01-01"
    if ((dateUntil == "YYYY-MM-DD") or (dateUntil == "")):
        dateUntil = "2100-12-31"
    if (timeFrom == ""):
        timeFrom = "00:00"
    if (timeUntil == ""):
        timeUntil = "23:59"

    timeFrom += ":00"
    timeUntil += ":00"

    # проверяем поля даты и времени
    err.append(checkDateTime(dateFrom, False, "Дата от"))
    err.append(checkDateTime(dateUntil, False, "Дата до"))
    err.append(checkDateTime(timeFrom, True, "Время от"))
    err.append(checkDateTime(timeUntil, True, "Время до"))

    # если были обнаружены ошибки в заполнении формы
    if (len(err) != 0):
        # выводим не больше 5 ошибок
        for i in range(min(5, len(err))):
            # ошибки может и не быть
            if (err[i] != ""):
                showerror(title="Данные заполнены неверно!", message=err[i])
        # сообщаем, что данные заполнены неверно
        return False

    return True

# создание отчета по рейсам от и до даты и времени
def createReport(db, dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr):
    # проверяем, что все данные верны, если нет, выходим из функции
    if (not checkDataReport(dateFrom, dateUntil, timeFrom, timeUntil)):
        return False

        # запрос на получение данных о полетах
        qr = '''SELECT flights.ID AS id,
                        flights.FLIGHT_NUMBER AS fly_num,
                        flights.AIRLINE AS company,
                        flights.DEP_AIRPORT AS dep_air,
                        flights.ARR_AIRPORT AS arr_air,
                        flights.SCHEDULED_DEP AS sch_dep,
                        flights.SCHEDULED_ARR AS sch_arr,
                        flights.ACTUAL_DEP AS act_dep,
                        flights.ACTUAL_ARR AS act_arr,
                        flights.STATUS AS status,
                        flights.DELAY_MINUTES AS delay,
                        flights.CANCELLATION_REASON AS reason
                FROM db.flights
             '''

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        # сортируем df по дате и затем по времени
        # sorted_df = df.sort_values(by=["date", "time"])

        fData = filterData(dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr)

        # создаем отчеты по полученным из БД данным
        # если папка для отчетов уже есть, удаляем ее, чтобы создать новые отчеты
        if (os.path.exists("logReports")):
            shutil.rmtree("logReports")
            # os.rmdir("logReports")
        # создаем папку для отчетов
        os.mkdir("logReports")

        # создаем папку с указанием текущей даты и времени
        folderName = datetime.now()
        folderName = folderName.strftime("%d") + "." + folderName.strftime("%m") + "." + folderName.strftime("%Y") + "_" + folderName.strftime("%H") + "-" + folderName.strftime("%M")
        # в названии папки указываем фамилию и дату
        os.mkdir(f"logReports/report_{folderName}")
        # загружаем шаблон отчета
        doc = DocxTemplate("funcs/logReport.docx")

        dateFrom = dateFrom.split("-")
        dateUntil = dateUntil.split("-")
        # словарь подстановки данных в шаблон
        context = {
            "reportDate": folderName,
            "dateFrom": dateFrom[-1] + "." + dateFrom[-2] + "." + dateFrom[-3],
            "timeFrom": timeFrom,
            "dateUntil": dateUntil[-1] + "." + dateUntil[-2] + "." + dateUntil[-3],
            "timeUntil": timeUntil,
            "idLog": "",
            "logCaption": "",
            "logType": "",
            "logStatus": "",
            "logDescr": "",
            "logDate": "",
            "logTime": "",
        }

        # заполняем словарь данными из БД
        # здесь row - строка вида [(column_caption, value), (..), ..]
        for row in fData:
            context["idLog"] += str(row[0]) + "\n"
            context["logCaption"] += row[1] + "\n"
            context["logType"] += row[2] + "\n"
            context["logStatus"] += str(row[3]) + "\n"
            context["logDescr"] += row[4] + "\n"
            context["logDate"] += row[5].strftime("%d") + "." + row[5].strftime("%m") + "." + row[5].strftime("%Y") + "\n"
            context["logTime"] += str(row[6]).split()[-1] + "\n"

        # загружаем данные из контекста в шаблон
        doc.render(context)
        # сохраняем отчет в конкретную папку
        doc.save(f"logReports/report_{folderName}/отчет_по_логам.docx")
        showinfo(title="Создание отчета", message="Отчет успешно сформирован!")

    except Exception as e:
        showinfo(title="Создание отчета",
                 message="При создании отчета произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
