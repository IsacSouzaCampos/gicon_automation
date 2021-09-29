# -*- coding: utf-8 -*-
import fdb
from constants import SYS_PATH


def run_command(command, host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB',
                user='SYSDBA', password='masterkey'):

    result = str()
    try:
        con = fdb.connect(host=host, database=database, user=user, password=password)

        # Create a Cursor object that operates in the context of Connection con:
        cur = con.cursor()

        # Execute the SELECT statement:
        cur.execute(command)
        result = ';'.join([';'.join([str(item) for item in row]) for row in cur])
        con.close()
    except Exception as e:
        print('Erro na conexão com o BD:', e)

    write_to_binary(result)


def write_to_binary(result):
    """
    Escreve a tabela resultante do comando SQL em formato binário.

    :param result: Tabela de resultado da consulta.
    :type result:  (str)
    """

    byte_arr = bytearray(result, 'utf8')
    with open(SYS_PATH + r'\bd_results.bin', 'wb') as fout:
        fout.write(byte_arr)


if __name__ == '__main__':
    import sys
    run_command(str(sys.argv[1].replace('_', ' ')), str(sys.argv[2]), str(sys.argv[3]), str(sys.argv[4]),
                str(sys.argv[5]))
