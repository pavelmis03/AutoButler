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

# функция получения рейсов в виде строки для нейронки
def getFlightAsStr(flyList):
    # строка с информацией из БД
    dataStr = ""
    # cols = ["№", "Номер рейса", "Авиакомпания", "Аэропорт вылета", "Аэропорт прибытия", "Плановое время вылета",
    #         "Плановое время прибытия", "Фактическое время вылета", "Фактическое время прибытия", "      Статус      ",
    #         "Минуты задержки", "Причина отмены"]
    i = 0
    # проходим по таблице, получаем данные
    for el in flyList.get_children(""):
        # получаем список значений по строке
        row = flyList.item(el)["values"]
        # собираем строку для нейронки
        dataStr += f"{i + 1}) рейс {row[1]} авиакомпании {row[2]}, вылет {row[5]} из {row[3]}, посадка в {row[4]}, статус рейса: {row[9]}\n"
        i += 1
    return dataStr

# получаем историю сообщений из tbOutput
def getMessagesHistory(tbOutput):
    # будущий массив сообщений
    messages = []
    # временный словарь
    tmp = {
        "role": "",
        "content": ""
    }
    # получаем весь текст
    text = tbOutput.get("1.0", "end")
    # разбиваем текст на массив по ключевым точкам, в которых были добавлены +++
    textarr = text.split("+++")
    # проходим текст по элементам
    for str in textarr:
        # короткие строки - мусор
        if (len(str) >= 9):
            # если нашли строку, где написана роль, добавляем ее
            if ("role" in str):
                # строка вида role: system
                tmp["role"] = str.split(": ")[1]
            else:
                # добавляем сщтеуте
                tmp["content"] = str
            # если все добавили во временный словарь, закидываем в массив сообщений
            if (tmp["content"] != ""):
                messages.append(tmp)
                tmp = { "role": "", "content": "" }

    return messages

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

# создаем подключение к модели
def getClient():
    # получаем ключи и создаем чат с нейронкой
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        # если не нашли ключ в переменных окружения, выбрасываем исключение
        if not api_key:
            showerror(title="Подключение к модели", message=f"API-ключ не найден в переменных окружения")
            raise ValueError("OPENROUTER_API_KEY не найден в переменных окружения")
        # возвращаем объект модели
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    except Exception as e:
        # отладочный
        print(e)
        showerror(title="Ошибка модели", message=f"Ошибка при создании клиента OpenAI: {e}")

# функция, в которой определяются настройки для нейронки
def updateSystemMessage(messages, tbOutput):
    messages[0] = {
        "role": "system",
        "content":
            "Ты специалист по прогнозированию отмены авиарейсов, помогающий менеджерам аэропорта определить количество"
            "пассажиров, которым потребуется номер в гостинице;\n"
            "Проводи анализ только тех данных, которые будут тебе предоставлены;\n"
            "Для расчета вероятности отмены используй данные из интернета;\n"
            "Запоминай свои выводы и сообщения менеджера аэропорта; всегда отвечай по-русски;\n"
            f"Используй данные по погоде в районе аэропортов для оценки вероятности отмены рейса;\n"
            f"Не бывает так, чтобы с большой вероятностью отменялось больше 30% рейсов.\n"
    }
    # выводим промпт
    tbOutput.insert(END, "+++role: system+++\n+++" + messages[0]["content"] + "+++\n\n")

