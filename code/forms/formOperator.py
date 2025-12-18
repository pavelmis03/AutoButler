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
# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts


# создаем форму для работы механика
def createOperatorMainForm(db, usrData):
    pass