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

# подключаем файл с функциями обработки данных
from funcs import *
from funcsForm import *
import consts

# создание стартовой формы
def createFormAuth(db):
    # создаем окно формы
    root = createWindow("Добро пожаловать!", 500, 250, icon="../static/icons/main.ico")

    # создаем рамку для текста и кнопок
    frMain = Frame(borderwidth=1, relief=SOLID, padx=8, pady=10)

    # создаем рамку для текста
    frHello = Frame(frMain, borderwidth=0, relief=SOLID, padx=8, pady=10)
    # приветственная подпись
    lblHello = Label(frHello, font=consts.FNTLBLS, text="Добро пожаловать в систему оптимизации затрат и\nподдержки процесса размещения пассажиров\nв гостиницах при задержках и отмене авиарейсов")
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
    btnEnter = Button(frBtns, text="Войти!", font=consts.FNTBTN, padx=20, pady=10)
    btnEnter.grid(row=0, column=0, padx=5, pady=[10, 5])

    # привязываем событие нажатия на кнопку
    btnEnter.bind("<ButtonPress-1>", clickFunc)
    # добавляем возможность подтверждать регистрацию энтером
    root.bind("<Return>", clickFunc)

    # кнопка для выходы из приложения
    btnQuit = Button(frBtns, text="Покинуть\nприложение", command=root.destroy, font=consts.FNTBTN, padx=5)
    btnQuit.grid(row=0, column=1, padx=5, pady=[10, 5])

    # добавляем frame на форму
    frBtns.pack(anchor=NW, fill=X, padx=5, pady=5)

    # добавляем frame на форму
    frMain.pack(anchor=NW, fill=X, padx=5, pady=5)

    # запускаем основной цикл отрисовки интерфейса
    root.mainloop()

# форма входа в аккаунт
def createSignInForm(db, root):
    # удаляем приветственное окно
    root.destroy()

    # создаем окно формы
    root = createWindow("Форма авторизации", 500, 300, icon="../static/icons/main.ico")

    # создаем рамку для полей ввода
    frInput = Frame(borderwidth=1, relief=SOLID, padx=8, pady=10)

    # подпись для поля логина
    lblLogin = Label(frInput, font=consts.FNTLBLH2, text="Введите ваш логин")
    # добавление элемента на форму
    lblLogin.pack(pady=10)

    # текстовое поле логина
    etrLogin = Entry(frInput)
    etrLogin.pack()
    # устанавливаем фокус на окно логина
    etrLogin.focus_set()

    lblPwd = Label(frInput, font=consts.FNTLBLH2, text="Введите ваш пароль")
    lblPwd.pack(pady=[20, 10])

    # поле ввода пароля
    # для пароля задаем маску символа
    etrPwd = Entry(frInput, show="*")
    etrPwd.pack()

    # поле для вывода сообщения об ошибке
    lblErr = Label(frInput, font=consts.FNTLBLS, foreground="red", text="")
    lblErr.pack()

    # кнопка для авторизации
    # функция обработки нажатия на кнопку
    clickFunc = lambda event: checkSignInData(event, db, etrLogin.get(), etrPwd.get(), lblErr, etrPwd, root)
    btnSignIn = Button(frInput, font=consts.FNTBTN, text="Авторизоваться")
    btnSignIn.pack()
    # привязываем событие нажатия на кнопку
    btnSignIn.bind("<ButtonPress-1>", clickFunc)
    # добавляем возможность подтверждать регистрацию энтером
    root.bind("<Return>", clickFunc)

    # зарегистрировать нового пользователя (может только админ)
    # btnSignUp = Button(frInput, text="Зарегистрировать пользователя", command=lambda: getAdminPwd())
    # btnSignUp.pack()

    # добавляем frame на форму
    frInput.pack(anchor=NW, fill=X, padx=5, pady=5)

    # запускаем основной цикл отрисовки интерфейса
    root.mainloop()