# первый запрос для нейронки
def addStartPrompt(messages, analysisType, addMessage, tbOutput, flyList):
    # словарь соответствия кодов radioBtn и текста на них
    arr = {
        "FlightCansel": "Отмена рейса",
        "allFlightCansel": "Количество отменных рейсов за период",
        "passengerCount": "Количество пассажиров с рейса, которым потребуется гостиница",
        "allPassengerCount": "Количество пассажиров, которым потребуется гостиница за период",
    }
    analysisType = arr[analysisType]
    # получаем данные по рейсам в виде строки
    dataStr = getFlightAsStr(flyList)
    firstPrompt = {  # промпт
        "role": "system",
        "content": f"Начни анализ по { analysisType }.\n"
                   f"Вот данные, которые нужно проанализировать: \n" + dataStr
    }

    # если было передано доп сообщение
    if (len(addMessage) > 15):
        # добавляем дополнительную информацию для нейронки
        firstPrompt = {  # промпт
            "role": "system",
            "content": f"Начни анализ по { analysisType } с учетом следующих данных:\n"
                       f"{addMessage}\n"
                       f"Вот данные, которые нужно проанализировать: \n" + dataStr
        }
    # если сообщение есть, но слишком короткое
    elif (len(addMessage) > 5):
        showinfo(title="Дополнительное сообщение",
                 message=f"Дополнительное сообщение слишком короткое, оно не будет передано на анализ. (В дополнительном сообщении должно быть больше 15 символов)")

    messages.append(firstPrompt)
    # выводим запрос
    tbOutput.insert(END, "+++role: system+++\n+++" + firstPrompt["content"] + "+++\n\n")

# отправляем нейронке вопрос, получаем ответ
def chat(messages, model, client):
    try:
        # отправляем запрос к API OpenAI, чтобы сгенерировать ответ модели для данного чата
        return client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except Exception as e:
        # отладочный
        print(e)
        showerror(title="Анализ данных", message=f"Ошибка при запросе к API: {e}")

# получаем текст ответа модели
def addAssistantResponse(response, messages):
    try:
        # проверяем, чтоб был ответ от сервера, что в ответе были варианты ответа модели
        if ((not response) or (not response.choices) or (len(response.choices) == 0)):
            showerror(title="Анализ данных", message=f"Пустой ответ от API")
            raise ValueError("Пустой ответ от API")
        # получаем первый ответ
        assistant_text = response.choices[0].message.content
        # если ответ пустой
        if (not assistant_text):
            showerror(title="Анализ данных", message=f"Пустое содержимое сообщения")
            raise ValueError("Пустое содержимое сообщения")
        # добавляем в переписку ответ модели
        assistant_msg = {"role": "assistant", "content": assistant_text}
        messages.append(assistant_msg)
        return assistant_text
    except Exception as e:
        # отладочный
        print(e)
        showerror(title="Анализ данных", message=f"Ошибка при обработке ответа ассистента: {e}")

# функция общения с нейронкой
def communication(tbOutput, message):
    # получаем историю сообщений из tbOutput
    messages = getMessagesHistory(tbOutput)
    try:
        # загружаем переменные среды из .env
        load_dotenv()
        # устанавливаем соединение с нейронкой
        client = getClient()
        # получаем объект модели
        model = os.getenv("MODEL")
        # получаем ответ пользователя
        user_msg = {"role": "user", "content": message}
        # выводим запрос
        tbOutput.insert(END, f"\n\n+++role: user+++: +++{message}+++ \n\n")
        # добавляем ответ пользователя в переписку
        messages.append(user_msg)
        # получаем ответ от сервера модели по отправленным сообщениям теперь уже по ответу пользователя
        response = chat(messages, model, client)
        # получаем текст ответа модели
        assistant_text = addAssistantResponse(response, messages)
        # выводим запрос
        tbOutput.insert(END, f"\n\n+++role: assistant+++: +++{assistant_text}+++ \n\n")
        # вывод в текст бокс
        # обновляем настройки для нейронки
        # updateSystemMessage(messages)
    except Exception as e:
        # отладочный
        print(e)
        showerror(title="Анализ данных", message=f"Ошибка во анализа: {e}")

