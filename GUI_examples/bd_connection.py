# import execnet
import fdb
import sys


def main():
    # call_python_version('2.7', 'GUI_examples.bd_connection', 'start_bd', '')
    return start_bd(sys.argv[1])


# def call_python_version(version, module, function, argument_list):
#     gw = execnet.makegateway("popen//python=python%s" % version)
#     channel = gw.remote_exec("""from %s import %s as the_function channel.send(the_function(*channel.receive()))"""
#                              % (module, function))
#     channel.send(argument_list)
#     return channel.receive()


def start_bd(command):
    try:
        con = fdb.connect(
            host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB',
            user='SYSDBA', password='masterkey'
        )

        # Create a Cursor object that operates in the context of Connection con:
        cur = con.cursor()

        # Execute the SELECT statement:
        cur.execute(command)

        # print(type(cur))

        # # Retrieve all rows as a sequence and print that sequence:
        # for row in cur.itermap():
        #     print(row['CHAVELCTOFISENT'])

        con.close()
        return cur

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()


# =====================================================================================================================

# import pyodbc
    # # Some other example server values are
    # # server = 'localhost\sqlexpress' # for a named instance
    # # server = 'myserver,port' # to specify an alternate port
    # # server = '10.0.4.92'
    # # database = r'C:\Questor\db_questor\Saraiva_teste.FDB'
    # # port = '3050'
    # # username = 'SYSDBA'
    # # password = 'masterkey'
    #
    # try:
    #     # cnxn = pyodbc.connect('DRIVER={Devart ODBC Driver for Firebird};SERVER=' + server + ';DATABASE=' + database
    #     + ';PORT=' + port + ' ;UID=' + username + ';PWD=' + password)
    #
    #    cnxn = pyodbc.connect(r'DRIVER={Devart ODBC Driver for Firebird};'
    #                          r'Description=Driver for Firebird;Data Source=10.0.4.92;'
    #                          r'Database=C:\Questor\db_questor\Saraiva_teste.FDB;User ID=SYSDBA;'
    #                          r'Password=masterkey;Client Library=C:\nQuestor\fbclient.dll')
    #
    #     cursor = cnxn.cursor()
    #
    #     # Sample select query
    #     cursor.execute("select SEQ,CHAVELCTOFISENT,CODIGOPRODUTO from LCTOFISENTPRODUTO where codigoempresa = 116  " +
    #                    "and CODIGOCFOP in (1403,2403) and datalctofis between '01.10.2019' and '31.10.2019';")
    #     row = cursor.fetchone()
    #     while row:
    #         print(row)
    #         row = cursor.fetchone()
    #
    #     cursor.close()
    #     print('finalizou')
    # except Exception as e:
    #     print('Erro:', e)

# def main():
#     import pyodbc
#     # Some other example server values are
#     # server = 'localhost\sqlexpress' # for a named instance
#     # server = 'myserver,port' # to specify an alternate port
#     server = '10.0.4.92'
#     database = r'C:\Questor\db_questor\Saraiva_teste.FDB'
#     port = '3050'
#     username = 'admin'
#     password = 'masterkey'
#
#     try:
#         cnxn = pyodbc.connect('DRIVER={Devart ODBC Driver for Firebird};SERVER=' + server + ';DATABASE=' + database +
#                               ';PORT=' + port + ' ;UID=' + username + ';PWD=' + password)
#         cursor = cnxn.cursor()
#         cursor.close()
#         print('finalizou')
#     except Exception as e:
#         print('Erro:', e)


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

# def main():
    # import fdb

    # The server is named 'bison'; the database file is at '/temp/test.db'.
    # con = fdb.connect(dsn=r'\\erp2-r\c$\Questor\db_questor\Saraiva_teste.FDB', user='admin', password='masterkey')

    # Or, equivalently:
    # con = fdb.connect(
    #     host='10.0.4.92', database=r'\\erp2-r\c$\Questor\db_questor\Saraiva_teste.FDB', port='3050',
    #     user='admin', password='masterkey'
    # )


# def main():
#     import pyodbc
#
#     server = '10.0.4.92'
#     database = 'Saraiva_teste'
#     port = '3050'
#     userid = 'admin'
#     password = 'masterkey'
#
#     cnxn = pyodbc.connect('DRIVER={Devart ODBC Driver for Firebird};' + f'Server={server};' +
#                          f'Database={database};' + f'Port={port};' + f'User ID={userid};' + f'Password={password};')


# import mysql.connector
# con = mysql.connector.connect(host='localhost', database='ens', user='root', password='')
# if con.is_connected():
#     db_info = con.get_server_info()
#     print("Conectado ao servidor MySQL versao ", db_info)
#     cursor = con.cursor()
#     cursor.execute("select database();")
#     linha = cursor.fetchone()
#     print("Conectado ao banco de dados ", linha)
# if con.is_connected():
#     cursor.close()
#     con.close()
#     print("Conexao ao MySQL foi encerrada")
