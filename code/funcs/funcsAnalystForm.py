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
from datetime import datetime, timedelta

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
# библиотека обмена запросами
import requests
# для работы с нейронкой
from openai import OpenAI
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

# создаем подключение к модели
def getClient():
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY не найден в переменных окружения")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    except Exception as e:
        print(f"Ошибка при создании клиента OpenAI: {e}")
        raise

# функция, в которой определяются настройки для нейронки
def updateSystemMessage(messages):
    messages[0] = {
        "role": "system",
        "content": (
            "Ты Мастер Ролевой Игры (GM) для сольного приключения в стиле DnD для одного игрока; "
            "Возраст игрока: 12-14 лет, поэтому следи за цензурой и возрастными ограничениями; "
            "Современный мир; "
            "Жанр игры: не хоррор, не мистика, не ужасы; "
            "Веди историю кинематографично, кратко и ярко; предлагай игроку 2–4 выбора с нумерацией; "
            "Запоминай факты и последствия; соблюдай логику мира; всегда отвечай по-русски; "
            "Мастер игры должен быть коротким и кратким, не более 3-4 предложений; "
            f"Следи за количеством сообщений. До конца игры осталось сообщений; "
            f"Используй местоположение игрока для описания окружающей среды: ; "
            f"Используй погоду для описания окружающей среды: . "
        ),
    }

# первый запрос для нейронки
def addStartPrompt(messages):
    first_message = {
        "role": "user",
        "content": "Начни игру: короткое вступление и 2–4 варианта действий для игрока.",
    }
    messages.append(first_message)

# отправляем нейронке вопрос, получаем ответ
def chat(messages, model, client):
    try:
        # отправляем запрос к API OpenAI, чтобы сгенерировать ответ модели для данного чата
        return client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except Exception as e:
        showerror(title="Анализ чего-то", message=f"Ошибка при запросе к API: {e}")
        raise

# получаем ответ от пользователя
def addUserMessage(messages):
    user_input = input("Вы: ")
    user_msg = {"role": "user", "content": user_input}
    # добавляем ответ пользователя в переписку
    messages.append(user_msg)

# получаем текст ответа модели
def addAssistantResponse(response, messages):
    try:
        # проверяем, чтоб был ответ от сервера, что в ответе были варианты ответа модели
        if ((not response) or (not response.choices) or (len(response.choices) == 0)):
            raise ValueError("Пустой ответ от API")
        # получаем первый ответ
        assistant_text = response.choices[0].message.content
        # если ответ пустой
        if (not assistant_text):
            raise ValueError("Пустое содержимое сообщения")
        # добавляем в переписку ответ модели
        assistant_msg = {"role": "assistant", "content": assistant_text}
        messages.append(assistant_msg)
        return assistant_text
    except Exception as e:
        showerror(title="Анализ чего-то", message=f"Ошибка при обработке ответа ассистента: {e}")
        raise

# функция общения с нейронкой
def communication():
    try:
        # получаем ответ пользователя
        addUserMessage(messages)
        # получаем ответ от сервера модели по отправленным сообщениям теперь уже по ответу пользователя
        response = chat(messages, model, client)
        # получаем текст ответа модели
        assistant_text = addAssistantResponse(response, messages)
        print(f"\nМастер игры: {assistant_text}\n")
        # вывод в текст бокс
        # обновляем настройки для нейронки
        updateSystemMessage(messages)
    except Exception as e:
        showerror(title="Анализ чего-то", message=f"Ошибка во анализа: {e}")
        # print("Попробуйте еще раз или завершите анализ (Ctrl+C).")

# первичные настройки для подготовки общения с нейронкой
def startCommunication():
    try:
        # загружаем переменные среды из .env
        load_dotenv()
        # устанавливаем соединение с нейронкой
        client = getClient()
        # получаем объект модели
        model = os.getenv("model")
        # сообщения для нейронки
        messages = []
        messages.append({"role": "system"})
        # обновляем настройки для нейронки
        updateSystemMessage(messages)
        # первый запрос для нейронки
        addStartPrompt(messages)
        # получаем ответ от сервера модели по отправленным сообщениям
        response = chat(messages, model, client)
        # получаем текст ответа модели
        assistant_text = addAssistantResponse(response, messages)
        print(assistant_text)

    except Exception as e:
        showerror(title="Анализ чего-то", message=f"Ошибка во анализа: {e}")

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
        showinfo(title="Получение авиакомпаний",
                 message="При выгрузке данных из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")

    return airport