# первичные настройки для подготовки общения с нейронкой
def startCommunication(tbOutput, addMessage, flyList, components, analysisType):
    # получаем данные из полей ввода
    dateFrom, dateUntil, timeFrom, timeUntil = processComponents(components)
    # если есть ошибка в заполнении полей даты и времени
    if (checkDateTime(dateFrom, False, "Дата от") or
        checkDateTime(dateUntil, False, "Дата до") or
        checkDateTime(timeFrom, True, "Время от") or
        checkDateTime(timeUntil, True, "Время до")):
        showerror(title="Передача данных для анализа", message=f"Ошибка в заполнении полей даты и времени.\nИсправьте, чтобы начать анализ")
        return
    try:
        # загружаем переменные среды из .env
        load_dotenv()
        # устанавливаем соединение с нейронкой
        client = getClient()
        # получаем объект модели
        model = os.getenv("MODEL")
        # сообщения для нейронки
        messages = []
        messages.append({"role": "system"})
        # обновляем настройки для нейронки
        updateSystemMessage(messages, tbOutput)
        # первый запрос для нейронки
        addStartPrompt(messages, analysisType, addMessage, tbOutput, flyList)
        # получаем ответ от сервера модели по отправленным сообщениям
        response = chat(messages, model, client)
        # получаем текст ответа модели
        assistant_text = addAssistantResponse(response, messages)
        # выводим запрос
        tbOutput.insert(END, f"\n\n+++role: assistant+++: +++{assistant_text}+++ \n\n")

    except Exception as e:
        # отладочный
        print(e)
        showerror(title="Установка соединения", message=f"Ошибка при установке соединения с моделью или при ее настройке: {e}")

