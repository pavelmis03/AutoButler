# библиотека графических элементов для
from tkinter import *
# дополнительные виджеты
from tkinter import ttk
# шрифты
from tkinter import font
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
from funcs import *
# функции для работы с формами
from funcsForm import *
# константы
import consts


# создаем форму для работы механика
def createMainForm(db, usrData):
    # ширина и высота окна
    w = 700
    h = 750
    # имя пользователя
    usrName = usrData[0]
    usrRegList = usrData[1]
    usrCars = usrData[2]
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrName}!", w=w, h=h, marginx=250, marginy=10)

    # -------------ВЕРХНЕЕ МЕНЮ-------------

    # создаем рамку основного блока
    frTopMenu = Frame(borderwidth=0, relief=SOLID, width=w)

    # создаем сетку для верхнего меню
    frTopMenu.columnconfigure(index=0, weight=1)
    frTopMenu.columnconfigure(index=1, weight=2)  # отступ
    frTopMenu.columnconfigure(index=2, weight=5)  # надпись
    frTopMenu.columnconfigure(index=3, weight=2)  # отступ
    frTopMenu.columnconfigure(index=4, weight=1)  # настройки
    for c in range(1):
        frTopMenu.rowconfigure(index=0, weight=1)

    # подпись для имени пользователя
    lblusrName = Label(frTopMenu, text="ГЛАВНОЕ МЕНЮ", font=("Arial", 18))
    # добавление элемента на форму
    lblusrName.grid(row=0, column=2, padx=50)

    # функция обработки нажатия на кнопку
    clickFunc = lambda event: createSetForm(db, usrData, root)
    img = Image.open("../static/icons/btnSet.png")
    img = ImageTk.PhotoImage(img)
    btnSet = Button(frTopMenu, image=img, compound=TOP)
    # устанавливаем картинку кнопке
    btnSet.image = img
    btnSet.grid(row=0, column=4, padx=0)
    # привязываем событие нажатия на кнопку
    # btnSet.bind("<ButtonPress-1>", clickFunc)

    frTopMenu.pack(ipadx=100, padx=0, pady=10)

    # -------------ТАБЛИЦА ЗАПИСЕЙ-------------

    # создаем рамку для таблицы записей
    frRegList = Frame(borderwidth=1, relief=SOLID, width=w)

    # создаем рамку для выбора таблицы
    lFRegList = LabelFrame(frRegList, text="", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    regList = ttk.Treeview(lFRegList, columns=[], show="headings", height=4)

    # создаем полосы прокрутки для таблицы
    scrlV = ttk.Scrollbar(lFRegList, orient="vertical", command=regList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = ttk.Scrollbar(lFRegList, orient="horizontal", command=regList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    regList["yscrollcommand"] = scrlV.set
    regList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in regList['columns']:
        regList.heading(col, text='')
    regList.delete(*regList.get_children())

    # список колонок будущей таблицы
    cols = ["№ Записи", "Транспортное средство", "Дата записи"]
    # строим таблицу по полученным данным
    regList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        regList.heading(col, text=col, anchor=CENTER)
        # выравнивание по центру для данных в ячейках
        regList.column(f"#{i}", anchor=CENTER)
        i += 1

    # добавляем данные в таблицу из dataFrame
    i = 1
    for row in usrRegList:
        regList.insert("", END, values=tuple([i, *row[:]]))
        i += 1

    # добавляем, растягивая по ширине элементы и заполняя контэйнер
    regList.pack(fill=BOTH, expand=1, padx=5, pady=[5, 10])
    # добавляем таблицу на форму
    lFRegList.pack(anchor=NW, fill=BOTH, expand=True, padx=8, pady=10)
    # добавляем frame на форму
    frRegList.pack(ipadx=10, padx=0, pady=10)

    # -------------ТАБЛИЦА ТС-------------

    # создаем рамку для таблицы записей
    frCarList = Frame(borderwidth=1, relief=SOLID, width=w)

    # создаем рамку для выбора таблицы
    lFCarList = LabelFrame(frCarList, text="", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    carList = ttk.Treeview(lFCarList, columns=[], show="headings", height=4)

    # создаем полосы прокрутки для таблицы
    scrlV = ttk.Scrollbar(lFCarList, orient="vertical", command=carList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = ttk.Scrollbar(lFCarList, orient="horizontal", command=carList.xview)
    scrlH.pack(side=BOTTOM, fill=X)
    # привязка полос прокрутки к таблице
    carList["yscrollcommand"] = scrlV.set
    carList["xscrollcommand"] = scrlH.set

    # очищаем таблицу перед наполнением
    for col in carList['columns']:
        carList.heading(col, text='')
    carList.delete(*carList.get_children())

    # список колонок будущей таблицы
    cols = ["№ ТС", "Транспортное средство", "Количество записей"]
    # строим таблицу по полученным данным
    carList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        carList.heading(col, text=col, anchor=CENTER)
        # выравнивание по центру для данных в ячейках
        carList.column(f"#{i}", anchor=CENTER)
        i += 1

    # добавляем данные в таблицу из dataFrame
    i = 1
    for row in usrCars:
        carList.insert("", END, values=tuple([i, *row[:2]]))
        i += 1

    # добавляем, растягивая по ширине элементы и заполняя контэйнер
    carList.pack(fill=BOTH, expand=1, padx=5, pady=[5, 10])
    # добавляем таблицу на форму
    lFCarList.pack(anchor=NW, fill=BOTH, expand=True, padx=8, pady=10)
    # добавляем frame на форму
    frCarList.pack(ipadx=10, padx=0, pady=10)

    # ------------НИЖНЕЕ МЕНЮ-------------

    # создаем рамку основного блока
    frBottomMenu = Frame(borderwidth=1, relief=SOLID, width=w)

    # создаем сетку для верхнего меню
    for c in range(5):
        frBottomMenu.columnconfigure(index=c, weight=1)
    for c in range(1):
        frBottomMenu.rowconfigure(index=c, weight=1)

    # функция обработки нажатия на кнопку
    clickFunc = lambda event: createRegForm(db, usrData, root)
    img = Image.open("../static/icons/btnReg.png")
    img = ImageTk.PhotoImage(img)
    btnReg = Button(frBottomMenu, image=img, compound=TOP)
    # устанавливаем картинку кнопке
    btnReg.image = img
    btnReg.grid(row=0, column=0, padx=0)
    # привязываем событие нажатия на кнопку
    btnReg.bind("<ButtonPress-1>", clickFunc)

    # функция обработки нажатия на кнопку
    clickFunc = lambda event: createRegListForm(db, usrData, root)
    img = Image.open("../static/icons/btnLists.png")
    img = ImageTk.PhotoImage(img)
    btnListReg = Button(frBottomMenu, image=img, compound=TOP)
    # устанавливаем картинку кнопке
    btnListReg.image = img
    btnListReg.grid(row=0, column=1, padx=0)
    # привязываем событие нажатия на кнопку
    btnListReg.bind("<ButtonPress-1>", clickFunc)

    # функция обработки нажатия на кнопку
    clickFunc = lambda event: createStatisticForm(db, usrData, root)
    img = Image.open("../static/icons/btnStatistic.png")
    img = ImageTk.PhotoImage(img)
    btnStatistic = Button(frBottomMenu, image=img, compound=TOP)
    # устанавливаем картинку кнопке
    btnStatistic.image = img
    btnStatistic.grid(row=0, column=2, padx=0)
    # привязываем событие нажатия на кнопку
    # btnStatistic.bind("<ButtonPress-1>", clickFunc)

    # функция обработки нажатия на кнопку
    clickFunc = lambda event: createCarsForm(db, usrData, root)
    img = Image.open("../static/icons/btnCar.png")
    img = ImageTk.PhotoImage(img)
    btnCars = Button(frBottomMenu, image=img, compound=TOP)
    # устанавливаем картинку кнопке
    btnCars.image = img
    btnCars.grid(row=0, column=3, padx=0)
    # привязываем событие нажатия на кнопку
    btnCars.bind("<ButtonPress-1>", clickFunc)

    # функция обработки нажатия на кнопку
    clickFunc = lambda event: createUsrForm(db, usrData, root)
    img = Image.open("../static/icons/btnUsr.png")
    img = ImageTk.PhotoImage(img)
    btnUsr = Button(frBottomMenu, image=img, compound=TOP)
    # устанавливаем картинку кнопке
    btnUsr.image = img
    btnUsr.grid(row=0, column=4, padx=0)
    # привязываем событие нажатия на кнопку
    # btnUsr.bind("<ButtonPress-1>", clickFunc)
    '''
    # массив иконок
    arrIcoName = ["btnReg", "btnLists", "btnStatistic", "btnCar", "btnUsr"]
    # массив функций
    arrclickFuncs = [createRegForm, createRegListForm, createStatisticForm, createCarsForm, createUsrForm]
    # массив кнопок
    arrBtn = []

    # создаем кнопки нижнего меню
    for i in range(5):
        # функция обработки нажатия на кнопку
        clickFunc = lambda event: arrclickFuncs[i](db, usrData, root)
        img = Image.open("../static/icons/" + arrIcoName[i] + ".png")
        img = ImageTk.PhotoImage(img)
        arrBtn.append(Button(frBottomMenu, image=img, compound=TOP))
        # устанавливаем картинку кнопке
        arrBtn[i].image = img
        arrBtn[i].grid(row=0, column=i, padx=0)
        # привязываем событие нажатия на кнопку
        arrBtn[i].bind("<ButtonPress-1>", clickFunc)
    '''

    frBottomMenu.pack(anchor=S, ipadx=100, padx=0, pady=60)

    root.mainloop()