def createGraph(db, components, needSave):
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
        # добавляем дату - метка на оси X
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

    # настройка шрифта
    plt.rcParams.update({"font.size": 10})
    # настраиваем размеры окна
    plt.figure(figsize=(10, 5))
    # настраиваем заголовок графика
    plt.title("Список полетов")
    # настраиваем заголовки осей
    plt.xlabel("Дата вылета")
    plt.ylabel("Количество рейсов")
    plt.plot(names, valuesOnTime, color="green")
    plt.plot(names, valuesDelay, color="yellow")
    plt.plot(names, valuesCansel, color="red")
    # Поворачиваем подписи осей
    plt.xticks(rotation=89)
    plt.tight_layout()  # Автоматически регулирует размеры для избегания перекрытий

    # если надо сохранить
    if (needSave.get()):
        if (not os.path.exists("code/reports/flightsGraphReport")):
            # создаем папку для графиков
            os.mkdir("code/reports/flightsGraphReport")
        # создаем папку с указанием текущей даты и времени
        folderName = datetime.now()
        folderName = folderName.strftime("%d") + "." + folderName.strftime("%m") + "." + folderName.strftime(
            "%Y") + "_" + folderName.strftime("%H") + "-" + folderName.strftime("%M")
        # в названии папки указываем дату
        os.mkdir(f"code/reports/flightsGraphReport/report_{folderName}")
        # сохранение графика в виде изображения
        plt.savefig(f"code/reports/flightsGraphReport/report_{folderName}/graph.jpg")
        showinfo(title="Соханение графика", message="График успешно сохранен!")

    # показываем график
    plt.show()

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
        showinfo(title="Загрузка рейсов", message="При выгрузке рейсов из БД произошла непредвиденная ошибка! Проверьте БД и попробуйте снова.")
        return False

# заполнение таблицы данными на форме анализа рейсов из БД
def insertDataToTable(db, table, components):
    # загружаем список полетов для построения таблицы
    df = loadFlyList(db)
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
        if (len(components) == 10):
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
    # разбираю по переменным ссылки на объекты
    dateFrom, dateUntil, timeFrom, timeUntil, depDel, arrDel, company, status, airportDep, airportArr = componentsVal

    for index, row in df.iterrows():
        # 2026-2-30 10:20:00
        dt = str(row["schDep"]).split()[0]
        tm = str(row["schDep"]).split()[1][:-3]
        # обходим DF, берем только подходящие по дате и времени строки
        if (dt >= dateFrom) and (dt <= dateUntil):
            if (tm >= timeFrom) and (tm <= timeUntil):
                # проверяем компанию, статус, аэропорты
                if (((company == "Все компании") or (row["company"] == company)) and
                    ((status == "Все варианты") or (row["status"] == status)) and
                    ((airportDep == "Все аэропорты") or (row["airportDep"] == airportDep)) and
                    ((airportArr == "Все аэропорты") or (row["airportArr"] == airportArr))):
                        # проверяем, задерживается или по расписанию и соответствует ли это настройкам
                        if (checkDel(depDel, row["schDep"], row["actDep"]) and checkDel(arrDel, row["schArr"], row["actArr"])):
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
        # загружаем шаблон отчета
        doc = DocxTemplate("code/reports/flightsMainReport.docx")

        dateFrom = dateFrom.split("-")
        dateUntil = dateUntil.split("-")
        # словарь подстановки данных в шаблон
        context = {
            "reportDate": folderName,
            "dateFrom": dateFrom[-1] + "." + dateFrom[-2] + "." + dateFrom[-3],
            "timeFrom": timeFrom,
            "dateUntil": dateUntil[-1] + "." + dateUntil[-2] + "." + dateUntil[-3],
            "timeUntil": timeUntil,
            "id": "",
            "flyNum": "",
            "company": "",
            "airportDep": "",
            "airportArr": "",
            "dateTimeDep": "",
            "dateTimeArr": "",
            "status": "",
            "delay": "",
            "reason": "",
        }

        # заполняем словарь данными из БД
        # здесь row - строка вида [(column_caption, value), (..), ..]
        for row in fData:
            context["id"] += str(row[0]) + "\n\n"
            context["flyNum"] += row[1] + "\n\n"
            context["company"] += row[2] + "\n\n"
            context["airportDep"] += row[3] + "\n\n"
            context["airportArr"] += row[4] + "\n\n"
            context["dateTimeDep"] += str(row[5]) + "/" + str(row[7]) + "\n"
            context["dateTimeArr"] += str(row[6]) + "/" + str(row[8]) + "\n"
            context["status"] += row[9] + "\n"
            context["delay"] += str(row[10]) + "\n\n"
            context["reason"] += str(row[11]) + "\n\n"

        # загружаем данные из контекста в шаблон
        doc.render(context)
        # сохраняем отчет в конкретную папку
        doc.save(f"code/reports/flightsMainReport/report_{folderName}/отчет_по_рейсам.docx")
        showinfo(title="Создание отчета", message="Отчет успешно сформирован!")

    except Exception as e:
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
    showwarning(title="Поиск рейса",
                message="Указанный рейс не найден!")
