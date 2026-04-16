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
from funcs.funcsAdminForm import *
# функции для работы с формами
from funcs.funcsForm import createGrid, createWindow
# константы
import consts

# создаем форму для работы Админа с пользователями
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createAndminUserManageForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

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
    tbComm = ScrolledText(frAddUser, width=25, height=5, wrap="word")
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

    # -----------column_4-------

    # поиск пользователя
    lblFindUser = Label(frAddUser, font=consts.FNTLBLS, justify="left", text="Введите фамилию, или логин,\nили телефон пользователя\nдля поиска: ")
    # устанавливаем позицию компонента в сетке
    lblFindUser.grid(row=1, column=3, columnspan=2, padx=15, pady=10, sticky=W)
    # текстовое поле пароль
    etrFindUser = Entry(frAddUser, font=consts.FNTLBLS)
    # значение по умолчанию для поля ввода
    etrFindUser.insert(0, "")
    etrFindUser.grid(row=2, column=3, columnspan=2, padx=15, pady=[0, 10], sticky=W)

    # найденные варианты
    lblFindUserRes = Label(frAddUser, font=consts.FNTLBLS, text="Найденные пользователи: ")
    # устанавливаем позицию компонента в сетке
    lblFindUserRes.grid(row=3, column=3, columnspan=2, padx=15, pady=10, sticky=W)
    # выпадающий список ролей для входа
    cbxFindUserRes = ttk.Combobox(frAddUser, values=["Нет совпадений"], state="readonly")
    # устанавливаем значение по умолчанию
    cbxFindUserRes.current(0)
    # устанавливаем позицию компонента в сетке
    cbxFindUserRes.grid(row=4, column=3, columnspan=2, padx=15, pady=[0, 10], sticky=W)


    # проверка правильности заполнения данных
    clickFunc = lambda: checkNewUserData(db, root, etrName.get(), etrSurname.get(), etrPatr.get(),
                                         cbxRole.get(), etrPhone.get(), etrEmail.get(), tbComm.get("1.0", "end"),
                                         etrLogin.get(), etrPass.get())
    # добавить пользователя (сначала вызывается функция проверки правильности заполнения данных)
    btnAddUser = Button(frAddUser, font=consts.FNTBTNMINI, text="Добавить\nпользователя", command=clickFunc, padx=5, pady=5)
    btnAddUser.grid(row=6, column=2, rowspan=2, padx=15, pady=[5, 5], sticky=W)

    # изменение пользователя
    clickFunc = lambda: changeUser(db, root, etrName.get(), etrSurname.get(), etrPatr.get(),
                                         cbxRole.get(), etrPhone.get(), etrEmail.get(), tbComm.get("1.0", "end"),
                                         etrLogin.get(), etrPass.get(), cbxFindUserRes.get(), etrFindUser.get(), cbxFindUserRes)
    # изменить пользователя (сначала вызывается функция проверки правильности заполнения данных)
    btnChangeUser = Button(frAddUser, font=consts.FNTBTNMINI, text="Изменить\nпользователя", command=clickFunc, padx=5, pady=5, state="disabled")
    btnChangeUser.grid(row=6, column=3, rowspan=2, padx=15, pady=[5, 5], sticky=W)

    # удаление пользователя
    clickFunc = lambda: delUser(db, cbxFindUserRes.get(), etrFindUser.get(), cbxFindUserRes)
    # удалить пользователя
    btnDelUser = Button(frAddUser, font=consts.FNTBTNMINI, text="Удалить\nпользователя", command=clickFunc, padx=5,
                           pady=5, state="disabled")
    btnDelUser.grid(row=6, column=4, rowspan=2, padx=15, pady=[5, 5], sticky=W)
    # поиск пользователя
    clickFunc = lambda: findUser(db, etrFindUser.get(), cbxFindUserRes)
    # найти пользователя
    btnFindUser = Button(frAddUser, font=consts.FNTBTNMINI, text="Найти\nпользователя", command=clickFunc, padx=5,
                        pady=5, state="disabled")
    btnFindUser.grid(row=6, column=5, rowspan=2, padx=15, pady=[5, 5], sticky=W)

    # группа для radioBtns
    workMode = StringVar(value="addUser")
    # изменение режима работы с добавлением на редактирование и наоборот
    clickFunc = lambda: changeWorkMode(workMode, btnAddUser, btnChangeUser, btnDelUser, btnFindUser)
    # кнопка для выбора режима добавления пользователя
    radioAddUser = Radiobutton(frAddUser, font=consts.FNTBTNMINI, text="Добавление\nпользователя", command=clickFunc, padx=5,
                           pady=5, value="addUser", variable=workMode)
    radioAddUser.grid(row=0, column=3, rowspan=1, padx=15, pady=[5, 5], sticky=W)
    # кнопка для выбора режима редактирования пользователя
    radioChangeUser = Radiobutton(frAddUser, font=consts.FNTBTNMINI, text="Редактирование\nпользователя", command=clickFunc,
                               padx=5, pady=5, value="changeUser", variable=workMode)
    radioChangeUser.grid(row=0, column=4, rowspan=1, padx=15, pady=[5, 5], sticky=W)
    # кнопка для выбора режима удаления пользователя
    radioDelUser = Radiobutton(frAddUser, font=consts.FNTBTNMINI, text="Удаление\nпользователя",
                                  command=clickFunc, padx=5, pady=5, value="delUser", variable=workMode)
    radioDelUser.grid(row=0, column=5, rowspan=1, padx=15, pady=[5, 5], sticky=W)

    # добавляем раздел на форму
    frAddUser.pack(anchor=NW, fill=BOTH, padx=15, pady=[0, 10])

    # выход в предыдущее меню
    clickFunc = lambda: createAdminMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=5)
    btnBack.pack(fill=BOTH, padx=30, pady=5, ipadx=10, ipady=10)

    frMain.pack(fill=BOTH, padx=5, pady=5, ipadx=10, ipady=10)

    root.mainloop()

