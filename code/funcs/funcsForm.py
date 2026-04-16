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

from tkinter.messagebox import showerror, showwarning, showinfo, askyesno, askokcancel, askretrycancel
# бибиблиотека для работы с ini файлами
import configparser

# библиотека для sql-запросов
import pymysql as sql
import pandas as pd
import numpy as np
# модули для работы с операционной системой
import os
import shutil
# копирование текста в буфер обмена
import pyperclip

# дата и время
from datetime import datetime, timedelta
import time
# random
import random

# библиотека для построения графика
import matplotlib.pyplot as plt
import pylab
# import cryptography

# библиотеки для создания отчетов
from docxtpl import DocxTemplate
import cryptography

# библиотека для работы с изображениями
from PIL import ImageTk, Image  # pip install pillow

# функции для работы с формами
from funcs.funcsForm import *
# константы
import consts

# функция создания окна tkinter с заданными параметрами
def createWindow(caption, w=500, h=500, marginx=400, marginy=200, resizable=False, icon=None):
    # создаем основное окно
    root = Tk()

    # настраиваем шрифты
    consts.setFonts()

    # заголовок окна
    root.title(caption)
    # настройки размеров и позиционирования окна
    root.geometry(f"{ w }x{ h }+{ marginx }+{ marginy }")
    # запрет на изменение размеров окна
    root.resizable(resizable, resizable)
    # устанавливаем иконку, если передали название файла
    if icon is not None:
        root.iconbitmap(default=icon)
    return root

# создаем сетку для указанного элемента
def createGrid(el, cols, rows, cWeight, rWeight):
    # настройка сетки блока столбцы
    for c in range(cols):
        el.columnconfigure(index=c, weight=cWeight)
    # строки
    for r in range(rows):
        el.rowconfigure(index=r, weight=rWeight)