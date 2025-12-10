# библиотека графических элементов для
from tkinter import *
# дополнительные виджеты
from tkinter import ttk
# шрифты
from tkinter import font

# библиотека для sql-запросов
import pymysql as sql
import pandas as pd
# модули для работы с операционной системой
import os
import shutil

# библиотека для работы с изображениями
from PIL import ImageTk, Image  # pip install pillow

# бибиблиотека для работы с ini файлами
import configparser

# подключаем файл с функциями обработки данных
from funcs import *
from funcsForm import *

# создание стартовой формы
def createFormAuth(db):
    # создаем окно формы
    root = createWindow("Добро пожаловать!", 500, 250, icon="../static/icons/main.ico")

    # настраиваем шрифт для кнопок
    fntBtn = font.Font(family="Arial", size=12, weight="normal", slant="roman")

    # создаем рамку для текста и кнопок
    frMain = Frame(borderwidth=1, relief=SOLID, padx=8, pady=10)

    # создаем рамку для текста
    frHello = Frame(frMain, borderwidth=0, relief=SOLID, padx=8, pady=10)
    # приветственная подпись
    lblHello = Label(frHello, text="Добро пожаловать в систему оптимизации затрат и\nподдержки процесса размещения пассажиров\nв гостиницах при задержках и отмене авиарейсов")
    # добавление элемента на форму
    lblHello.pack()
    # добавляем frame на форму
    frHello.pack(anchor=NW, fill=X, padx=5, pady=5)

    # создаем рамку для кнопок
    frBtns = Frame(frMain, borderwidth=0, relief=SOLID, padx=8, pady=10)

    # создаем сетку 2 столбца, 1 строка
    createGrid(frBtns, 2, 1, 1, 1)

    # кнопка для входа в приложение
    # функция обработки нажатия на кнопку
    clickFunc = lambda event: createSignInForm(db, root)  # функция создания окна авторизации
    btnEnter = Button(frBtns, text="Войти! ", font=fntBtn, padx=20, pady=10)
    btnEnter.grid(row=0, column=0, padx=5, pady=[10, 5])

    # привязываем событие нажатия на кнопку
    btnEnter.bind("<ButtonPress-1>", clickFunc)
    # добавляем возможность подтверждать регистрацию энтером
    root.bind("<Return>", clickFunc)

    # кнопка для выходы из приложения
    btnQuit = Button(frBtns, text="Покинуть\nприложение", command=root.destroy, font=fntBtn, padx=5)
    btnQuit.grid(row=0, column=1, padx=5, pady=[10, 5])

    # добавляем frame на форму
    frBtns.pack(anchor=NW, fill=X, padx=5, pady=5)

    # добавляем frame на форму
    frMain.pack(anchor=NW, fill=X, padx=5, pady=5)

    # запускаем основной цикл отрисовки интерфейса
    root.mainloop()

# форма входа в аккаунт
def createSignInForm(db):
    pass