# создаем форму для работы Админа - окно управления системой
# userData = {"login", "pwd", "role", "email", "phone", "name", "surname", "patr", "descr"}
def createAndminSystemManageForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 1270
    h = 750
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="УПРАВЛЕНИЕ СИСТЕМОЙ")
    lblMain.pack(pady=30)

    # -------------БЛОК таблицы-------------

    # создаем рамку таблицы логов
    lFRegList = LabelFrame(frMain, font=consts.FNTLBLH2, text="Список логов", borderwidth=1, relief=SOLID)

    # строим таблицу по полученным данным
    logList = ttk.Treeview(lFRegList, columns=[], show="headings", height=8)

    # создаем полосы прокрутки для таблицы
    scrlV = ttk.Scrollbar(lFRegList, orient="vertical", command=logList.yview)
    scrlV.pack(side=RIGHT, fill=Y)
    scrlH = ttk.Scrollbar(lFRegList, orient="horizontal", command=logList.xview)
    scrlH.pack(side=BOTTOM, fill=X)

    # привязка полос прокрутки к таблице
    logList["yscrollcommand"] = scrlV.set
    logList["xscrollcommand"] = scrlH.set

    # добавляем, растягивая по ширине элементы и заполняя контэйнер
    logList.pack(fill=BOTH, expand=1, padx=5, pady=[5, 10])

    # определяем заголовки для столбцов
    i = 1
    # очищаем таблицу перед наполнением
    for col in logList["columns"]:
        logList.heading(col, text="")
        i += 1
    logList.delete(*logList.get_children())

    # список колонок будущей таблицы
    cols = ["№", "Название", "Тип записи", "Статус", "Описание", "Дата записи", "Время записи"]
    # строим таблицу по полученным данным
    logList["columns"] = cols
    # определяем заголовки для столбцов
    i = 1
    for col in cols:
        logList.heading(col, text=col, anchor=CENTER,
                        # здесь создаю замыкание, чтобы i передавалась, как значение, а не как ссылка
                        # настройка сортировки по столбцам
                        command=(lambda tree, i, f: (lambda: columnSort(tree, i, f)))(logList, i - 1, False))
        # выравнивание по центру для данных в ячейках
        logList.column(f"#{i}", width=len(col) * 7, minwidth=40, anchor=CENTER, stretch=True)
        i += 1

    # наполняем таблицу данными
    insertDataToTable(db, logList, [], 6)

    # добавляем таблицу на форму
    lFRegList.pack(anchor=NW, fill=BOTH, expand=True, padx=10, pady=10)

    # -------------БЛОК кнопок управления-------------

    # создаем рамку для кнопок
    frManageBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Рабочие окна", borderwidth=1, relief=SOLID)

    # сетка компонентов 6x5
    createGrid(frManageBtns, 15, 6, 1, 1)
    # массив компонентов управления данными
    components = []

    # очистить журнал
    clickFunc = lambda: clearLogList(db, logList)
    btnCleareLogList = Button(frManageBtns, font=consts.FNTBTN, text="Очистить журнал", command=clickFunc, padx=20, pady=10)
    btnCleareLogList.grid(row=0, column=0, columnspan=2, rowspan=2, padx=10, pady=[10, 10], ipadx=10)

    # удалить запись
    clickFunc = lambda: delRecord(db, logList, components)
    btnDelRecord = Button(frManageBtns, font=consts.FNTBTN, text="Удалить запись", command=clickFunc, padx=10, pady=10)
    btnDelRecord.grid(row=2, column=0, columnspan=2, padx=15, pady=[10, 10], ipadx=20)

    # сформировать гистограмму
    clickFunc = lambda: createHist(db, components, True)
    btnCreateHist = Button(frManageBtns, font=consts.FNTBTN, text="Гистограмма", command=clickFunc, padx=10, pady=10)
    btnCreateHist.grid(row=2, column=0, columnspan=2, padx=15, pady=[10, 10], ipadx=20)

    # сформировать отчет
    clickFunc = lambda: createReport(db, etrDateFrom.get(), etrDateUntil.get(), etrTimeFrom.get(), etrTimeUntil.get())
    btnCreateReport = Button(frManageBtns, font=consts.FNTBTN, text="Сформировать отчет", command=clickFunc, padx=10, pady=10)
    btnCreateReport.grid(row=4, column=0, columnspan=2, rowspan=2, padx=15, pady=[10, 20])

    # дата от
    lblDateFrom = Label(frManageBtns, font=consts.FNTLBLS, text="Дата от:")
    lblDateFrom.grid(row=0, column=2, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrDateFromVar = StringVar()
    etrDateFromVar.trace("w", lambda a, b, c: insertDataToTable(db, logList, components, 6))
    # текстовое поле дата ОТ
    etrDateFrom = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrDateFromVar)
    # значение по умолчанию для поля ввода
    etrDateFrom.insert(0, "2000-01-01")
    etrDateFrom.grid(row=1, column=2, columnspan=1, padx=10, pady=[0, 10], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateFrom)

    # дата до
    lblDateUntil = Label(frManageBtns, font=consts.FNTLBLS, text="Дата до:")
    lblDateUntil.grid(row=2, column=2, columnspan=2, padx=10, pady=[0, 10], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrDateUntilVar = StringVar()
    etrDateUntilVar.trace("w", lambda a, b, c: insertDataToTable(db, logList, components, 6))
    # текстовое поле дата ДО
    etrDateUntil = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrDateUntilVar)
    # значение по умолчанию для поля ввода
    etrDateUntil.insert(0, str(datetime.now().date()))
    etrDateUntil.grid(row=3, column=2, columnspan=1, padx=10, pady=[0, 10], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrDateUntil)

    # время от
    lblTimeFrom = Label(frManageBtns, font=consts.FNTLBLS, text="Время от:")
    lblTimeFrom.grid(row=0, column=3, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeFromVar = StringVar()
    etrTimeFromVar.trace("w", lambda a, b, c: insertDataToTable(db, logList, components, 6))
    # текстовое поле время ОТ
    etrTimeFrom = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrTimeFromVar)
    # значение по умолчанию для поля ввода
    etrTimeFrom.insert(0, "00:00")
    etrTimeFrom.grid(row=1, column=3, columnspan=1, padx=10, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeFrom)

    # время до
    lblTimeUntil = Label(frManageBtns, font=consts.FNTLBLS, text="Время до:", padx=0, pady=0)
    lblTimeUntil.grid(row=2, column=3, columnspan=2, padx=10, pady=[0, 0], sticky=W)

    # переменная для отслеживания изменения поля ввода
    etrTimeUntilVar = StringVar()
    etrTimeUntilVar.trace("w", lambda a, b, c: insertDataToTable(db, logList, components, 6))
    # текстовое поле время ДО
    etrTimeUntil = Entry(frManageBtns, font=consts.FNTLBLS, textvariable=etrTimeUntilVar)
    # значение по умолчанию для поля ввода
    etrTimeUntil.insert(0, "23:59")
    etrTimeUntil.grid(row=3, column=3, columnspan=1, padx=10, pady=[0, 0], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(etrTimeUntil)

    # переменная для отслеживания изменения поля ввода
    cbxActTypeVar = StringVar()
    cbxActTypeVar.trace("w", lambda a, b, c: insertDataToTable(db, logList, components, 6))
    # выпадающий список типов действий
    cbxActType = ttk.Combobox(frManageBtns, values=["Не указан", "error", "warning", "trace", "alert", "debug", "info", "more"], state="readonly",
                             textvar=cbxActTypeVar)
    # устанавливаем значение по умолчанию
    cbxActType.current(0)
    # устанавливаем позицию компонента в сетке
    cbxActType.grid(row=4, column=3, padx=10, pady=[0, 20], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(cbxActType)

    # переменная для отслеживания изменения поля ввода
    cbxStatusVar = StringVar()
    cbxStatusVar.trace("w", lambda a, b, c: insertDataToTable(db, logList, components, 6))
    # выпадающий список статусов
    cbxStatus = ttk.Combobox(frManageBtns, values=["Не указан", "relevant", "irrelevant", "timeout"], state="readonly", textvar=cbxStatusVar)
    # устанавливаем значение по умолчанию
    cbxStatus.current(0)
    # устанавливаем позицию компонента в сетке
    cbxStatus.grid(row=4, column=2, padx=10, pady=[0, 20], sticky=W)
    # добавляем в массив компонентов текущий элемент
    components.append(cbxStatus)

    frManageBtns.pack(fill=BOTH, padx=10, pady=5, ipadx=3)

    # выход в предыдущее меню
    clickFunc = lambda: createAdminMainForm(db, root, usrData)
    # кнопка ,,назад,, (выйти в предыдущее меню)
    btnBack = Button(frMain, font=consts.FNTLBLH2, text="Назад", command=clickFunc, padx=5, pady=5)
    btnBack.pack(fill=BOTH, padx=30, pady=5, ipadx=10, ipady=10)


    frMain.pack(fill=BOTH, padx=10, pady=5, ipadx=10, ipady=10)

    root.mainloop()

# создаем форму для работы Админа - основное окно
def createAdminMainForm(db, root, usrData):
    # удаляем предыдущее окно
    root.destroy()

    # ширина и высота окна
    w = 570
    h = 520
    # если дошло до этого места, значит, есть пользователь с введенными данными - создаем новое окно
    root = createWindow(f"Добро пожаловать, {usrData['name']}. Ваша роль: {usrData['role']}", w=w, h=h, marginx=250,
                        marginy=10)

    # создаем основную рамку
    frMain = Frame(borderwidth=1, relief=SOLID)

    # основной заголовок
    lblMain = Label(frMain, font=consts.FNTLBLH1, text="АДМИНИСТРИРОВАНИЕ")
    lblMain.pack(pady=30)

    # создаем рамку для кнопок
    frBtns = LabelFrame(frMain, font=consts.FNTLBLH2, text="Рабочие окна", borderwidth=1, relief=SOLID)

    # сетка компонентов 3x3
    createGrid(frBtns, 3, 9, 1, 1)

    # -------------БЛОК выбора окна-------------

    # управление пользователями
    clickFunc = lambda: createAndminUserManageForm(db, root, usrData)
    # управление пользователями
    btnUserManageForm = Button(frBtns, font=consts.FNTBTN, text="Управление учетными\nзаписями пользователей", command=clickFunc, padx=10, pady=10)
    btnUserManageForm.grid(row=1, column=1, rowspan=2, padx=15, pady=[35, 10])

    # настройка системы
    clickFunc = lambda: createAndminSystemManageForm(db, root, usrData)
    # настройка системы
    btnSystemManageForm = Button(frBtns, font=consts.FNTBTN, text="Настройки системы", command=clickFunc, padx=30, pady=20)
    btnSystemManageForm.grid(row=4, column=1, rowspan=2, padx=15, pady=[10, 10])

    # выход из пользователя
    btnLogOut = Button(frBtns, font=consts.FNTBTN, text="Сменить пользователя", padx=17, pady=20,
                       command=lambda: fAuth.logOut(db, root))
    btnLogOut.grid(row=7, column=1, rowspan=2, padx=15, pady=[10, 35])

    # добавляем раздел на форму
    frBtns.pack(anchor=NW, fill=BOTH, padx=15, pady=[0, 10])

    frMain.pack(fill=BOTH, padx=5, pady=5, ipadx=10, ipady=10)

    root.mainloop()


