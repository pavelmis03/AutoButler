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
from funcs.funcsAnalystForm import *
# функции для работы с формами
from funcs.funcsForm import createGrid, createWindow
# константы
import consts

# создаем форму для работы менеджера - окно работы с бюджетом
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createManagerFinanceForm(db, root, usrData):
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
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="УПРАВЛЕНИЕ ФИНАНСАМИ")
    lblMain.pack(pady=[30, 10])

    # -------------БЛОК таблицы-------------


    # выход в предыдущее меню
    clickFunc = lambda: createManagerMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=10)
    btnBack.pack(fill=BOTH, padx=30, pady=20, ipadx=10, ipady=5)


    frMain.pack(fill=BOTH, padx=10, pady=20, ipadx=10, ipady=5)

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
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="СТАТИСТИКА И АНАЛИТИКА")
    lblMain.pack(pady=30)

    # -------------БЛОК таблицы-------------

    # создаем рамку таблицы логов
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
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="УПРАВЛЕНИЕ И УЧЕТ")
    lblMain.pack(pady=30)

    # создаем рамку для кнопок
    frBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Рабочие окна", borderwidth=1, relief=SOLID)

    # сетка компонентов 9x3
    createGrid(frBtns, 3, 9, 1, 1)

    # -------------БЛОК выбора окна-------------

    # прогнозирование
    clickFunc = lambda: createManagerFinanceForm(db, root, usrData)
    # прогнозирование
    btnForecastForm = Button(frBtns, font=consts.FNTBTN, text="Управление финансами", command=clickFunc, padx=25, pady=20)
    btnForecastForm.grid(row=1, column=1, rowspan=2, padx=15, pady=[35, 10])

    # аналитика рейсов
    clickFunc = lambda: createManagerAnalyticsForm(db, root, usrData)
    # аналитика рейсов
    btnFlightsForm = Button(frBtns, font=consts.FNTBTN, text="Статистика и аналитика", command=clickFunc, padx=43, pady=20)
    btnFlightsForm.grid(row=4, column=1, rowspan=2, padx=15, pady=[10, 10])

    # выход из пользователя
    btnLogOut = Button(frBtns, font=consts.FNTBTN, text="Сменить пользователя", padx=12, pady=20,
                       command=lambda: fAuth.logOut(db, root))
    btnLogOut.grid(row=7, column=1, rowspan=2, padx=15, pady=[10, 35])

    # добавляем раздел на форму
    frBtns.pack(anchor=NW, fill=BOTH, padx=15, pady=[0, 10])

    frMain.pack(fill=BOTH, padx=5, pady=5, ipadx=10, ipady=10)

    root.mainloop()