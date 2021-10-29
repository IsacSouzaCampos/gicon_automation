# -*- coding: utf-8 -*-
import fdb
from constants import SYS_PATH


def run_command(host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB',
                user='SYSDBA', password='masterkey'):

    # limpar o arquivo que conterá os resultados de consultas
    open(SYS_PATH + r'\bd_results.bin', 'w').close()

    # carregar os comands em memória
    with open(SYS_PATH + r'\commands.bin', 'r') as fin:
        commands = fin.read()

    results = list()
    try:
        con = fdb.connect(host=host, database=database, user=user, password=password)
        # print('conexão com BD aberta')

        # Create a Cursor object that operates in the context of Connection con:
        cur = con.cursor()

        # Execute the SELECT statements:
        for command in commands.split(';'):
            cur.execute(command)
            results.append(';'.join([';'.join([str(item) for item in row]) for row in cur]))

        cur.close()
        con.close()

    except Exception as e:
        print('Erro na conexão com o BD:', e)

    # if 'select' in command.lower():
        # print('escrevendo resultado em arquivo')
    write_to_binary(results)


def write_to_binary(results):
    """
    Escreve a tabela resultante do comando SQL em formato binário.

    :param results: Tabela de resultado da consulta.
    :type results:  (list)
    """

    byte_arr = bytearray('\n'.join(results), 'utf8')
    with open(SYS_PATH + r'\bd_results.bin', 'w+b') as fout:
        fout.write(byte_arr)


if __name__ == '__main__':
    import sys
    run_command(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]),
                str(sys.argv[4]))
