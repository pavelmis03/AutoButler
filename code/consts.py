# шрифты
from tkinter import font

# КОНСТАНТЫ

# список ролей
ROLELIST = [
    ["Администратор", "Аналитик", "Менеджер по размещению", "Начальник отдела обслуживания"],
    ["admin",         "analyst",  "operator",               "manager"],
]

# константы шрифтов
FNTBTN = 0
FNTBTNMINI = 0
FNTLBLS = 0
FNTLBLERR = 0
FNTLBLH1 = 0
FNTLBLH2 = 0
FNTLBLH3 = 0

def setFonts():
    # константы шрифтов
    global FNTBTN, FNTBTNMINI, FNTLBLS, FNTLBLERR, FNTLBLH1, FNTLBLH2, FNTLBLH3
    # настраиваем шрифт для кнопок
    FNTBTN = font.Font(family="Arial", size=12, weight="normal", slant="roman")
    # настраиваем маленький шрифт для кнопок
    FNTBTNMINI = font.Font(family="Arial", size=10, weight="normal", slant="roman")
    # стандартный шрифт для обычных надписей
    FNTLBLS = font.Font(family="Arial", size=10, weight="normal", slant="roman")
    # шрифт для вывода сообщений об ошибке
    FNTLBLERR = font.Font(family="Arial", size=10, weight="normal", slant="roman")
    # шрифт для крупных заголовков
    FNTLBLH1 = font.Font(family="Arial", size=14, weight="bold", slant="roman")
    # шрифт для средних заголовков
    FNTLBLH2 = font.Font(family="Arial", size=12, weight="normal", slant="roman")
    # шрифт для мелких заголовков
    FNTLBLH3 = font.Font(family="Arial", size=11, weight="normal", slant="roman")