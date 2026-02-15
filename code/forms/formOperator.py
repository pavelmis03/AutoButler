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

# подключаем файл с функциями обработки данных, получаемых от форм
import funcs.funcsAuth as fAuth
# подключаем файл с функциями обработки данных, получаемых от форм админа
from funcs.funcsOperatorForm import *
# функции для работы с формами
from funcs.funcsForm import createGrid, createWindow
# константы
import consts

# создаем форму для работы оператора - подбор гостиницы
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createOperatorChooseHotelForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 1500
    h = 800
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=10,
                        marginy=0)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ПОДОБРАТЬ ГОСТИНИЦУ")
    lblMain.pack(pady=[30, 10])

    # создаем рамку таблицы рейсов
    frInfoList = Frame(frMain, borderwidth=1, relief=SOLID)

    # -------------БЛОК таблицы полетов-------------

    lfFlyList = LabelFrame(frInfoList, font=consts.FNTLBLH2, text="Список отмененных рейсов", borderwidth=1, relief=SOLID)

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
    for col in flyList['columns']:
        flyList.heading(col, text='')
    flyList.delete(*flyList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Номер рейса", "Авиакомпания", "Аэропорт вылета", "Аэропорт прибытия", "Статус", "Причина отмены", "Класс рейса", "Количество пассажиров"]
    # строим таблицу по полученным данным
    flyList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        flyList.heading(col, text=col, anchor=CENTER)
        # выравнивание по центру для данных в ячейках
        flyList.column(f"#{i}", width=len(col) * 7, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # -------------БЛОК таблицы пассажиров-------------

    lfPassList = LabelFrame(frInfoList, font=consts.FNTLBLH2, text="Пассажиры рейса", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    passList = ttk.Treeview(lfPassList, columns=[], show="headings", height=9)

    # создаем полосы прокрутки для таблицы
    scrlV = Scrollbar(lfPassList, orient="vertical", command=passList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = Scrollbar(lfPassList, orient="horizontal", command=passList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    passList["yscrollcommand"] = scrlV.set
    passList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in passList['columns']:
        passList.heading(col, text='')
    passList.delete(*passList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Номер рейса", "    Имя   ", "Фамилия", "Ссылка на бронь", "Номер билета", "Стоимость билета"]
    # строим таблицу по полученным данным
    passList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        passList.heading(col, text=col, anchor=CENTER)
        # выравнивание по центру для данных в ячейках
        passList.column(f"#{i}", width=len(col) * 9, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, flyList, passList, "first")
    # выделяем первую строку, по которой пассажиров выгрузили
    flyList.selection_add(0)
    # добавляем, растягивая по ширине элементы и заполняя контейнер
    flyList.pack(fill=NONE, expand=0, padx=5, pady=[10, 10], anchor=NW)
    # при нажатии на строку таблицы полетов подгружаются данные по пассажирам этого рейса
    clickFunc = lambda e: insertDataToTable(db, flyList, passList, "second")
    # привязываем событие обработки нажатия на строку
    flyList.bind("<<TreeviewSelect>>", clickFunc)
    # добавляем блок таблицы полетов на форму
    lfFlyList.pack(anchor=NW, fill=NONE, padx=10, pady=[0, 0], side=LEFT)

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    passList.pack(fill=NONE, expand=0, padx=5, pady=[10, 10], anchor=NW)
    # добавляем блок таблицы пассажиров на форму
    lfPassList.pack(anchor=NW, fill=BOTH, padx=10, pady=[0, 0], side=LEFT)

    # добавляем таблицы на форму
    frInfoList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # -------------БЛОК подбора готинницы-------------

    lfHotelSettings = LabelFrame(frMain, font=consts.FNTLBLH2, text="Подобрать гостиницу", borderwidth=1, relief=SOLID)
    # сетка компонентов 9x9
    createGrid(lfHotelSettings, 9, 9, 1, 1)

    # -------------БЛОК выбора пассажира-------------

    # выберите пассажира
    lblChoosePass = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Выберите пассажира на рейсе:")
    lblChoosePass.grid(row=0, column=0, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)

    # введите имя, или фамилию, или номер рейса
    lblFindPass = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Введите имя, или фамилию:")
    lblFindPass.grid(row=1, column=0, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # текстовое поле для поиска
    etrFindPass = Entry(lfHotelSettings, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrFindPass.insert(0, "")
    etrFindPass.grid(row=2, column=0, columnspan=2, padx=10, pady=[5, 0], sticky=W)

    # найденные пассажиры
    lblFindPassResult = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Найденные пассажиры:")
    lblFindPassResult.grid(row=3, column=0, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список компаний
    cbxPassResult = ttk.Combobox(lfHotelSettings, values=["Пассажиров не найдено"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxPassResult.current(0)
    # устанавливаем позицию компонента в сетке
    cbxPassResult.grid(row=4, column=0, columnspan=2, rowspan=2, padx=15, pady=[5, 10], sticky=W)

    # члены семьи
    lblFamilyMember = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Члены семьи:")
    lblFamilyMember.grid(row=5, column=0, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # члены семьи
    sbFamilyMember = Spinbox(from_=1.0, to=100.0)
    sbFamilyMember.grid(row=6, column=0, columnspan=2, rowspan=1, padx=10, pady=[10, 10], sticky=W)

    # -------------БЛОК выбранный пользователь-------------

    # выберите пассажира
    lblChooseFlight = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Выбранный пассажир:")
    lblChooseFlight.grid(row=0, column=2, columnspan=2, rowspan=1, padx=10, pady=[0, 0], sticky=W)

    # данные по пассажиру
    lblPassFIO = Label(lfHotelSettings, font=consts.FNTLBLH3, text="ФИО: ")
    lblPassFIO.grid(row=1, column=2, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # данные по пассажиру
    lblPassFlight = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Рейс: ")
    lblPassFlight.grid(row=2, column=2, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # данные по пассажиру
    lblPassClass = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Класс: ")
    lblPassClass.grid(row=3, column=2, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)

    # список лэйблов для передачи данных о пассажире
    components = [lblPassFIO, lblPassFlight, lblPassClass]

    clickFunc = lambda e: selectPass(cbxPassResult, flyList, passList, components, "cbx")
    # привязываем функцию-обработчик нажатия при выборе пассажира в комбо-боксе
    cbxPassResult.bind("<<ComboboxSelected>>", clickFunc)

    # при нажатии на строку таблицы пассажиров подгружаются данные по пассажиру
    clickFunc = lambda e: selectPass(cbxPassResult, flyList, passList, components, "table")
    # привязываем событие обработки нажатия на строку
    passList.bind("<<TreeviewSelect>>", clickFunc)

    # получаем список найденных пассажиров
    clickFunc = lambda: getPass(db, flyList, passList, etrFindPass.get(), cbxPassResult, components)
    btnFindPass = Button(lfHotelSettings, font=consts.FNTBTN, text="Найти пассажира", command=clickFunc, padx=15, pady=10)
    btnFindPass.grid(row=4, column=2, columnspan=2, rowspan=1, padx=0, pady=[10, 0])

    # подобрать номер
    clickFunc = lambda: getHotels()
    btnFindHotels = Button(lfHotelSettings, font=consts.FNTBTN, text="Подобрать номера", command=clickFunc, padx=15, pady=10)
    btnFindHotels.grid(row=5, column=2, columnspan=2, rowspan=1, padx=0, pady=[10, 0])

    # закрепить номер за пассажиром
    clickFunc = lambda: chooseHotel(db, flyList, passList, etrFindPass.get(), cbxPassResult, components)
    btnChooseHotel = Button(lfHotelSettings, font=consts.FNTBTN, text="Закрепить номер за пассажиром", command=clickFunc, padx=15, pady=10)
    btnChooseHotel.grid(row=5, column=2, columnspan=2, rowspan=1, padx=0, pady=[10, 0])

    # -------------БЛОК сообщений для модели-------------

    # дополнительное сообщение для модели
    lblComm = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Сообщение для модели:")
    lblComm.grid(row=0, column=2, columnspan=2, rowspan=1, padx=10, pady=[0, 0], sticky=W)
    # текстовое поле для комментария
    tbComm = Text(lfHotelSettings, width=25, height=5, wrap="word")
    tbComm.grid(row=5, column=1, rowspan=3, padx=15, pady=[0, 10], sticky=W)
    # отправить сообщение
    clickFunc = lambda: addMessage()
    btnChooseHotel = Button(lfHotelSettings, font=consts.FNTBTN, text="Отправить сообщение", command=clickFunc, padx=15, pady=10)
    btnChooseHotel.grid(row=5, column=2, columnspan=2, rowspan=1, padx=0, pady=[10, 0])

    # добавляем блок на форму
    lfHotelSettings.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # выход в предыдущее меню
    clickFunc = lambda: createOperatorMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=10)
    btnBack.pack(fill=BOTH, padx=30, pady=20, ipadx=10, ipady=5)

    frMain.pack(fill=BOTH, padx=10, pady=20, ipadx=10, ipady=5)

    root.mainloop()

# окно для создания отчетов
def createOperatorReportsForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 1270
    h = 1000
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ОТЧЕТЫ")
    lblMain.pack(pady=30)

    # -------------БЛОК таблицы-------------

    # создаем рамку таблицы рейсов
    lfFlyList = LabelFrame(frMain, font=consts.FNTLBLH2, text="Список отмененных рейсов", borderwidth=1, relief=SOLID)

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
    for col in flyList['columns']:
        flyList.heading(col, text='')
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
        flyList.heading(col, text=col, anchor=CENTER)
        # выравнивание по центру для данных в ячейках
        flyList.column(f"#{i}", width=len(col) * 7, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, flyList, [])

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    flyList.pack(fill=BOTH, expand=1, padx=5, pady=[10, 10])
    # добавляем таблицу на форму
    lfFlyList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])



    # выход в предыдущее меню
    clickFunc = lambda: createOperatorMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=5)
    btnBack.pack(fill=BOTH, padx=30, pady=5, ipadx=10, ipady=10)

    frMain.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=10)

    root.mainloop()

# создаем форму для работы аналитика - выбор рабочего окна
def createOperatorMainForm(db, root, usrData):
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
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="РАЗМЕЩЕНИЕ ПАССАЖИРОВ")
    lblMain.pack(pady=30)

    # создаем рамку для кнопок
    frBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Рабочие окна", borderwidth=1, relief=SOLID)

    # сетка компонентов 9x3
    createGrid(frBtns, 3, 9, 1, 1)

    # -------------БЛОК выбора окна-------------

    # прогнозирование
    clickFunc = lambda: createOperatorChooseHotelForm(db, root, usrData)
    # прогнозирование
    btnForecastForm = Button(frBtns, font=consts.FNTBTN, text="Подобрать гостиницу", command=clickFunc, padx=20, pady=20)
    btnForecastForm.grid(row=1, column=1, rowspan=2, padx=15, pady=[35, 10])

    # аналитика рейсов
    clickFunc = lambda: createOperatorReportsForm(db, root, usrData)
    # аналитика рейсов
    btnFlightsForm = Button(frBtns, font=consts.FNTBTN, text="Создать отчет", command=clickFunc, padx=43, pady=20)
    btnFlightsForm.grid(row=4, column=1, rowspan=2, padx=15, pady=[10, 10])

    # выход из пользователя
    btnLogOut = Button(frBtns, font=consts.FNTBTN, text="Сменить пользователя", padx=12, pady=20,
                       command=lambda: fAuth.logOut(db, root))
    btnLogOut.grid(row=7, column=1, rowspan=2, padx=15, pady=[10, 35])

    # добавляем раздел на форму
    frBtns.pack(anchor=NW, fill=BOTH, padx=15, pady=[0, 10])

    frMain.pack(fill=BOTH, padx=5, pady=5, ipadx=10, ipady=10)

    root.mainloop()
