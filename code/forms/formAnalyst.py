# библиотека графических элементов для
from tkinter import *
# дополнительные виджеты
from tkinter import ttk
# шрифты
from tkinter import font
# прокручиваемый текст
from tkinter.scrolledtext import ScrolledText
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

# дата и время
from datetime import datetime, timedelta

# подключаем файл с функциями обработки данных, получаемых от форм
import funcs.funcsAuth as fAuth
# подключаем файл с функциями обработки данных, получаемых от форм админа
from funcs.funcsAnalystForm import *
# функции для работы с формами
from funcs.funcsForm import createGrid, createWindow
# константы
import consts

# создаем форму для работы аналитика - окно работы с таблицей полетов
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createAnalystFlightsForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 1270
    h = 800
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ДАННЫЕ ПО РЕЙСАМ")
    lblMain.pack(pady=[30, 10])

    # -------------БЛОК таблицы-------------

    # создаем рамку таблицы рейсов
    lfFlyList = LabelFrame(frMain, font=consts.FNTLBLH2, text="Список рейсов", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    flyList = ttk.Treeview(lfFlyList, columns=[], show="headings", height=9)

    # создаем полосы прокрутки для таблицы
    scrlV = Scrollbar(lfFlyList, orient="vertical", command=flyList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = Scrollbar(lfFlyList, orient="horizontal", command=flyList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    flyList["yscrollcommand"] = scrlV.set
    flyList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in flyList["columns"]:
        flyList.heading(col, text="")
    flyList.delete(*flyList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Номер рейса", "Авиакомпания", "Аэропорт вылета", "Аэропорт прибытия", "Плановое время вылета", "Плановое время прибытия", "Фактическое время вылета", "Фактическое время прибытия", "      Статус      ", "Минуты задержки", "Причина отмены"]
    # строим таблицу по полученным данным
    flyList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        flyList.heading(col, text=col, anchor=CENTER,
        # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
        command = (lambda tree, i, f: (lambda: columnSort(tree, i, f)))(flyList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        flyList.column(f"#{i}", width=len(col) * 7, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, flyList, [], 10)

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    flyList.pack(fill=BOTH, expand=1, padx=5, pady=[10, 10])
    # добавляем таблицу на форму
    lfFlyList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # -------------БЛОК кнопок управления графиком-------------

    # создаем рамку для кнопок
    frManageBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Настрока отображения графика", borderwidth=1, relief=SOLID)

    # сетка компонентов 8x9
    createGrid(frManageBtns, 8, 8, 1, 1)
    # массив компонентов управления данными
    components = []
    # переменная для отслеживания изменения чекбокса ,,сохранить график,,
    cbtnSaveGraphVar = IntVar()

            # -------------ЭЛЕМЕНТЫ управления ДАТОЙ И ВРЕМЕНЕМ-------------
    # дата от
    lblDateFrom = Label(frManageBtns, font=consts.FNTLBLS, text="Дата от:", padx=0, pady=0)
    lblDateFrom.grid(row=0, column=0, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrDateFromVar = StringVar()
    etrDateFromVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # текстовое поле дата ОТ
    etrDateFrom = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrDateFromVar)
    # значение по умолчанию для поля ввода
    etrDateFrom.insert(0, "2000-01-01")
    etrDateFrom.grid(row=1, column=0, columnspan=1, padx=10, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateFrom)

    # дата до
    lblDateUntil = Label(frManageBtns, font=consts.FNTLBLS, text="Дата до:", padx=0, pady=0)
    lblDateUntil.grid(row=2, column=0, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrDateUntilVar = StringVar()
    etrDateUntilVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # текстовое поле дата ДО
    etrDateUntil = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrDateUntilVar)
    # значение по умолчанию для поля ввода
    etrDateUntil.insert(0, str(datetime.now().date()))
    etrDateUntil.grid(row=3, column=0, columnspan=1, padx=10, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateUntil)

    # время от
    lblTimeFrom = Label(frManageBtns, font=consts.FNTLBLS, text="Время от:", padx=0, pady=0)
    lblTimeFrom.grid(row=0, column=2, columnspan=2, padx=0, pady=[10, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeFromVar = StringVar()
    etrTimeFromVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # текстовое поле время ОТ
    etrTimeFrom = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrTimeFromVar)
    # значение по умолчанию для поля ввода
    etrTimeFrom.insert(0, "00:00")
    etrTimeFrom.grid(row=1, column=2, columnspan=1, padx=0, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeFrom)

    # время до
    lblTimeUntil = Label(frManageBtns, font=consts.FNTLBLS, text="Время до:", padx=0, pady=0)
    lblTimeUntil.grid(row=2, column=2, columnspan=2, padx=0, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeUntilVar = StringVar()
    etrTimeUntilVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # текстовое поле время ДО
    etrTimeUntil = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrTimeUntilVar)
    # значение по умолчанию для поля ввода
    etrTimeUntil.insert(0, "23:59")
    etrTimeUntil.grid(row=3, column=2, columnspan=1, padx=0, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeUntil)

        # -------------ЭЛЕМЕНТЫ управления ВЫЛЕТОМ И ПРИЗЕМЛЕНИЕМ-------------

    # вылет (опоздание или нет)
    lblDep = Label(frManageBtns, font=consts.FNTLBLS, text="Вылет:")
    lblDep.grid(row=0, column=4, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # группа для radioBtns
    workModeDep = StringVar(value="allDep")
    # добавляем в массив компонентов текущий элемент
    components.append(workModeDep)
    # изменение поиска все, опоздавшие, вылетевшие по расписанию
    clickFunc = lambda: insertDataToTable(db, flyList, components, 10)
    # кнопка для выбора всех вариантов вылетов
    radioAllDep = Radiobutton(frManageBtns, font=consts.FNTBTNMINI, text="Все варианты", command=clickFunc, padx=5,
                              pady=0, value="allDep", variable=workModeDep)
    radioAllDep.grid(row=1, column=4, rowspan=1, padx=15, pady=[0, 0], sticky=W)
    # кнопка для выбора опоздавших самолетов
    radioDelayDep = Radiobutton(frManageBtns, font=consts.FNTBTNMINI, text="Опоздавшие",
                                command=clickFunc, padx=5, pady=0, value="delayDep", variable=workModeDep)
    radioDelayDep.grid(row=2, column=4, rowspan=1, padx=15, pady=[0, 0], sticky=W)
    # кнопка для выбора рейсов, улетевших по расписанию
    radioScheduleDep = Radiobutton(frManageBtns, font=consts.FNTBTNMINI, text="По расписанию",
                                   command=clickFunc, padx=5, pady=0, value="scheduleDep", variable=workModeDep)
    radioScheduleDep.grid(row=3, column=4, rowspan=1, padx=15, pady=[0, 0], sticky=W)

    # посадка (опоздание или нет)
    lblArr = Label(frManageBtns, font=consts.FNTLBLS, text="Посадка:")
    lblArr.grid(row=4, column=4, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # группа для radioBtns
    workModeArr = StringVar(value="allArr")
    # добавляем в массив компонентов текущий элемент
    components.append(workModeArr)
    # изменение поиска все, опоздавшие, вылетевшие по расписанию
    clickFunc = lambda: insertDataToTable(db, flyList, components, 10)
    # кнопка для выбора всех вариантов вылетов
    radioAllArr = Radiobutton(frManageBtns, font=consts.FNTBTNMINI, text="Все варианты", command=clickFunc, padx=5,
                              pady=0, value="allArr", variable=workModeArr)
    radioAllArr.grid(row=5, column=4, rowspan=1, padx=15, pady=[0, 0], sticky=W)
    # кнопка для выбора опоздавших самолетов
    radioDelayArr = Radiobutton(frManageBtns, font=consts.FNTBTNMINI, text="Опоздавшие",
                                command=clickFunc, padx=5, pady=0, value="delayArr", variable=workModeArr)
    radioDelayArr.grid(row=6, column=4, rowspan=1, padx=15, pady=[0, 0], sticky=W)
    # кнопка для выбора рейсов, улетевших по расписанию
    radioScheduleArr = Radiobutton(frManageBtns, font=consts.FNTBTNMINI, text="По расписанию",
                                   command=clickFunc, padx=5, pady=0, value="scheduleArr", variable=workModeArr)
    radioScheduleArr.grid(row=7, column=4, rowspan=1, padx=15, pady=[0, 20], sticky=W)


        # -------------ЭЛЕМЕНТЫ управления КОМПАНИЕЙ И СТАТУСОМ-------------

    # компания
    lblCompany = Label(frManageBtns, font=consts.FNTLBLS, text="Авиакомпания: ", padx=0, pady=0)
    lblCompany.grid(row=0, column=5, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    cbxCompanyVar = StringVar()
    cbxCompanyVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # получаем список авиакомпаний
    companyList = getCompany(db)
    # выпадающий список компаний
    cbxCompany = ttk.Combobox(frManageBtns, values=["Все компании", *companyList], state="readonly", textvar=cbxCompanyVar)
    # устанавливаем значение по умолчанию
    cbxCompany.current(0)
    # устанавливаем позицию компонента в сетке
    cbxCompany.grid(row=1, column=5, padx=15, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(cbxCompany)

    # статус рейса
    lblStatus = Label(frManageBtns, font=consts.FNTLBLS, text="Статус рейса: ", padx=0, pady=0)
    lblStatus.grid(row=2, column=5, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    cbxStatusVar = StringVar()
    cbxStatusVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # выпадающий список статусов
    cbxStatus = ttk.Combobox(frManageBtns, values=["Все варианты", "Отменен", "Открыта регистрация", "Открыта посадка",
                                                   "Ожидает вылета", "В полете",
                                                 "Вылет задерживается", "Регистрация завершена", "Посадка закончена",
                                                 "Вылет состоялся", "Посадка задерживается", "Прибыл по расписанию",
                                                 "Прибыл с задержкой"], state="readonly", textvar=cbxStatusVar)
    # устанавливаем значение по умолчанию
    cbxStatus.current(0)
    # устанавливаем позицию компонента в сетке
    cbxStatus.grid(row=3, column=5, padx=15, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(cbxStatus)


        # -------------ЭЛЕМЕНТЫ управления АЭРОПОРТОМ-------------

    # аэропорт вылета
    lblAirportDep = Label(frManageBtns, font=consts.FNTLBLS, text="Аэропорт вылета: ", padx=0, pady=0)
    lblAirportDep.grid(row=0, column=6, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    cbxAirportDepVar = StringVar()
    cbxAirportDepVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # получаем список аэропортов отправления
    airportList = getAirport(db, "dep")
    # выпадающий список аэропортов
    cbxAirportDep = ttk.Combobox(frManageBtns, values=["Все аэропорты", *airportList], state="readonly", textvar=cbxAirportDepVar)
    # устанавливаем значение по умолчанию
    cbxAirportDep.current(0)
    # устанавливаем позицию компонента в сетке
    cbxAirportDep.grid(row=1, column=6, padx=15, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(cbxAirportDep)

    # аэропорт приземления
    lblAirportArr = Label(frManageBtns, font=consts.FNTLBLS, text="Аэропорт посадки: ", padx=0, pady=0)
    lblAirportArr.grid(row=2, column=6, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    cbxAirportArrVar = StringVar()
    cbxAirportArrVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 10))
    # получаем список аэропортов отправления
    airportList = getAirport(db, "arr")
    # выпадающий список аэропортов
    cbxAirportArr = ttk.Combobox(frManageBtns, values=["Все аэропорты", *airportList], state="readonly", textvar=cbxAirportArrVar)
    # устанавливаем значение по умолчанию
    cbxAirportArr.current(0)
    # устанавливаем позицию компонента в сетке
    cbxAirportArr.grid(row=3, column=6, padx=15, pady=[0, 10], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(cbxAirportArr)


        # -------------КНОПКИ управления-------------

    # сформировать отчет
    clickFunc = lambda: createReport(db, components)
    btnCreateReport = Button(frManageBtns, font=consts.FNTBTN, text="Сформировать отчет", command=clickFunc, padx=15, pady=10)
    btnCreateReport.grid(row=0, column=7, columnspan=2, rowspan=2, padx=0, pady=[10, 0])

    # сформировать график
    clickFunc = lambda: createGraph(db, components, cbtnSaveGraphVar)
    btnCreateGraph = Button(frManageBtns, font=consts.FNTBTN, text="Сформировать график", command=clickFunc, padx=9, pady=10)
    btnCreateGraph.grid(row=2, column=7, columnspan=2, rowspan=2, padx=0, pady=[0, 0])

    # сохранить график
    cbtnSaveGraph = Checkbutton(frManageBtns, font=consts.FNTBTN, text="Сохранить график", variable=cbtnSaveGraphVar)
    cbtnSaveGraph.grid(row=4, column=7, columnspan=2, rowspan=2, padx=0, pady=[0, 0])

    # массив радио-кнопок
    # radioBtnArr = [radioAllDep, radioDelayDep, radioScheduleDep, radioAllArr, radioDelayArr, radioScheduleArr]
    # массив комбобоксов
    cbxArr = [cbxCompany, cbxStatus, cbxAirportDep, cbxAirportArr]
    # сбросить настройки
    clickFunc = lambda: resetSettings(etrDateFrom, etrDateUntil, etrTimeFrom, etrTimeUntil, workModeDep, workModeArr, cbxArr)
    btnResetSettings = Button(frManageBtns, font=consts.FNTBTN, text="Сбросить настройки", command=clickFunc, padx=20, pady=10)
    btnResetSettings.grid(row=6, column=7, columnspan=2, rowspan=2, padx=0, pady=[0, 20])

    frManageBtns.pack(fill=BOTH, padx=10, pady=[10, 20], ipadx=3)

    # выход в предыдущее меню
    clickFunc = lambda: createAnalystMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=10)
    btnBack.pack(fill=BOTH, padx=30, pady=20, ipadx=10, ipady=5)


    frMain.pack(fill=BOTH, padx=10, pady=20, ipadx=10, ipady=5)

    root.mainloop()

# окно прогнозирования отмены рейсов и количества людей, которые захотят остаться в гостинице
def createAnalystForecastForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 1270
    h = 1000
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=0)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ПРОГНОЗИРОВАНИЕ И АНАЛИТИКА")
    lblMain.pack(pady=[10, 0])

    # -------------БЛОК таблицы-------------

    # создаем рамку таблицы рейсов
    lfFlyList = LabelFrame(frMain, font=consts.FNTLBLH2, text="Список рейсов", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    flyList = ttk.Treeview(lfFlyList, columns=[], show="headings", height=5)

    # создаем полосы прокрутки для таблицы
    scrlV = Scrollbar(lfFlyList, orient="vertical", command=flyList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = Scrollbar(lfFlyList, orient="horizontal", command=flyList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    flyList["yscrollcommand"] = scrlV.set
    flyList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in flyList["columns"]:
        flyList.heading(col, text="")
    flyList.delete(*flyList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Номер рейса", "Авиакомпания", "Аэропорт вылета", "Аэропорт прибытия", "Плановое время вылета",
            "Плановое время прибытия", "Фактическое время вылета", "Фактическое время прибытия", "      Статус      ",
            "Минуты задержки", "Причина отмены"]
    # строим таблицу по полученным данным
    flyList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        flyList.heading(col, text=col, anchor=CENTER,
        # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
        command = (lambda tree, i, f: (lambda: columnSort(tree, i, f)))(flyList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        flyList.column(f"#{i}", width=len(col) * 7, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, flyList, [], 4)

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    flyList.pack(fill=BOTH, expand=1, padx=5, pady=[10, 10])
    # добавляем таблицу на форму
    lfFlyList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # -------------БЛОК управления-------------

    # создаем рамку блока управления
    lfManageField = LabelFrame(frMain, font=consts.FNTLBLH2, text="Настройки прогнозирования", borderwidth=1, relief=SOLID)

    # сетка компонентов 5x10
    createGrid(lfManageField, 5, 10, 1, 1)
    components = []

    # поиск рейсов
    lblFindFlight = Label(lfManageField, font=consts.FNTLBLH2, text="Поиск рейсов:")
    lblFindFlight.grid(row=0, column=0, columnspan=1, rowspan=1, padx=10, pady=[0, 0], sticky=W)
    # номер рейса
    lblFlightNum = Label(lfManageField, font=consts.FNTLBLH3, text="Введите номер рейса:")
    lblFlightNum.grid(row=1, column=0, columnspan=1, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # текстовое поле номер рейса
    etrFlightNum = Entry(lfManageField, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrFlightNum.insert(0, "")
    etrFlightNum.grid(row=2, column=0, columnspan=1, padx=10, pady=[0, 0], sticky=W)
    # найти рейс
    clickFunc = lambda: findFlight(flyList, etrFlightNum.get())
    btnfindFlight = Button(lfManageField, font=consts.FNTBTNMINI, text="Найти рейс",
                                   command=clickFunc, padx=35, pady=5)
    btnfindFlight.grid(row=3, column=0, columnspan=1, rowspan=2, padx=10, pady=[10, 10], sticky=W)

        # -------------управление типом прогноза-------------
    # тип прогноза
    lblForecastType = Label(lfManageField, font=consts.FNTLBLH2, text="Выберите тип прогноза:")
    lblForecastType.grid(row=0, column=1, columnspan=1, rowspan=1, padx=0, pady=[10, 0], sticky=W)

    # группа для radioBtns
    forecastType = StringVar(value="FlightCansel")
    # кнопка для выбора прогноза по одному рейсу
    radioFlightCansel = Radiobutton(lfManageField, font=consts.FNTBTNMINI, text="Отмена рейса", padx=5,
                              pady=0, value="FlightCansel", variable=forecastType)
    radioFlightCansel.grid(row=1, column=1, rowspan=1, padx=15, pady=[0, 0], sticky=W)
    # кнопка для выбора прогноза по всем рейсам за период времени
    radioAllFlightCansel = Radiobutton(lfManageField, font=consts.FNTBTNMINI, text="Количество отменных\nрейсов за период", padx=5,
                                    pady=0, value="allFlightCansel", variable=forecastType)
    radioAllFlightCansel.grid(row=2, column=1, rowspan=2, padx=15, pady=[0, 0], sticky=W)
    # кнопка для выбора прогноза по количеству пассажиров на рейсе
    radioPassengerCount = Radiobutton(lfManageField, font=consts.FNTBTNMINI, text="Количество пассажиров\nс рейса, которым\nпотребуется гостиница", padx=5,
                                    pady=0, value="passengerCount", variable=forecastType)
    radioPassengerCount.grid(row=4, column=1, rowspan=2, padx=15, pady=[0, 0], sticky=W)
    # кнопка для выбора прогноза по количеству пассажиров по всем рейсам за период
    radioAllPassengerCount = Radiobutton(lfManageField, font=consts.FNTBTNMINI, text="Количество пассажиров,\nкоторым потребуется\nгостиница за период", padx=5,
                                    pady=0, value="allPassengerCount", variable=forecastType)
    radioAllPassengerCount.grid(row=6, column=1, rowspan=2, padx=15, pady=[0, 0], sticky=W)

        # -------------управление датой и временем-------------
    # заголовок блока управления датой и временем
    lblDateTime = Label(lfManageField, font=consts.FNTLBLH2, text="Настроить диапазон:")
    lblDateTime.grid(row=0, column=2, columnspan=2, rowspan=1, padx=0, pady=[10, 0], sticky=N)

    # дата от
    lblDateFrom = Label(lfManageField, font=consts.FNTLBLS, text="Дата от:")
    lblDateFrom.grid(row=1, column=2, columnspan=1, padx=10, pady=[0, 0], sticky=E)

    # переменная для отслеживания изменения поля ввода
    etrDateFromVar = StringVar()
    etrDateFromVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 4))
    # текстовое поле дата ОТ
    etrDateFrom = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrDateFromVar)
    # значение по умолчанию для поля ввода
    etrDateFrom.insert(0, "2000-01-01")
    etrDateFrom.grid(row=2, column=2, columnspan=1, padx=10, pady=[0, 0], sticky=E)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateFrom)

    # дата до
    lblDateUntil = Label(lfManageField, font=consts.FNTLBLS, text="Дата до:", padx=0, pady=0)
    lblDateUntil.grid(row=3, column=2, columnspan=1, padx=10, pady=[0, 0], sticky=E)

    # переменная для отслеживания изменения поля ввода
    etrDateUntilVar = StringVar()
    etrDateUntilVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 4))
    # текстовое поле дата ДО
    etrDateUntil = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrDateUntilVar)
    # значение по умолчанию для поля ввода
    etrDateUntil.insert(0, str(datetime.now().date()))
    etrDateUntil.grid(row=4, column=2, columnspan=1, padx=10, pady=[0, 0], sticky=E)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateUntil)

    # время от
    lblTimeFrom = Label(lfManageField, font=consts.FNTLBLS, text="Время от:", padx=0, pady=0)
    lblTimeFrom.grid(row=1, column=3, columnspan=2, padx=0, pady=[10, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeFromVar = StringVar()
    etrTimeFromVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 4))
    # текстовое поле время ОТ
    etrTimeFrom = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrTimeFromVar)
    # значение по умолчанию для поля ввода
    etrTimeFrom.insert(0, "00:00")
    etrTimeFrom.grid(row=2, column=3, columnspan=1, padx=0, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeFrom)

    # время до
    lblTimeUntil = Label(lfManageField, font=consts.FNTLBLS, text="Время до:", padx=0, pady=0)
    lblTimeUntil.grid(row=3, column=3, columnspan=2, padx=0, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeUntilVar = StringVar()
    etrTimeUntilVar.trace("w", lambda a, b, c: insertDataToTable(db, flyList, components, 4))
    # текстовое поле время ДО
    etrTimeUntil = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrTimeUntilVar)
    # значение по умолчанию для поля ввода
    etrTimeUntil.insert(0, "23:59")
    etrTimeUntil.grid(row=4, column=3, columnspan=1, padx=0, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeUntil)

    # добавляем блок на форму
    lfManageField.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

        # -------------дополнительное сообщени для прогнозирования-------------
    # доп сообщение
    lblAdditionsMessage = Label(lfManageField, font=consts.FNTLBLH2, text="Дополнительное сообщение для донастройки модели:")
    lblAdditionsMessage.grid(row=5, column=2, columnspan=2, rowspan=1, padx=10, pady=[10, 10], sticky=W)
    # текстовое поле доп сообщения
    tbAdditionsMessage = ScrolledText(lfManageField, width=90, height=3, wrap="word")
    tbAdditionsMessage.grid(row=6, column=2, columnspan=2, rowspan=3, padx=10, pady=[0, 10], sticky=W)

    # -------------БЛОК общения с нейронкой-------------

    # создаем рамку блока общения с нейронкой
    lfCommunicationField = LabelFrame(frMain, font=consts.FNTLBLH2, text="Результат прогнозирования", borderwidth=1, relief=SOLID)

    # сетка компонентов 7x5
    createGrid(lfCommunicationField, 7, 5, 1, 1)

    # текстовое поле для отображения переписки с нейронкой
    tbCommunication = ScrolledText(lfCommunicationField, width=170, height=10, wrap="none")
    tbCommunication.grid(row=0, column=0, columnspan=5, rowspan=4, padx=10, pady=[10, 10], sticky=NSEW)
    # добавляем скроллбар
    xs = Scrollbar(lfCommunicationField, orient="horizontal", command=tbCommunication.xview)
    xs.grid(column=0, row=4, columnspan=5, sticky=EW)
    tbCommunication["xscrollcommand"] = xs.set

    # начать прогнозирование
    clickFunc = lambda: startCommunication(tbCommunication, tbAdditionsMessage.get("1.0", "end"), flyList, components, forecastType.get())
    btnStartCommunication = Button(lfCommunicationField, font=consts.FNTBTNMINI, text="Начать прогнозирование",
                                   command=clickFunc, padx=30, pady=5)
    btnStartCommunication.grid(row=0, column=5, columnspan=2, rowspan=1, padx=10, pady=[0, 0])

    # текстовое поле для ввода сообщения-ответа нейронке
    tbMessage = ScrolledText(lfCommunicationField, width=40, height=5, wrap="word", pady=0)
    tbMessage.grid(row=1, column=5, columnspan=2, rowspan=1, padx=10, pady=[0, 0])

    # отправить сообщение
    clickFunc = lambda: communication(tbCommunication, tbMessage.get("1.0", "end"))
    btnSendMessage = Button(lfCommunicationField, font=consts.FNTBTNMINI, text="Отправить сообщение",
                                   command=clickFunc, padx=40, pady=5)
    btnSendMessage.grid(row=2, column=5, columnspan=2, rowspan=1, padx=10, pady=[0, 10])

    # добавляем блок на форму
    lfCommunicationField.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # выход в предыдущее меню
    clickFunc = lambda: createAnalystMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=3, pady=2)
    btnBack.pack(fill=BOTH, padx=30, pady=0, ipadx=10, ipady=5)

    frMain.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=10)

    root.mainloop()

# создаем форму для работы аналитика - выбор рабочего окна
def createAnalystMainForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 570
    h = 620
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="АНАЛИТИЧЕСКИЕ ДАННЫЕ")
    lblMain.pack(pady=30)

    # создаем рамку для кнопок
    frBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Рабочие окна", borderwidth=1, relief=SOLID)

    # сетка компонентов 9x3
    createGrid(frBtns, 3, 9, 1, 1)

    # -------------БЛОК выбора окна-------------

    # прогнозирование
    clickFunc = lambda: createAnalystForecastForm(db, root, usrData)
    # прогнозирование
    btnForecastForm = Button(frBtns, font=consts.FNTBTN, text="Прогнозы и модели", command=clickFunc, padx=25, pady=20)
    btnForecastForm.grid(row=1, column=1, rowspan=2, padx=15, pady=[35, 10])

    # аналитика рейсов
    clickFunc = lambda: createAnalystFlightsForm(db, root, usrData)
    # аналитика рейсов
    btnFlightsForm = Button(frBtns, font=consts.FNTBTN, text="Анализ рейсов", command=clickFunc, padx=43, pady=20)
    btnFlightsForm.grid(row=4, column=1, rowspan=2, padx=15, pady=[10, 10])

    # выход из пользователя
    btnLogOut = Button(frBtns, font=consts.FNTBTN, text="Сменить пользователя", padx=12, pady=20,
                       command=lambda: fAuth.logOut(db, root))
    btnLogOut.grid(row=7, column=1, rowspan=2, padx=15, pady=[10, 35])

    # добавляем раздел на форму
    frBtns.pack(anchor=NW, fill=BOTH, padx=15, pady=[0, 10])

    frMain.pack(fill=BOTH, padx=5, pady=5, ipadx=10, ipady=10)

    root.mainloop()