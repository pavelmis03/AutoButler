# библиотека графических элементов для
from tkinter import *
# дополнительные виджеты
from tkinter import ttk
# шрифты
from tkinter import font
# бибиблиотека для работы с ini файлами
import configparser

# подключаем файл с функциями обработки данных, получаемых от форм
from funcs import *
# константы
import consts
# основные формы
from formMain import *

# библиотека для работы с изображениями
from PIL import ImageTk, Image  # pip install pillow

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