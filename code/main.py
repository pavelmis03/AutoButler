# библиотека для sql-запросов
import pymysql as sql
import pandas as pd

# подключаем файлы с функциями создания форм
from forms.formAuth import *

def main():
    # подключение к базе данных
    db = sql.connect(
        host="127.0.0.1", # ip-адрес локального компьютера
        port=3306,
        user="root",
        password="pOiLkJ03",
        database="db",
    )
    # функция создания стартового окна
    createStartForm(db)
    # завершаем подключение к БД
    db.close()

if __name__ == "__main__":
    main()