# получает список авиакомпаний из БД
def getCompany(db):
    # запрос на получение данных о системе
    qr = """SELECT flights.AIRLINE AS company
            FROM db.flights
         """

    # список авиакомпаний
    company = []

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)
        company = df["company"].tolist()
        # избавляемся от повторов с помощью множества
        company = set(company)
        # возвращаемся к списку
        company = list(company)

    except Exception as e:
        # отладочный
        print(e)
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
    qr = f"""SELECT flights.{destination} AS airport
            FROM db.flights
         """

    # список аэропортов
    airport = []

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)
        airport = df["airport"].tolist()
        # избавляемся от повторов с помощью множества
        airport = set(airport)
        # возвращаемся к списку
        airport = list(airport)

    except Exception as e:
        # отладочный
        print(e)
        showinfo(title="Получение авиакомпаний",
                 message="При выгрузке данных из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

    return airport

# создаем граф по опоздавшим, отмененным и вылетевшим рейсам
def createGraph(db, components, needSave, isHist=False):
    # загружаем список полетов для построения таблицы
    df = loadFlyList(db)

    # получаем значения по ссылкам на компоненты и меняем дату и время, если они имеют значения по умолчанию
    componentsVal = processComponents(components)
    # отфильтрованные значения
    # fData = filterData(df, componentsVal)
    # разбираю по переменным ссылки на объекты
    dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr = componentsVal

    # деления
    names = []
    # значения в этих делениях
    # вылетевшие вовремя
    valuesOnTime = []
    # с опозданием
    valuesDelay = []
    # отмененные
    valuesCansel = []

    # начало и конец рассматриваемого промежутка
    dtStart = datetime.strptime(dateFrom, "%Y-%m-%d")
    dtEnd = datetime.strptime(dateUntil, "%Y-%m-%d")
    # считаем, сколько дней в промежутке
    delta = dtEnd - dtStart
    daysStep = abs(round(delta.days / 30))

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
        componentsVal[7] = "Прибыл по расписанию"
        tData = filterData(df, componentsVal)
        # количество рейсов, прибывших вовремя
        valuesOnTime.append(len(tData))

        # настраиваем status рейсов
        componentsVal[7] = "Прибыл с задержкой"
        tData = filterData(df, componentsVal)
        # количество рейсов с задержкой
        valuesDelay.append(len(tData))

        # настраиваем status рейсов
        componentsVal[7] = "Отменен"
        tData = filterData(df, componentsVal)
        # количество отмененных рейсов
        valuesCansel.append(len(tData))
        # прибавляем по n дней за раз
        dtStart += timedelta(days=daysStep)

    try:
        # настройка шрифта
        plt.rcParams.update({"font.size": 10})
        # настраиваем размеры окна
        plt.figure(figsize=(10, 5))
        # настраиваем заголовок графика
        plt.title("Список полетов")
        # настраиваем заголовки осей
        plt.xlabel("Дата вылета")
        plt.ylabel("Количество рейсов")

        # метки на оси Х, которые будут подписаны, как даты
        x = np.arange(len(names))

        # если нужно сделать гистограмму
        if (isHist):
            plt.bar(x - 0.2, valuesDelay, width=0.2, label="С задержкой")
            plt.bar(x, valuesOnTime, width=0.2, label="Без опозданий")
            plt.bar(x + 0.2, valuesCansel, width=0.2, label="Отмененные")
        else:
            # если нужно сделать график
            plt.plot(x, valuesOnTime, color="green", label="Без опозданий")
            plt.plot(x, valuesDelay, color="yellow", label="С задержкой")
            plt.plot(x, valuesCansel, color="red", label="Отмененные")

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
                if (not os.path.exists("code/reports/flightsHistReport")):
                    # создаем папку для графиков
                    os.mkdir("code/reports/flightsHistReport")
                # в названии папки указываем дату
                os.mkdir(f"code/reports/flightsHistReport/report_{folderName}")
                # сохранение графика в виде изображения
                plt.savefig(f"code/reports/flightsHistReport/report_{folderName}/hist.jpg")
            else:
                if (not os.path.exists("code/reports/flightsGraphReport")):
                    # создаем папку для графиков
                    os.mkdir("code/reports/flightsGraphReport")
                # в названии папки указываем дату
                os.mkdir(f"code/reports/flightsGraphReport/report_{folderName}")
                plt.savefig(f"code/reports/flightsGraphReport/report_{folderName}/graph.jpg")
            showinfo(title="Соханение графика", message="График успешно сохранен!")
        # показываем график
        plt.show()
    except Exception as e:
        # отладочный
        print(e)
        showinfo(title="Соханение графика", message="Возникла неожиданная ошибка при создании графика!")

# функция сброса настроек формирования графика и отчета
def resetSettings(dateFrom, dateUntil, timeFrom, timeUntil, workModeDep, workModeArr, cbxArr):
    # сбрасываем настройки даты и времени
    dateFrom.delete(0, END)
    dateFrom.insert(0, "YYYY-MM-DD")
    dateUntil.delete(0, END)
    dateUntil.insert(0, "YYYY-MM-DD")
    timeFrom.delete(0, END)
    timeFrom.insert(0, "00:00")
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
    qr = """SELECT flights.ID AS id,
                flights.FLIGHT_NUMBER AS flyNum,
                flights.AIRLINE AS company,
                flights.DEP_AIRPORT AS airportDep,
                flights.ARR_AIRPORT AS airportArr,
                flights.SCHEDULED_DEP AS schDep,
                flights.SCHEDULED_ARR AS schArr,
                flights.ACTUAL_DEP AS actDep,
                flights.ACTUAL_ARR AS actArr,
                flights.STATUS AS status,
                flights.DELAY_MINUTES AS delay,
                flights.CANCELLATION_REASON AS reason
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

# заполнение таблицы данными на форме анализа рейсов из БД
def insertDataToTable(db, table, components, componentsCnt=10):
    # загружаем список полетов для построения таблицы
    df = loadFlyList(db)
    # отфильтрованный список данных
    fData = []

    # очищаем таблицу
    for item in table.get_children(""):
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
            table.insert("", END, values=tuple([*row]))
        # если ни одна строка не выбрана, назначаем выбранной первую строку
        if (len(table.selection()) == 0):
            table.selection_add(table.get_children("")[0])

# функция проверки рейса на опоздание по вылету и приземлению и на соответствие этого настройкам фильтрации
# параметры: настройка (все, опаздывает, по расписанию); плановое время; фактическое время
def checkDel(param, schTime, actTime):
    # если все варианты (и опоздавшие, и вовремя прилетевшие) - отрезаем начало
    if (param[:3] == "all"):
        return True

    # 2026-2-30 10:20:00
    schDt = str(schTime).split()[0]
    schTm = str(schTime).split()[1][:-3]

    actDt = str(actTime).split()[0]
    actTm = str(actTime).split()[1][:-3]

    # если опаздывает
    if ((actTm > schTm) or (actDt > schDt)):
        # отрезаем конец
        if (param[:-3] == "delay"):
            return True
    else: # если вовремя
        # отрезаем конец
        if (param[:-3] == "schedule"):
            return True

    return False

# функция для фильтрации данных по параметрам
def filterData(df, componentsVal):

    fData = []
    # на разные случаи
    if (len(componentsVal) == 10):
        # разбираю по переменным ссылки на объекты
        dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr = componentsVal
    else:
        dateFrom, dateUntil, timeFrom, timeUntil = componentsVal

    for index, row in df.iterrows():
        # 2026-2-30 10:20:00
        dt = str(row["schDep"]).split()[0]
        tm = str(row["schDep"]).split()[1][:-3]
        # заменяем буквы ё, если есть на е
        row["status"] = row["status"].replace("ё", "е")

        # обходим DF, берем только подходящие по дате и времени строки
        if (dt >= dateFrom) and (dt <= dateUntil):
            if ((tm + ":00") >= timeFrom) and ((tm + ":00") <= timeUntil):
                # если у нас окно для прогноза, то интересно только это
                if ((len(componentsVal) != 10) or
                    (# если акно анализа, проверяем компанию, статус, аэропорты
                        ((company == "Все компании") or (row["company"].lower() == company.lower())) and
                        ((status == "Все варианты") or (row["status"].lower() == status.lower())) and
                        ((airportDep == "Все аэропорты") or (row["airportDep"].lower() == airportDep.lower())) and
                        ((airportArr == "Все аэропорты") or (row["airportArr"].lower() == airportArr.lower()))
                    )
                ):
                        # проверяем, задерживается или по расписанию и соответствует ли это настройкам
                        if ((len(componentsVal) != 10) or (checkDel(depDel, row["schDep"], row["actDep"]) and checkDel(arrDel, row["schArr"], row["actArr"]))):
                            fData.append(row)

    return fData

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
        except Exception as e:
            # отладочный
            print(e)
            return f"Неправильный формат времени в поле \"{str}\". Запишите в виде: HH:MM, например 09:12"
        # else:
        #     return "Неправильный формат времени. Запишите в виде: HH:MM, например 09:12"
    else: # проверяем дату
        # if len(data.split("-")) == 3:
        try:
            datetime.strptime(data, "%Y-%m-%d")
            return ""
        except Exception as e:
            # отладочный
            print(e)
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
def createReport(db, components):
    # получаем значения по ссылкам на компоненты и меняем дату и время, если они имеют значения по умолчанию
    componentsVal = processComponents(components)

    # разбираю по переменным ссылки на объекты
    dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr = componentsVal

    # проверяем, что все данные верны, если нет, выходим из функции
    if (not checkDataReport(dateFrom, dateUntil, timeFrom, timeUntil)):
        return False

    # запрос на получение данных о полетах
    qr = """SELECT flights.ID AS id,
                flights.FLIGHT_NUMBER AS flyNum,
                flights.AIRLINE AS company,
                flights.DEP_AIRPORT AS airportDep,
                flights.ARR_AIRPORT AS airportArr,
                flights.SCHEDULED_DEP AS schDep,
                flights.SCHEDULED_ARR AS schArr,
                flights.ACTUAL_DEP AS actDep,
                flights.ACTUAL_ARR AS actArr,
                flights.STATUS AS status,
                flights.DELAY_MINUTES AS delay,
                flights.CANCELLATION_REASON AS reason
        FROM db.flights
        """

    # пробуем прочитать данные
    try:
        # чтение данных из БД с помощью query запроса
        df = pd.read_sql(qr, con=db)

        # собираем обратно
        # components = [dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr]
        fData = filterData(df, componentsVal)

        if (not os.path.exists("code/reports/flightsMainReport")):
            # создаем папку для отчетов
            os.mkdir("code/reports/flightsMainReport")

        # создаем папку с указанием текущей даты и времени
        folderName = datetime.now()
        folderName = folderName.strftime("%d") + "." + folderName.strftime("%m") + "." + folderName.strftime("%Y") + "_" + folderName.strftime("%H") + "-" + folderName.strftime("%M")
        # в названии папки указываем фамилию и дату
        os.mkdir(f"code/reports/flightsMainReport/report_{folderName}")

        # создаем документ
        doc = Document("code/reports/flightsMainReport.docx")

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
        table = doc.add_table(1, cols=12)
        header = table.rows[0].cells
        # задаем заголовки столбцов
        header[0].text = '№'
        header[1].text = 'Номер рейса'
        header[2].text = 'Компания'
        header[3].text = 'Аэропорт отправления'
        header[4].text = 'Аэропорт прибытия'
        header[5].text = 'Дата и время вылета по расписанию'
        header[6].text = 'Дата и время вылета фактические'
        header[7].text = 'Дата и время посадки по расписанию'
        header[8].text = 'Дата и время посадки фактические'
        header[9].text = 'Статус рейса'
        header[10].text = 'Задержка в минутах'
        header[11].text = 'Причина отмены рейса'

        # добавляем строки
        # заполняем словарь данными из БД
        # здесь row - строка вида [(column_caption, value), (..), ..]
        for row in fData:
            rowTable = table.add_row().cells
            rowTable[0].text = str(row.iloc[0])
            rowTable[1].text = str(row.iloc[1])
            rowTable[2].text = str(row.iloc[2])
            rowTable[3].text = str(row.iloc[3])
            rowTable[4].text = str(row.iloc[4])
            rowTable[5].text = str(row.iloc[5])
            rowTable[6].text = str(row.iloc[6])
            rowTable[7].text = str(row.iloc[7])
            rowTable[8].text = str(row.iloc[8])
            rowTable[9].text = str(row.iloc[9])
            rowTable[10].text = str(row.iloc[10])

        # сохраняем отчет в конкретную папку
        doc.save(f"code/reports/flightsMainReport/report_{folderName}/отчет_по_рейсам.docx")

        # загружаем шаблон отчета, в котором только что сделали таблицу, чтобы закинуть туда переменные
        doc = DocxTemplate(f"code/reports/flightsMainReport/report_{folderName}/отчет_по_рейсам.docx")
        # загружаем данные из контекста в шаблон
        doc.render(context)
        # сохраняем отчет в конкретную папку
        doc.save(f"code/reports/flightsMainReport/report_{folderName}/отчет_по_рейсам.docx")

        showinfo(title="Создание отчета", message="Отчет успешно сформирован!")

    except Exception as e:
        # отладочный
        print(e)
        showwarning(title="Создание отчета", message="При создании отчета произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

# поиск нужного рейса по названию
def findFlight(flyList, flyNum):
    # удаляем выделение со строк
    for k in flyList.selection():
        flyList.selection_remove(k)

    # проходим по таблице, ищем нужный рейс
    for k in flyList.get_children(""):
        # получаем строку по идентификатору
        arr = flyList.item(k)["values"]
        if (arr[1].lower() == flyNum.lower()):
            showinfo(title="Поиск рейса", message=f"Выбран рейс {flyNum}")
            # выделяем нужную строку
            flyList.selection_add(k)
            return
    showwarning(title="Поиск рейса", message="Указанный рейс не найден!")
