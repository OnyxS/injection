# script.py

import pymysql

# Запросы к базе данных
query1 = "SELECT * FROM users WHERE id = {}".format(user_id)
query2 = "SELECT * FROM products WHERE price > {}".format(max_price)
query3 = "UPDATE users SET name = '{}' WHERE id = {}".format(new_name, user_id)

# Выполнение запросов
cursor.execute(query1)
cursor.execute(query2)
cursor.execute(query3)
