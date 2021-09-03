# import mysql.connector
# con = mysql.connector.connect(host='localhost', database='ens', user='root', password='')
# if con.is_connected():
#     db_info = con.get_server_info()
#     print("Conectado ao servidor MySQL versão ", db_info)
#     cursor = con.cursor()
#     cursor.execute("select database();")
#     linha = cursor.fetchone()
#     print("Conectado ao banco de dados ", linha)
# if con.is_connected():
#     cursor.close()
#     con.close()
#     print("Conexão ao MySQL foi encerrada")


# import pyodbc
# # Some other example server values are
# # server = 'localhost\sqlexpress' # for a named instance
# # server = 'myserver,port' # to specify an alternate port
# server = 'tcp:myserver.database.windows.net'
# database = 'mydb'
# username = 'myusername'
# password = 'mypassword'
# cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='
#                        +username+';PWD='+ password)
# cursor = cnxn.cursor()


# import pandas as pd
# import pyodbc
# conn = pyodbc.connect(r'Driver={SQL Server};'
#                       'Server=RON\SQLEXPRESS;'
#                       'Database=TestDB;'
#                       'Trusted_Connection=yes;')
#
# cursor = conn.cursor()
#
# sql_query = pd.read_sql_query('SELECT * FROM TestDB.dbo.Person', conn)
# print(sql_query)
# print(type(sql_query))
