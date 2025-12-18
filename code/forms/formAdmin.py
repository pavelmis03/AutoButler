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
from funcs.funcsAuth import *
# подключаем файл с функциями обработки данных, получаемых от форм админа
from funcs.funcsAdminForm import *
# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts

# создаем форму для работы Админа - окно вывода ошибок
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createAndminUserManageForm(db, usrData):
    # ширина и высота окна
    w = 970
    h = 750
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, { usrData['name'] }. Ваша роль: { usrData['role'] }", w=w, h=h, marginx=250, marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="УЧЕТНЫЕ ЗАПИСИ")
    lblMain.pack(pady=30)

    # -------------БЛОК добавления и изменения пользователя-------------

    # создаем рамку для выбора таблицы
    frAddUser = LabelFrame(frMain, font=consts.FNTLBLH2, text="Добавление пользователя", borderwidth=1, relief=SOLID)

    # сетка компонентов 8x4
    createGrid(frAddUser, 8, 8, 1, 1)

    # -----------column_1-------
    # имя
    lblName = Label(frAddUser, font=consts.FNTLBLS, text="Имя:")
    # устанавливаем позицию компонента в сетке
    lblName.grid(row=0, column=0, padx=15, pady=10, sticky=W)
    # текстовое поле имя
    etrName = Entry(frAddUser, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrName.insert(0, "Введите имя")
    etrName.grid(row=1, column=0, padx=15, pady=[0, 10], sticky=W)

    # фамилия
    lblSurname = Label(frAddUser, font=consts.FNTLBLS, text="Фамилия:")
    # устанавливаем позицию компонента в сетке
    lblSurname.grid(row=2, column=0, padx=15, pady=10, sticky=W)
    # текстовое поле фамилия
    etrSurname = Entry(frAddUser, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrSurname.insert(0, "Введите фамилию")
    etrSurname.grid(row=3, column=0, padx=15, pady=[0, 10], sticky=W)

    # отчество
    lblPatr = Label(frAddUser, font=consts.FNTLBLS, text="Отчество:")
    # устанавливаем позицию компонента в сетке
    lblPatr.grid(row=4, column=0, padx=15, pady=10, sticky=W)
    # текстовое поле Отчество
    etrPatr = Entry(frAddUser, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrPatr.insert(0, "Введите отчество")
    etrPatr.grid(row=5, column=0, padx=15, pady=[0, 10], sticky=W)

    # Роль
    lblRole = Label(frAddUser, font=consts.FNTLBLS, text="Роль:")
    # устанавливаем позицию компонента в сетке
    lblRole.grid(row=6, column=0, padx=15, pady=10, sticky=W)
    # выпадающий список ролей для входа
    cbxRole = ttk.Combobox(frAddUser, values=["Выберите роль", *consts.ROLELIST[0]], state="readonly")
    # устанавливаем значение по умолчанию
    cbxRole.current(0)
    # устанавливаем позицию компонента в сетке
    cbxRole.grid(row=7, column=0, padx=15, pady=[0, 10], sticky=W)

    #-----------column_2-------
    # Телефон
    lblPhone = Label(frAddUser, font=consts.FNTLBLS, text="Телефон:")
    # устанавливаем позицию компонента в сетке
    lblPhone.grid(row=0, column=1, padx=15, pady=10, sticky=W)
    # текстовое поле телефон
    etrPhone = Entry(frAddUser, font=consts.FNTLBLS, width=25)
    # значение по умолчанию для поля ввода
    etrPhone.insert(0, "79991112233")
    etrPhone.grid(row=1, column=1, padx=15, pady=[0, 10], sticky=W)

    # Почта
    lblEmail = Label(frAddUser, font=consts.FNTLBLS, text="Почта:")
    # устанавливаем позицию компонента в сетке
    lblEmail.grid(row=2, column=1, padx=15, pady=10, sticky=W)
    # текстовое поле почта
    etrEmail = Entry(frAddUser, font=consts.FNTLBLS, width=25)
    # значение по умолчанию для поля ввода
    etrEmail.insert(0, "post@gmail.com")
    etrEmail.grid(row=3, column=1, padx=15, pady=[0, 10], sticky=W)

    # Комментарий
    lblComm = Label(frAddUser, font=consts.FNTLBLS, text="Комментарий:")
    # устанавливаем позицию компонента в сетке
    lblComm.grid(row=4, column=1, padx=15, pady=10, sticky=W)
    # текстовое поле для комментария
    tbComm = Text(frAddUser, width=25, height=5, wrap="word")
    tbComm.grid(row=5, column=1, rowspan=3, padx=15, pady=[0, 10], sticky=W)
    # скроллбары для текстбокса, привязываем их к виду в текстбоксе
    # ys = ttk.Scrollbar(orient="vertical", command=tbComm.yview)
    # ys.grid(row=5, column=2, sticky=NS)
    # xs = ttk.Scrollbar(orient="horizontal", command=tbComm.xview)
    # xs.grid(row=6, column=1, sticky=EW)
    # # устанавливаем созданные скроллбары текстовому полю
    # tbComm["yscrollcommand"] = ys.set
    # tbComm["xscrollcommand"] = xs.set

    # -----------column_3-------
    # логин
    lblLogin = Label(frAddUser, font=consts.FNTLBLS, text="Логин:")
    # устанавливаем позицию компонента в сетке
    lblLogin.grid(row=0, column=2, padx=15, pady=10, sticky=W)
    # текстовое поле логин
    etrLogin = Entry(frAddUser, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrLogin.insert(0, "Введите логин")
    etrLogin.grid(row=1, column=2, padx=15, pady=[0, 10], sticky=W)


    # Пароль
    lblPass = Label(frAddUser, font=consts.FNTLBLS, text="Пароль:")
    # устанавливаем позицию компонента в сетке
    lblPass.grid(row=2, column=2, padx=15, pady=10, sticky=W)
    # текстовое поле пароль
    etrPass = Entry(frAddUser, font=consts.FNTLBLS, show="*")
    # значение по умолчанию для поля ввода
    etrPass.insert(0, "")
    etrPass.grid(row=3, column=2, padx=15, pady=[0, 10], sticky=W)

    # проверка правильности заполнения данных
    clickFunc = lambda: checkNewUserData(db, root, etrName.get(), etrSurname.get(), etrPatr.get(),
                                         cbxRole.get(), etrPhone.get(), etrEmail.get(), tbComm.get("1.0", "end"), etrLogin.get(),
                                         etrPass.get())
    # добавить пользователя (сначала вызывается функция проверки правильности заполнения данных)
    btnAddUser = Button(frAddUser, font=consts.FNTBTNMINI, text="Добавить\nпользователя", command=clickFunc, padx=5, pady=5)
    btnAddUser.grid(row=4, column=2, rowspan=2, padx=15, pady=[5, 5], sticky=W)

    # добавить пользователя (сначала вызывается функция проверки правильности заполнения данных)
    btnChangeUser = Button(frAddUser, font=consts.FNTBTNMINI, text="Изменить\nпользователя", command=clickFunc, padx=5, pady=5)
    btnChangeUser.grid(row=6, column=2, rowspan=2, padx=15, pady=[5, 5], sticky=W)

    # # для вывода сообщений об ошибке
    # lblErr = Label(frAddUser, font=consts.FNTLBLS, text="Пароль:")
    # # устанавливаем позицию компонента в сетке
    # lblErr.grid(row=2, column=2, padx=15, pady=10, sticky=W)

    # добавляем таблицу на форму
    frAddUser.pack(anchor=NW, fill=BOTH, padx=15, pady=[0, 10])

    # -------------БЛОК удаление пользователя-------------

    frDelUser = LabelFrame(frMain, font=consts.FNTLBLH2, text="Удаление пользователя", borderwidth=1, relief=SOLID)


    # добавляем таблицу на форму
    frDelUser.pack(anchor=NW, fill=BOTH, padx=15, pady=10)

    # выход из пользователя
    btnLogOut = Button(frMain, font=consts.FNTBTN, text="Сменить пользователя", padx=5, pady=5, command=lambda: logOut(db, root))
    btnLogOut.pack(anchor=S, padx=10, pady=[8, 20])

    frMain.pack(fill=BOTH, padx=5, pady=5, ipadx=10, ipady=10)

    root.mainloop()

# создаем форму для работы Админа - основное окно
def createAdminMainForm(db, usrData):
    createAndminUserManageForm(db, usrData)