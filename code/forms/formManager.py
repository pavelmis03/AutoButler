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
from funcs.funcsManagerForm import *
# функции для работы с формами
from funcs.funcsForm import createGrid, createWindow
# константы
import consts
from openai.types.beta.threads import text


# создаем форму для работы менеджера - окно работы с бюджетом
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createManagerFinanceForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 1270
    h = 800
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250, marginy=0)

    # создаем основную рамку
    frMain = Frame(borderwidth=2, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="УПРАВЛЕНИЕ БЮДЖЕТОМ")
    lblMain.pack(pady=[10, 0])

    # -------------БЛОК таблицы-------------

    # основной заголовок
    lfReqList = LabelFrame(frMain, width=300, font=consts.FNTLBLH2, text="Подтверждение заявок", borderwidth=1, relief=SOLID)

    # переменные картинок для чекбоксов картинок
    im_checked = ImageTk.PhotoImage(Image.open("static/icons/cbx_checked.png"))
    im_unchecked = ImageTk.PhotoImage(Image.open("static/icons/cbx_unchecked.png"))

    # строим таблицу по полученным данным
    reqList = ttk.Treeview(lfReqList, columns=[], height=5)
    # добавляем стили для чек боксов
    style = ttk.Style(reqList)
    style.configure("Treeview", rowheight=15)
    # настраиваем картинку для выбранной и не выбранной ячейки
    reqList.tag_configure("checked", image=im_checked)
    reqList.tag_configure("unchecked", image=im_unchecked)


    # создаем полосы прокрутки для таблицы
    scrlV = Scrollbar(lfReqList, orient="vertical", command=reqList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = Scrollbar(lfReqList, orient="horizontal", command=reqList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    reqList["yscrollcommand"] = scrlV.set
    reqList["xscrollcommand"] = scrlH.set

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    reqList.pack(fill=NONE, expand=0, padx=10, pady=[10, 10], anchor=NW)

    # очищаем таблицу перед наполнением
    for col in reqList["columns"]:
        reqList.heading(col, text="")
    reqList.delete(*reqList.get_children())

    # список колонок будущей таблицы
    cols = [" № ", "  Дата заявки  ", "   Пассажир   ", "Количество гостей", "   Рейс   ", "   Исполнитель   ", "        Отель        ",
            "        Номер        ", "Стоимость", "  Дата заезда  ", "  Дата выезда  ", "  Ссылка  "]
    # строим таблицу по полученным данным
    reqList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        reqList.heading(col, text=col, anchor=CENTER,
                         # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
                         command=(lambda tree, i, f: (lambda: columnSort(tree, i, f)))(reqList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        reqList.column(f"#{i}", width=len(col) * 9, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # функция обработки нажатия на ячейку
    clickFunc = lambda e: toggleCheck(reqList, e)
    # привязываем событие нажатия на кнопку
    reqList.bind("<Double 1>", clickFunc)

    # добавляем блок таблицы пассажиров на форму
    lfReqList.pack(anchor=NW, fill=BOTH, padx=10, pady=[0, 5])


    # -------------БЛОК ИНФОРМАЦИИ-------------

    # создаем рамку информации
    frMiddle = Frame(frMain, borderwidth=1, relief=SOLID)

    # сетка компонентов 8x10
    createGrid(frMiddle, 10, 8, 1, 1)

    # СТОЛБЕЦ 1

    # выделенный бюджет надпись
    lblBudgetText = Label(frMiddle, font=consts.FNTLBLH3, text="Выделенный бюджет на период:")
    lblBudgetText.grid(row=0, column=0, columnspan=3, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # планируемые расходы надпись
    lblExpText = Label(frMiddle, font=consts.FNTLBLH3, text="Планируемые расходы:")
    lblExpText.grid(row=1, column=0, columnspan=3, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # сальдо надпись
    lblBalanceText = Label(frMiddle, font=consts.FNTLBLH3, text="Сальдо:")
    lblBalanceText.grid(row=2, column=0, columnspan=3, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # период
    lblPeriod = Label(frMiddle, font=consts.FNTLBLH3, text="Период:")
    lblPeriod.grid(row=4, column=0, columnspan=1, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список длины периода
    cbxPeriod = ttk.Combobox(frMiddle, values=["Все", "5 лет", "1 год", "6 месяцев", "1 месяц", "1 неделя", "1 день"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxPeriod.current(0)
    # устанавливаем позицию компонента в сетке
    cbxPeriod.grid(row=5, column=0, columnspan=1, rowspan=1, padx=12, pady=[5, 0], sticky=NW)

    # ответственный оператор
    lblBalanceText = Label(frMiddle, font=consts.FNTLBLH3, text="Ответсвенный оператор:")
    lblBalanceText.grid(row=6, column=0, columnspan=2, rowspan=1, padx=10, pady=[10, 10], sticky=W)

    # СТОЛБЕЦ 2

    # выделенный бюджет
    lblBudget = Label(frMiddle, font=consts.FNTLBLH3, text="в процессе")
    lblBudget.grid(row=0, column=3, columnspan=1, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # планируемые расходы
    lblExp = Label(frMiddle, font=consts.FNTLBLH3, text="в процессе")
    lblExp.grid(row=1, column=3, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # сальдо
    lblBalance = Label(frMiddle, font=consts.FNTLBLH3, text="в процессе")
    lblBalance.grid(row=2, column=3, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # ответственный оператор
    lblBalance = Label(frMiddle, font=consts.FNTLBLH3, text="в процессе")
    lblBalance.grid(row=6, column=2, columnspan=2, rowspan=1, padx=10, pady=[10, 10], sticky=W)

    # СТОЛБЕЦ 3

    # план размещения пассажиров надпись
    lblPlanText = Label(frMiddle, font=consts.FNTLBLH3, text="План размещения пассажиров:")
    lblPlanText.grid(row=0, column=4, columnspan=3, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # ожидаемое количество надпись
    lblFactText = Label(frMiddle, font=consts.FNTLBLH3, text="Фактическое количество:")
    lblFactText.grid(row=1, column=4, columnspan=3, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # расхождение надпись
    lblDiffText = Label(frMiddle, font=consts.FNTLBLH3, text="Расхождение:")
    lblDiffText.grid(row=2, column=4, columnspan=3, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # номер периода
    lblPeriodNum = Label(frMiddle, font=consts.FNTLBLH3, text="Номер периода:")
    lblPeriodNum.grid(row=4, column=4, columnspan=1, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список длины периода
    cbxPeriodNum = ttk.Combobox(frMiddle, values=["Не найдено периодов"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxPeriodNum.current(0)
    # устанавливаем позицию компонента в сетке
    cbxPeriodNum.grid(row=5, column=4, columnspan=1, rowspan=1, padx=12, pady=[5, 0], sticky=NW)

    # СТОЛБЕЦ 4

    # план размещения пассажиров
    lblPlan = Label(frMiddle, font=consts.FNTLBLH3, text="в процессе")
    lblPlan.grid(row=0, column=7, columnspan=3, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # ожидаемое количество
    lblFact = Label(frMiddle, font=consts.FNTLBLH3, text="в процессе")
    lblFact.grid(row=1, column=7, columnspan=3, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # расхождение
    lblDiff = Label(frMiddle, font=consts.FNTLBLH3, text="в процессе")
    lblDiff.grid(row=2, column=7, columnspan=3, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # СТОЛБЕЦ 5

    # выбрать все
    clickFunc = lambda: selectAll(True)
    btnSelectAll = Button(frMiddle, font=consts.FNTBTN, text="Выбрать все", command=clickFunc, padx=37, pady=10)
    btnSelectAll.grid(row=0, column=9, columnspan=2, rowspan=2, padx=10, pady=[10, 0], sticky=W)

    # снять все
    clickFunc = lambda: selectAll(True)
    btnUnSelectAll = Button(frMiddle, font=consts.FNTBTN, text="Снять выделение", command=clickFunc, padx=20, pady=10)
    btnUnSelectAll.grid(row=2, column=9, columnspan=2, rowspan=2, padx=10, pady=[10, 0], sticky=W)

    # зафиксировать изменения
    clickFunc = lambda: saveSelection(True)
    btnSaveSelection = Button(frMiddle, font=consts.FNTBTN, text="Зафиксировать\nизменения", command=clickFunc, padx=33, pady=10)
    btnSaveSelection.grid(row=4, column=9, columnspan=2, rowspan=2, padx=10, pady=[10, 0], sticky=W)


    frMiddle.pack(anchor=NW, fill=BOTH, padx=10, pady=[0, 5])

    # -------------БЛОК НИЖНЕЙ ЧАСТИ-------------

    # создаем рамку нижней части с фильтрами и таблицей продуктивности операторов
    frBottom = Frame(frMain, borderwidth=1, relief=SOLID)

    # сетка компонентов 1x6
    createGrid(frBottom, 6, 1, 1, 1)

    # -------------БЛОК ФИЛЬТРОВ-------------
    lfFilters = LabelFrame(frBottom, width=300, font=consts.FNTLBLH2, text="Фильтры", borderwidth=1,
                            relief=SOLID)

    # сетка компонентов 8x1
    createGrid(lfFilters, 1, 8, 1, 1)

    # гостиница
    lblHotelFilter = Label(lfFilters, font=consts.FNTLBLH3, text="Гостиница:")
    lblHotelFilter.grid(row=0, column=0, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=W)
    # выпадающий список гостиниц
    cbxHotelFilter = ttk.Combobox(lfFilters, values=["Гостиниц не найдено"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxHotelFilter.current(0)
    # устанавливаем позицию компонента в сетке
    cbxHotelFilter.grid(row=1, column=0, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # Компания
    lblCompanyFilter = Label(lfFilters, font=consts.FNTLBLH3, text="Компания:")
    lblCompanyFilter.grid(row=2, column=0, columnspan=1, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список компаний
    cbxCompanyFilter = ttk.Combobox(lfFilters, values=["Компаний не найдено"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxCompanyFilter.current(0)
    # устанавливаем позицию компонента в сетке
    cbxCompanyFilter.grid(row=3, column=0, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # Аэропорт вылета
    lblAirportDep = Label(lfFilters, font=consts.FNTLBLH3, text="Аэропорт вылета:")
    lblAirportDep.grid(row=4, column=0, columnspan=1, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список компаний
    cbxAirportDep = ttk.Combobox(lfFilters, values=["Аэропортов не найдено"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxAirportDep.current(0)
    # устанавливаем позицию компонента в сетке
    cbxAirportDep.grid(row=5, column=0, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # Аэропорт посадки
    lblAirportArr = Label(lfFilters, font=consts.FNTLBLH3, text="Аэропорт посадки:")
    lblAirportArr.grid(row=6, column=0, columnspan=1, rowspan=1, padx=10, pady=[10, 0], sticky=W)
    # выпадающий список компаний
    cbxAirportArr = ttk.Combobox(lfFilters, values=["Аэропортов не найдено"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxAirportArr.current(0)
    # устанавливаем позицию компонента в сетке
    cbxAirportArr.grid(row=7, column=0, columnspan=1, rowspan=1, padx=10, pady=[5, 10], sticky=NW)

    # добавляем блок фильтров на форму
    lfFilters.grid(row=0, column=0, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # -------------БЛОК ТАБЛИЦЫ ПРОДУКТИВНОСТИ-------------
    # основной заголовок
    lfOperList = LabelFrame(frBottom, width=300, font=consts.FNTLBLH2, text="Продуктивность операторов", borderwidth=1,
                           relief=SOLID)

    # строим таблицу по полученным данным
    operList = ttk.Treeview(lfOperList, columns=[], show="headings", height=5)

    # создаем полосы прокрутки для таблицы
    scrlV = Scrollbar(lfOperList, orient="vertical", command=operList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = Scrollbar(lfOperList, orient="horizontal", command=operList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    operList["yscrollcommand"] = scrlV.set
    operList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in operList["columns"]:
        operList.heading(col, text="")
    operList.delete(*operList.get_children())

    # список колонок будущей таблицы
    cols = [" № ", "    Оператор    ", "Количество заявок", "Из них принято", "Процент принятых", "Премия    ",]
    # строим таблицу по полученным данным
    operList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        operList.heading(col, text=col, anchor=CENTER,
                        # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
                        command=(lambda tree, i, f: (lambda: columnSort(tree, i, f)))(operList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        operList.column(f"#{i}", width=len(col) * 9, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, reqList, operList)

    # выделяем первую строку
    reqList.selection_add(0)

    # добавляем, растягивая по ширине элементы и заполняя контейнер
    operList.pack(fill=NONE, expand=0, padx=10, pady=[10, 10], anchor=NW)
    # добавляем блок таблицы пассажиров на форму
    lfOperList.grid(row=0, column=1, columnspan=4, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # -------------БЛОК графика-------------
    lfGraph = LabelFrame(frBottom, width=300, font=consts.FNTLBLH2, text="График", borderwidth=1,
                           relief=SOLID)

    # сетка компонентов 1x6
    createGrid(lfGraph, 6, 1, 1, 1)

    # сформировать график
    clickFunc = lambda: createGraph()
    btnCreateGraph = Button(lfGraph, font=consts.FNTBTNMINI, text="Сформировать график", command=clickFunc, padx=20, pady=2)
    btnCreateGraph.grid(row=0, column=0, columnspan=1, rowspan=1, padx=10, pady=[5, 0], sticky=W)

    # кнопки выбора того, что будет на графике
    lblCheckBox = Label(lfGraph, font=consts.FNTLBLH2, text="Отобразить:")
    lblCheckBox.grid(row=1, column=0, columnspan=2, rowspan=1, padx=10, pady=[5, 0], sticky=NW)

    # переменная для отслеживания изменения чекбокса
    cbtnExpPlanVar = IntVar()
    cbtnExpPlan = Checkbutton(lfGraph, font=consts.FNTBTN, text="Расходы (план)", variable=cbtnExpPlanVar, padx=15, pady=0)
    cbtnExpPlan.grid(row=2, column=0, columnspan=1, rowspan=1, padx=0, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения чекбокса
    cbtnExpFactVar = IntVar()
    cbtnExpFact = Checkbutton(lfGraph, font=consts.FNTBTN, text="Расходы (факт)", variable=cbtnExpFactVar, padx=15, pady=0)
    cbtnExpFact.grid(row=3, column=0, columnspan=1, rowspan=1, padx=0, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения чекбокса
    cbtnPassPlanVar = IntVar()
    cbtnPassPlan = Checkbutton(lfGraph, font=consts.FNTBTN, text="Пассажиры (план)", variable=cbtnPassPlanVar, padx=15, pady=0)
    cbtnPassPlan.grid(row=4, column=0, columnspan=1, rowspan=1, padx=0, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения чекбокса
    cbtnPassFactVar = IntVar()
    cbtnPassFact = Checkbutton(lfGraph, font=consts.FNTBTN, text="Пассажиры (факт)", variable=cbtnPassFactVar, padx=15, pady=0)
    cbtnPassFact.grid(row=5, column=0, columnspan=1, rowspan=1, padx=0, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения чекбокса
    cbtnReqCntVar = IntVar()
    cbtnReqCnt = Checkbutton(lfGraph, font=consts.FNTBTN, text="Количество заявок", variable=cbtnReqCntVar, padx=15, pady=0)
    cbtnReqCnt.grid(row=6, column=0, columnspan=1, rowspan=1, padx=0, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения чекбокса
    cbtnSaveGraphVar = IntVar()
    cbtnSaveGraph = Checkbutton(lfGraph, font=consts.FNTBTN, text="Сохранить график", variable=cbtnSaveGraphVar, padx=15, pady=5)
    cbtnSaveGraph.grid(row=7, column=0, columnspan=1, rowspan=1, padx=0, pady=[0, 0], sticky=W)

    # добавляем блок графиков на форму
    lfGraph.grid(row=0, column=5, columnspan=1, rowspan=1, padx=10, pady=[5, 5], sticky=NW)

    # добавляем блок нижних компонентов на форму
    frBottom.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=5)


    # выход в предыдущее меню
    clickFunc = lambda: createManagerMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=5)
    btnBack.pack(fill=BOTH, padx=30, pady=5, ipadx=10, ipady=15)


    frMain.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=5)

    root.mainloop()

# окно для просмотра аналитики: сколько людей размещено, сколько рейсов отменено,
# сколько отчетов было сделано другими пользователями
def createManagerAnalyticsForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 1270
    h = 1000
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=2, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="СТАТИСТИКА И АНАЛИТИКА")
    lblMain.pack(pady=30)

    # -------------БЛОК таблицы-------------





    # выход в предыдущее меню
    clickFunc = lambda: createManagerMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=5)
    btnBack.pack(fill=BOTH, padx=30, pady=5, ipadx=10, ipady=10)

    frMain.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=10)

    root.mainloop()

# создаем форму для работы аналитика - выбор рабочего окна
def createManagerMainForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 570
    h = 620
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=2, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="УПРАВЛЕНИЕ И УЧЕТ")
    lblMain.pack(pady=30)

    # создаем рамку для кнопок
    frBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Рабочие окна", borderwidth=1, relief=SOLID)

    # сетка компонентов 9x3
    createGrid(frBtns, 3, 9, 1, 1)

    # -------------БЛОК выбора окна-------------

    # управление финансами
    clickFunc = lambda: createManagerFinanceForm(db, root, usrData)
    btnForecastForm = Button(frBtns, font=consts.FNTBTN, text="Управление финансами", command=clickFunc, padx=25, pady=20)
    btnForecastForm.grid(row=1, column=1, rowspan=2, padx=15, pady=[35, 10])

    # аналитика
    clickFunc = lambda: createManagerAnalyticsForm(db, root, usrData)
    btnFlightsForm = Button(frBtns, font=consts.FNTBTN, text="Статистика и аналитика", command=clickFunc, padx=25, pady=20)
    btnFlightsForm.grid(row=4, column=1, rowspan=2, padx=15, pady=[10, 10])

    # выход из пользователя
    btnLogOut = Button(frBtns, font=consts.FNTBTN, text="Сменить пользователя", padx=28, pady=20,
                       command=lambda: fAuth.logOut(db, root))
    btnLogOut.grid(row=7, column=1, rowspan=2, padx=15, pady=[10, 35])

    # добавляем раздел на форму
    frBtns.pack(anchor=NW, fill=BOTH, padx=15, pady=[0, 10])

    frMain.pack(fill=BOTH, padx=5, pady=5, ipadx=10, ipady=10)

    root.mainloop()