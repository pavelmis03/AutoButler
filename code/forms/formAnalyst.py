# библиотека графических элементов для
from tkinter import *
# дополнительные виджеты
from tkinter import ttk
# шрифты
from tkinter import font
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
from funcs.funcsAnalystForm import *
# функции для работы с формами
from funcs.funcsForm import createGrid, createWindow
# константы
import consts

# создаем форму для работы Админа с пользователями
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}

# создаем форму для работы Админа - окно вывода ошибок
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createAnalystFlightsForm(db, root, usrData):
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
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ДАННЫЕ ПО РЕЙСАМ")
    lblMain.pack(pady=10)

    # -------------БЛОК таблицы-------------

    # создаем рамку таблицы логов
    lfFlyList = LabelFrame(frMain, font=consts.FNTLBLH2, text="Список рейсов", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    flyList = ttk.Treeview(lfFlyList, columns=[], show="headings", height=8)

    # создаем полосы прокрутки для таблицы
    scrlV = ttk.Scrollbar(lfFlyList, orient="vertical", command=flyList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = ttk.Scrollbar(lfFlyList, orient="horizontal", command=flyList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    flyList["yscrollcommand"] = scrlV.set
    flyList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in flyList['columns']:
        flyList.heading(col, text='')
    flyList.delete(*flyList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Номер рейса", "Авиакомпания", "Аэропорт вылета", "Аэропорт прибытия", "Плановое время вылета", "Плановое время прибытия", "Фактическое время вылета", "Фактическое время прибытия", "Статус", "Минуты задержки", "Причина отмены"]
    # строим таблицу по полученным данным
    flyList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        flyList.heading(col, text=col, anchor=CENTER)
        # выравнивание по центру для данных в ячейках
        flyList.column(f"#{i}", anchor=CENTER)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, flyList)

    # добавляем, растягивая по ширине элементы и заполняя контэйнер
    flyList.pack(fill=BOTH, expand=1, padx=5, pady=[5, 10])
    # добавляем таблицу на форму
    lfFlyList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=5)

    # -------------БЛОК построения графика-------------

    # создаем рамку для графика
    frGraph = LabelFrame(frMain, font=consts.FNTLBLH2, text="График", borderwidth=1, relief=SOLID)



    frGraph.pack(fill=BOTH, padx=10, pady=5, ipadx=3)


    # -------------БЛОК кнопок управления графиком-------------

    # создаем рамку для кнопок
    frManageBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Настрока отображения графика", borderwidth=1, relief=SOLID)

    # сетка компонентов 12x8
    createGrid(frManageBtns, 12, 8, 1, 1)

            # -------------ЭЛЕМЕНТЫ управления ДАТОЙ И ВРЕМЕНЕМ-------------
    # дата от
    lblDateFrom = Label(frManageBtns, font=consts.FNTLBLS, text="Дата от:", padx=0, pady=0)
    lblDateFrom.grid(row=0, column=0, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # текстовое поле дата ОТ
    etrDateFrom = Entry(frManageBtns, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrDateFrom.insert(0, "YYYY-MM-DD")
    etrDateFrom.grid(row=1, column=0, columnspan=1, padx=10, pady=[0, 0], sticky=W)

    # дата до
    lblDateUntil = Label(frManageBtns, font=consts.FNTLBLS, text="Дата до:", padx=0, pady=0)
    lblDateUntil.grid(row=2, column=0, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # текстовое поле дата ДО
    etrDateUntil = Entry(frManageBtns, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrDateUntil.insert(0, "YYYY-MM-DD")
    etrDateUntil.grid(row=3, column=0, columnspan=1, padx=10, pady=[0, 0], sticky=W)

    # время от
    lblTimeFrom = Label(frManageBtns, font=consts.FNTLBLS, text="Время от:", padx=0, pady=0)
    lblTimeFrom.grid(row=0, column=2, columnspan=2, padx=0, pady=[10, 0], sticky=W)

    # текстовое поле время ОТ
    etrTimeFrom = Entry(frManageBtns, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrTimeFrom.insert(0, "00:01")
    etrTimeFrom.grid(row=1, column=2, columnspan=1, padx=0, pady=[0, 0], sticky=W)

    # время до
    lblTimeUntil = Label(frManageBtns, font=consts.FNTLBLS, text="Время до:", padx=0, pady=0)
    lblTimeUntil.grid(row=2, column=2, columnspan=2, padx=0, pady=[0, 0], sticky=W)

    # текстовое поле время ДО
    etrTimeUntil = Entry(frManageBtns, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrTimeUntil.insert(0, "23:59")
    etrTimeUntil.grid(row=3, column=2, columnspan=1, padx=0, pady=[0, 0], sticky=W)

        # -------------ЭЛЕМЕНТЫ управления ВЫЛЕТОМ И ПРИЗЕМЛЕНИЕМ-------------

    # вылет (опоздание или нет)
    lblDep = Label(frManageBtns, font=consts.FNTLBLS, text="Вылет:")
    lblDep.grid(row=0, column=4, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # группа для radioBtns
    workModeDep = StringVar(value="allDep")
    # изменение поиска все, опоздавшие, вылетевшие по расписанию
    clickFunc = lambda: changeWorkMode(workModeDep)
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
    # изменение поиска все, опоздавшие, вылетевшие по расписанию
    clickFunc = lambda: changeWorkMode(workModeArr)
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
    radioScheduleArr.grid(row=7, column=4, rowspan=1, padx=15, pady=[0, 10], sticky=W)

        # -------------ЭЛЕМЕНТЫ управления КОМПАНИЕЙ И СТАТУСОМ-------------

    # компания
    lblCompany = Label(frManageBtns, font=consts.FNTLBLS, text="Авиакомпания: ", padx=0, pady=0)
    lblCompany.grid(row=0, column=5, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # получаем список авиакомпаний
    companyList = getCompany(db)
    # выпадающий список компаний
    cbxCompany = ttk.Combobox(frManageBtns, values=["Все компании", *companyList], state="readonly")
    # устанавливаем значение по умолчанию
    cbxCompany.current(0)
    # устанавливаем позицию компонента в сетке
    cbxCompany.grid(row=1, column=5, padx=15, pady=[0, 0], sticky=W)

    # статус рейса
    lblStatus = Label(frManageBtns, font=consts.FNTLBLS, text="Статус рейса: ", padx=0, pady=0)
    lblStatus.grid(row=2, column=5, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # выпадающий список статусов
    cbxStatus = ttk.Combobox(frManageBtns, values=["Все варианты", "Отменен", "Открыта регистрация", "Открыта посадка",
                                                 "Вылет задерживается", "Регистрация завершена", "Посадка закончена",
                                                 "Вылет состоялся", "Посадка задерживается", "Прибыл"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxStatus.current(0)
    # устанавливаем позицию компонента в сетке
    cbxStatus.grid(row=3, column=5, padx=15, pady=[0, 0], sticky=W)


        # -------------ЭЛЕМЕНТЫ управления АЭРОПОРТОМ-------------

    # аэропорт вылета
    lblAirportDep = Label(frManageBtns, font=consts.FNTLBLS, text="Аэропорт вылета: ", padx=0, pady=0)
    lblAirportDep.grid(row=0, column=6, columnspan=2, padx=10, pady=[10, 0], sticky=W)

    # получаем список аэропортов отправления
    airportList = getAirport(db, "dep")
    # выпадающий список аэропортов
    cbxAirportDep = ttk.Combobox(frManageBtns, values=["Все аэропорты", *airportList], state="readonly")
    # устанавливаем значение по умолчанию
    cbxAirportDep.current(0)
    # устанавливаем позицию компонента в сетке
    cbxAirportDep.grid(row=1, column=6, padx=15, pady=[0, 0], sticky=W)

    # аэропорт приземления
    lblAirportArr = Label(frManageBtns, font=consts.FNTLBLS, text="Аэропорт посадки: ", padx=0, pady=0)
    lblAirportArr.grid(row=2, column=6, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # получаем список аэропортов отправления
    airportList = getAirport(db, "arr")
    # выпадающий список аэропортов
    cbxAirportArr = ttk.Combobox(frManageBtns, values=["Все аэропорты", *airportList], state="readonly")
    # устанавливаем значение по умолчанию
    cbxAirportArr.current(0)
    # устанавливаем позицию компонента в сетке
    cbxAirportArr.grid(row=3, column=6, padx=15, pady=[0, 10], sticky=W)


        # -------------КНОПКИ управления-------------

    # сформировать отчет
    clickFunc = lambda: createReport(db, etrDateFrom.get(), etrDateUntil.get(), etrTimeFrom.get(), etrTimeUntil.get(),
                                     workModeDep, workModeArr, cbxCompany.get(), cbxStatus.get(), cbxAirportDep.get(), cbxAirportArr.get())
    btnCreateReport = Button(frManageBtns, font=consts.FNTBTN, text="Сформировать отчет", command=clickFunc, padx=15, pady=10)
    btnCreateReport.grid(row=0, column=7, columnspan=2, rowspan=2, padx=0, pady=[10, 0])

    # сформировать график
    clickFunc = lambda: createGraph(db, etrDateFrom.get(), etrDateUntil.get(), etrTimeFrom.get(), etrTimeUntil.get(),
                                    workModeDep, workModeArr, cbxCompany.get(), cbxStatus.get(), cbxAirportDep.get(), cbxAirportArr.get())
    btnCreateGraph = Button(frManageBtns, font=consts.FNTBTN, text="Сформировать график", command=clickFunc, padx=9, pady=10)
    btnCreateGraph.grid(row=2, column=7, columnspan=2, rowspan=2, padx=0, pady=[0, 0])

    # сохранить график
    clickFunc = lambda: saveGraph()
    btnSaveGraph = Button(frManageBtns, font=consts.FNTBTN, text="Сохранить график", command=clickFunc, padx=26, pady=10)
    btnSaveGraph.grid(row=4, column=7, columnspan=2, rowspan=2, padx=0, pady=[0, 0])

    # массив радио-кнопок
    # radioBtnArr = [radioAllDep, radioDelayDep, radioScheduleDep, radioAllArr, radioDelayArr, radioScheduleArr]
    # массив комбобоксов
    cbxArr = [cbxCompany, cbxStatus, cbxAirportDep, cbxAirportArr]
    # сбросить настройки
    # clickFunc = lambda: resetSettings(etrDateFrom, etrDateUntil, etrTimeFrom, etrTimeUntil, radioBtnArr, cbxArr)
    clickFunc = lambda: resetSettings(etrDateFrom, etrDateUntil, etrTimeFrom, etrTimeUntil, workModeDep, workModeArr, cbxArr)
    btnResetSettings = Button(frManageBtns, font=consts.FNTBTN, text="Сбросить настройки", command=clickFunc, padx=20, pady=10)
    btnResetSettings.grid(row=6, column=7, columnspan=2, rowspan=2, padx=0, pady=[0, 10])



    frManageBtns.pack(fill=BOTH, padx=10, pady=5, ipadx=3)

    # выход в предыдущее меню
    clickFunc = lambda: createAnalystMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=5)
    btnBack.pack(fill=BOTH, padx=30, pady=5, ipadx=10, ipady=5)


    frMain.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=5)

    root.mainloop()

def createAnalystForecastForm(db, root, usrData):
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
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="ПРОГНОЗИРОВАНИЕ И АНАЛИТИКА")
    lblMain.pack(pady=30)

    # -------------БЛОК таблицы-------------

    # выход в предыдущее меню
    clickFunc = lambda: createAnalystMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=5)
    btnBack.pack(fill=BOTH, padx=30, pady=5, ipadx=10, ipady=10)

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