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
    w = 1550
    h = 800
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=-5,
                        marginy=0)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ПОДОБРАТЬ ГОСТИНИЦУ")
    lblMain.pack(pady=[10, 10])

    # создаем рамку таблицы рейсов
    frInfoList = Frame(frMain, borderwidth=1, relief=SOLID)

    # -------------БЛОК таблицы полетов-------------

    lfFlyList = LabelFrame(frInfoList,width=300, font=consts.FNTLBLH2, text="Список отмененных рейсов", borderwidth=0, relief=SOLID)

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
    cols = ["№", "Номер рейса", "Авиакомпания", "Аэропорт вылета", "Аэропорт прибытия", "    Статус    ", "Причина отмены", "Класс рейса", "Количество пассажиров"]
    # строим таблицу по полученным данным
    flyList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        flyList.heading(col, text=col, anchor=CENTER,
        # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
        command = (lambda tree, i, f: (lambda: columnSort(tree, i, f)))(flyList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        flyList.column(f"#{i}", width=len(col) * 7, minwidth=60, anchor=CENTER, stretch=True)
        i += 1

    # -------------БЛОК таблицы пассажиров-------------

    lfPassList = LabelFrame(frInfoList, font=consts.FNTLBLH2, text="Пассажиры рейса", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    passList = ttk.Treeview(lfPassList, columns=[], show="headings", height=5)

    # создаем полосы прокрутки для таблицы
    scrlV = Scrollbar(lfPassList, orient="vertical", command=passList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = Scrollbar(lfPassList, orient="horizontal", command=passList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    passList["yscrollcommand"] = scrlV.set
    passList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in passList["columns"]:
        passList.heading(col, text="")
    passList.delete(*passList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Номер рейса", "    Имя   ", "Фамилия", "Ссылка на бронь", "Номер билета", "Стоимость билета"]
    # строим таблицу по полученным данным
    passList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        passList.heading(col, text=col, anchor=CENTER,
        # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
        command = (lambda tree, i, f: (lambda: columnSort(tree, i, f)))(passList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        passList.column(f"#{i}", width=len(col) * 9, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, flyList, passList, "first")
    # выделяем первую строку, по которой пассажиров выгрузили
    flyList.selection_add(0)
    # добавляем, растягивая по ширине элементы и заполняя контейнер
    flyList.pack(fill=NONE, expand=0, padx=10, pady=[10, 10], anchor=NW)
    # при нажатии на строку таблицы полетов подгружаются данные по пассажирам этого рейса
    clickFunc = lambda e: insertDataToTable(db, flyList, passList, "second")
    # привязываем событие обработки нажатия на строку
    flyList.bind("<<TreeviewSelect>>", clickFunc)
    # добавляем блок таблицы полетов на форму
    lfFlyList.pack(anchor=NW, fill=NONE, expand=0, padx=10, pady=[0, 5], side=LEFT)

    # выделяем первую строку, по которой будем данные загружать
    passList.selection_add(0)
    # добавляем, растягивая по ширине элементы и заполняя контейнер
    passList.pack(fill=NONE, expand=0, padx=10, pady=[10, 10], anchor=NW)
    # добавляем блок таблицы пассажиров на форму
    lfPassList.pack(anchor=NW, fill=BOTH, padx=10, pady=[0, 5], side=LEFT)

    # добавляем таблицы на форму
    frInfoList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # -------------БЛОК подбора готинницы-------------

    lfHotelSettings = LabelFrame(frMain, font=consts.FNTLBLH2, text="Подобрать гостиницу", borderwidth=1, relief=SOLID)
    # сетка компонентов 9x9
    createGrid(lfHotelSettings, 12, 9, 1, 1)

    # -------------БЛОК выбора рейса-------------

    # выберите рейс
    lblChooseFlight = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Выберите рейс:")
    lblChooseFlight.grid(row=0, column=0, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # введите номер и компанию
    lblFindFlight = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Введите номер или компанию:")
    lblFindFlight.grid(row=1, column=0, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # текстовое поле для поиска
    etrFindFlight = Entry(lfHotelSettings, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrFindFlight.insert(0, "")
    etrFindFlight.grid(row=2, column=0, columnspan=2, padx=10, pady=[5, 0], sticky=W)

    # найденные рейсы
    lblFindFlightResult = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Найденные рейсы:")
    lblFindFlightResult.grid(row=3, column=0, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список рейсов
    cbxFlightResult = ttk.Combobox(lfHotelSettings, values=["Рейсов не найдено"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxFlightResult.current(0)
    # устанавливаем позицию компонента в сетке
    cbxFlightResult.grid(row=4, column=0, columnspan=2, rowspan=2, padx=10, pady=[5, 0], sticky=NW)

    # -------------БЛОК выбора пассажира-------------

    # выберите пассажира
    lblChoosePass = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Выберите пассажира на рейсе:")
    lblChoosePass.grid(row=0, column=2, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # введите имя, или фамилию, или номер рейса
    lblFindPass = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Введите имя или фамилию:")
    lblFindPass.grid(row=1, column=2, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # текстовое поле для поиска
    etrFindPass = Entry(lfHotelSettings, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrFindPass.insert(0, "")
    etrFindPass.grid(row=2, column=2, columnspan=2, padx=10, pady=[5, 0], sticky=W)

    # найденные пассажиры
    lblFindPassResult = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Найденные пассажиры:")
    lblFindPassResult.grid(row=3, column=2, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список пассажиров
    cbxPassResult = ttk.Combobox(lfHotelSettings, values=["Пассажиров не найдено"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxPassResult.current(0)
    # устанавливаем позицию компонента в сетке
    cbxPassResult.grid(row=4, column=2, columnspan=2, rowspan=2, padx=10, pady=[5, 0], sticky=NW)

    # члены семьи
    lblFamilyMember = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Члены семьи:")
    lblFamilyMember.grid(row=5, column=2, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # члены семьи
    sbFamilyMember = Spinbox(lfHotelSettings, from_=0.0, to=10.0)
    sbFamilyMember.grid(row=6, column=2, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # -------------БЛОК выбранный пользователь-------------

    # выбранный пассажир
    lblChoosedPass = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Выбранный пассажир:")
    lblChoosedPass.grid(row=0, column=4, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # данные по пассажиру
    lblPassFIO = Label(lfHotelSettings, font=consts.FNTLBLH3, text="ФИО: ")
    lblPassFIO.grid(row=1, column=4, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # данные по пассажиру
    lblPassFlight = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Рейс: ")
    lblPassFlight.grid(row=2, column=4, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # данные по пассажиру
    lblPassClass = Label(lfHotelSettings, font=consts.FNTLBLH3, text="Класс: ")
    lblPassClass.grid(row=3, column=4, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # список лэйблов для передачи данных о пассажире
    components = [lblPassFIO, lblPassFlight, lblPassClass]
    # список лэйблов для передачи данных о выбранном номере
    componentsH = []

    # заранее создаю переменные, чтобы потом сохранить в них нужные компоненты, не нарушая структуры кода
    hotelList = 0
    tbMess = 0
    # подобрать номер
    clickFunc = lambda: getHotelList(flyList, sbFamilyMember.get(), tbMess, hotelList, tbComm.get("1.0", "end"))
    btnFindHotels = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Подобрать номера", command=clickFunc, padx=48, pady=2)
    btnFindHotels.grid(row=4, column=4, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # закрепить номер за пассажиром
    clickFunc = lambda: chooseHotel(db, hotelList, passList, flyList, sbFamilyMember.get(), usrData["name"]) # , etrFindPass.get(), cbxPassResult
    btnChooseHotel = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Закрепить номер за пассажиром", command=clickFunc, padx=5, pady=2)
    btnChooseHotel.grid(row=5, column=4, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # -------------БЛОК выбранный номер-------------

    # выбранная гостиница
    lblChoosedHotel = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Выбранный номер:")
    lblChoosedHotel.grid(row=0, column=6, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # данные по гостинице
    lblHotelName = Label(lfHotelSettings, font=consts.FNTLBLH4, text="Название: ")
    lblHotelName.grid(row=1, column=6, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    componentsH.append(lblHotelName)
    # данные по гостинице
    lblHotelDist = Label(lfHotelSettings, font=consts.FNTLBLH4, text="Удаленность: ")
    lblHotelDist.grid(row=2, column=6, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    componentsH.append(lblHotelDist)
    # данные по гостинице
    lblHotelCost = Label(lfHotelSettings, font=consts.FNTLBLH4, text="Стоимость номера: ")
    lblHotelCost.grid(row=3, column=6, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    componentsH.append(lblHotelCost)
    # данные по гостинице
    lblHotelMeals = Label(lfHotelSettings, font=consts.FNTLBLH4, text="Питание: ")
    lblHotelMeals.grid(row=4, column=6, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    componentsH.append(lblHotelMeals)
    # данные по гостинице
    lblHotelLink = Label(lfHotelSettings, font=consts.FNTLBLH5, text="Ссылка: ")
    lblHotelLink.grid(row=5, column=6, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    componentsH.append(lblHotelLink)
    # данные по гостинице
    lblHotelAddit = Label(lfHotelSettings, font=consts.FNTLBLH4, text="Дополнительно: ")
    lblHotelAddit.grid(row=6, column=6, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    componentsH.append(lblHotelAddit)

    # скопировать ссылку
    clickFunc = lambda: copyHotelLink(hotelList)
    btnCopyLink = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Скопировать ссылку", command=clickFunc, padx=35, pady=2)
    btnCopyLink.grid(row=7, column=6, columnspan=2, rowspan=1, padx=10, pady=[0, 10], sticky=NW)

    # -------------БЛОК сообщений для модели-------------

    # дополнительное сообщение для модели
    lblComm = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Сообщение для модели:")
    lblComm.grid(row=0, column=8, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    # текстовое поле для комментария
    tbComm = ScrolledText(lfHotelSettings, width=25, height=6, wrap="word", pady=0)
    tbComm.grid(row=1, column=8, rowspan=4, padx=10, pady=[5, 0], sticky=NW)
    # отправить сообщение
    clickFunc = lambda: addMessage(flyList, sbFamilyMember.get(), tbMess, hotelList, tbComm.get("1.0", "end"))
    btnChooseHotel = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Отправить сообщение", command=clickFunc, padx=35, pady=2)
    btnChooseHotel.grid(row=5, column=8, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # -------------БЛОК переписки с моделью-------------

    # сообщения от нейронки
    lblMess = Label(lfHotelSettings, font=consts.FNTLBLH2, text="Лог сообщений:")
    lblMess.grid(row=0, column=10, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    # текстовое поле сообщений от нейронки
    # tbMess = ScrolledText(lfHotelSettings, width=35, height=14, wrap="word", pady=0)
    tbMess = ScrolledText(lfHotelSettings, width=35, height=14, pady=0)
    tbMess.grid(row=1, column=10, rowspan=8, columnspan=4, padx=10, pady=[5, 0], sticky=NW)

    # добавляем блок на форму
    lfHotelSettings.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # -------------БЛОК кнопок и действий которые нельзя было сделать раньше-------------

    # получаем список найденных рейсов
    clickFunc = lambda: getFlight(db, etrFindFlight.get(), cbxFlightResult)
    btnFindFlight = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Найти рейс", command=clickFunc, padx=59, pady=2)
    btnFindFlight.grid(row=5, column=0, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # выбрать рейс
    clickFunc = lambda: insertDataToTable(db, flyList, passList, "chooseFlight", cbxFlightResult)
    btnChooseFlight = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Выбрать рейс", command=clickFunc, padx=51, pady=2)
    btnChooseFlight.grid(row=6, column=0, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # выбрать пассажира
    clickFunc = lambda: insertDataToTable(db, flyList, passList, "choosePass", cbxPassResult)
    btnChoosePass = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Выбрать пассажира", command=clickFunc, padx=33,
                             pady=2)
    btnChoosePass.grid(row=7, column=0, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # получаем список найденных пассажиров
    clickFunc = lambda: getPass(db, flyList, passList, etrFindPass.get(), cbxPassResult, components)
    btnFindPass = Button(lfHotelSettings, font=consts.FNTBTNMINI, text="Найти пассажира", command=clickFunc, padx=51, pady=2)
    btnFindPass.grid(row=7, column=2, columnspan=2, rowspan=1, padx=10, pady=[5, 10], sticky=W)

    clickFunc = lambda e: insertDataToTable(db, flyList, passList, "chooseFlight", cbxFlightResult)
    # привязываем функцию-обработчик нажатия при выборе пассажира в комбо-боксе
    cbxFlightResult.bind("<<ComboboxSelected>>", clickFunc)

    clickFunc = lambda e: selectPass(cbxPassResult, flyList, passList, components, "cbx")
    # привязываем функцию-обработчик нажатия при выборе пассажира в комбо-боксе
    cbxPassResult.bind("<<ComboboxSelected>>", clickFunc)

    # при нажатии на строку таблицы пассажиров подгружаются данные по пассажиру
    clickFunc = lambda e: selectPass(cbxPassResult, flyList, passList, components, "table")
    # привязываем событие обработки нажатия на строку
    passList.bind("<<TreeviewSelect>>", clickFunc)

    # -------------БЛОК найденных гостиниц-------------

    lfHotels = LabelFrame(frMain, font=consts.FNTLBLH2, text="Найденные гостиницы", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    hotelList = ttk.Treeview(lfHotels, columns=[], show="headings", height=5)

    # создаем полосы прокрутки для таблицы
    scrlV = Scrollbar(lfHotels, orient="vertical", command=hotelList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = Scrollbar(lfHotels, orient="horizontal", command=hotelList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    hotelList["yscrollcommand"] = scrlV.set
    hotelList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in hotelList["columns"]:
        hotelList.heading(col, text="")
    hotelList.delete(*hotelList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Ссылка", "Название", "Удаленность", "Класс гостиницы", "Стоимость", "Питание", "        Номер        "]
    # строим таблицу по полученным данным
    hotelList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        hotelList.heading(col, text=col, anchor=CENTER,
            # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
            command = (lambda tree, i, f: (lambda: columnSort(tree, i, f)))(hotelList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        hotelList.column(f"#{i}", width=len(col) * 9, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    hotelList.pack(fill=BOTH, expand=0, padx=10, pady=[10, 10], anchor=NW)
    # при нажатии на строку таблицы гостиниц подгружаются данные по конкретной гостинице
    clickFunc = lambda e: selectHotel(hotelList, componentsH)
    # привязываем событие обработки нажатия на строку
    hotelList.bind("<<TreeviewSelect>>", clickFunc)

    # добавляем блок таблицы пассажиров на форму
    lfHotels.pack(anchor=NW, fill=BOTH, padx=10, pady=[0, 0])

    # выход в предыдущее меню
    clickFunc = lambda: createOperatorMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=10)
    btnBack.pack(fill=BOTH, padx=30, pady=10, ipadx=10, ipady=5)

    frMain.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=5)

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
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ОТЧЕТЫ ПО РАЗМЕЩЕННЫМ ПАССАЖИРАМ")
    lblMain.pack(pady=30)

    # -------------БЛОК таблицы-------------

    # создаем рамку таблицы пассажиров
    lfPassList = LabelFrame(frMain, font=consts.FNTLBLH2, text="Размещенные пассажиры", borderwidth=1, relief=SOLID)

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
    for col in passList["columns"]:
        passList.heading(col, text="")
    passList.delete(*passList.get_children())

    # список колонок будущей таблицы
    cols = [" № ", "Дата заявки", "     Диспетчер     ", "Номер рейса", "Пассажир",
            "Количество гостей", "   Гостиница   ", "   Номер   ", "  Дата заезда  ",
            "  Дата выезда  ", "Стоимость проживания"]
    # строим таблицу по полученным данным
    passList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        passList.heading(col, text=col, anchor=CENTER,
        # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
        command = (lambda tree, i, f: (lambda: columnSort(tree, i, f)))(passList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        passList.column(f"#{i}", width=len(col) * 6, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    passList.pack(fill=BOTH, expand=1, padx=5, pady=[10, 10])
    # добавляем таблицу на форму
    lfPassList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=[0, 10])

    # -------------БЛОК управления-------------

    # создаем рамку блока управления отчетом
    lfManageField = LabelFrame(frMain, font=consts.FNTLBLH2, text="Настройки отчета", borderwidth=1, relief=SOLID)

    # сетка компонентов 7x7
    createGrid(lfManageField, 7, 7, 1, 1)
    # массив компонентов управления данными
    components = []

    # всего затрачено средств
    lblSummaryCaption = Label(lfManageField, font=consts.FNTLBLH2, text="Затрачено за указанный период: ")
    lblSummaryCaption.grid(row=0, column=0, columnspan=3, rowspan=1, padx=10, pady=[10, 0], sticky=NW)
    lblSummary = Label(lfManageField, font=consts.FNTLBLH2, text="")
    lblSummary.grid(row=0, column=3, columnspan=1, rowspan=1, padx=0, pady=[10, 0], sticky=NW)
    # добавляем в массив компонентов текущий элемент
    components.append(lblSummary)

    # всего размещено пассажиров
    lblPassCountCaption = Label(lfManageField, font=consts.FNTLBLH2, text="Размещено пассажиров за указанный период: ")
    lblPassCountCaption.grid(row=1, column=0, columnspan=3, rowspan=1, padx=10, pady=[5, 0], sticky=NW)
    lblPassCount = Label(lfManageField, font=consts.FNTLBLH2, text="")
    lblPassCount.grid(row=1, column=3, columnspan=1, rowspan=1, padx=0, pady=[5, 0], sticky=NW)
    # добавляем в массив компонентов текущий элемент
    components.append(lblPassCount)

    # заголовок блока управления датой и временем
    lblDateTime = Label(lfManageField, font=consts.FNTLBLH2, text="Настроить диапазон:")
    lblDateTime.grid(row=2, column=0, columnspan=2, rowspan=1, padx=10, pady=[10, 0], sticky=N)

    # дата от
    lblDateFrom = Label(lfManageField, font=consts.FNTLBLS, text="Дата от:")
    lblDateFrom.grid(row=3, column=0, columnspan=1, padx=10, pady=[0, 0], sticky=E)

    # переменная для отслеживания изменения поля ввода
    etrDateFromVar = StringVar()
    etrDateFromVar.trace("w", lambda a, b, c: insertDataHotelToTable(db, passList, components, usrData["name"]))
    # текстовое поле дата ОТ
    etrDateFrom = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrDateFromVar)
    # значение по умолчанию для поля ввода
    etrDateFrom.insert(0, "YYYY-MM-DD")
    etrDateFrom.grid(row=4, column=0, columnspan=1, padx=20, pady=[0, 10], sticky=E)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateFrom)

    # дата до
    lblDateUntil = Label(lfManageField, font=consts.FNTLBLS, text="Дата до:")
    lblDateUntil.grid(row=5, column=0, columnspan=1, padx=10, pady=[0, 0], sticky=E)

    # переменная для отслеживания изменения поля ввода
    etrDateUntilVar = StringVar()
    etrDateUntilVar.trace("w", lambda a, b, c: insertDataHotelToTable(db, passList, components, usrData["name"]))
    # текстовое поле дата ДО
    etrDateUntil = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrDateUntilVar)
    # значение по умолчанию для поля ввода
    etrDateUntil.insert(0, "YYYY-MM-DD")
    etrDateUntil.grid(row=6, column=0, columnspan=1, padx=20, pady=[0, 10], sticky=E)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateUntil)

    # время от
    lblTimeFrom = Label(lfManageField, font=consts.FNTLBLS, text="Время от:")
    lblTimeFrom.grid(row=3, column=2, columnspan=1, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeFromVar = StringVar()
    etrTimeFromVar.trace("w", lambda a, b, c: insertDataHotelToTable(db, passList, components, usrData["name"]))
    # текстовое поле время ОТ
    etrTimeFrom = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrTimeFromVar)
    # значение по умолчанию для поля ввода
    etrTimeFrom.insert(0, "00:01")
    etrTimeFrom.grid(row=4, column=2, columnspan=1, padx=10, pady=[0, 10], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeFrom)

    # время до
    lblTimeUntil = Label(lfManageField, font=consts.FNTLBLS, text="Время до:")
    lblTimeUntil.grid(row=5, column=2, columnspan=1, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeUntilVar = StringVar()
    etrTimeUntilVar.trace("w", lambda a, b, c: insertDataHotelToTable(db, passList, components, usrData["name"]))
    # текстовое поле время ДО
    etrTimeUntil = Entry(lfManageField, font=consts.FNTLBLS, textvariable=etrTimeUntilVar)
    # значение по умолчанию для поля ввода
    etrTimeUntil.insert(0, "23:59")
    etrTimeUntil.grid(row=6, column=2, columnspan=2, padx=10, pady=[0, 10], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeUntil)

    # Гостиница
    lblHotel = Label(lfManageField, font=consts.FNTLBLS, text="Гостиница: ", padx=0, pady=0)
    lblHotel.grid(row=2, column=3, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    cbxHotelVar = StringVar()
    cbxHotelVar.trace("w", lambda a, b, c: insertDataHotelToTable(db, passList, components, usrData["name"]))
    # получаем список гостиниц
    hotelList = getHotel(db)
    # выпадающий список гостиниц
    cbxHotel = ttk.Combobox(lfManageField, values=["Все гостиницы", *hotelList], state="readonly",
                              textvar=cbxHotelVar)
    # устанавливаем значение по умолчанию
    cbxHotel.current(0)
    # устанавливаем позицию компонента в сетке
    cbxHotel.grid(row=3, column=3, columnspan=2, padx=15, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(cbxHotel)

    # наполняем таблицу данными при первом запуске
    insertDataHotelToTable(db, passList, components, usrData["name"])

    # сформировать отчет
    clickFunc = lambda: createReport(db, components, usrData["name"])
    btnCreateReport = Button(lfManageField, font=consts.FNTBTN, text="Сформировать отчет", command=clickFunc, padx=15, pady=10)
    btnCreateReport.grid(row=4, column=3, columnspan=2, rowspan=2, padx=0, pady=[10, 0], sticky=W)

    lfManageField.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=10)


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
