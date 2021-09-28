import fdb
# import sys


def run_command(command='', host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB',
                user='SYSDBA', password='masterkey'):
    # command = "SELECT CODIGOEMPRESA FROM LCTOFISENT WHERE CODIGOEMPRESA = 421 and CODIGOPESSOA = 48888 and
    # NUMERONF " \
    #           "= 379428 and ESPECIENF = 'NFSE' and SERIENF = 'U'"

    # print('command:', command)
    # print('host:', host)
    # print('database:', database)
    # print('user:', user)
    # print('password:', password)

    try:
        con = fdb.connect(host=host, database=database, user=user, password=password)

        # Create a Cursor object that operates in the context of Connection con:
        cur = con.cursor()

        # Execute the SELECT statement:
        cur.execute(command)

        for row in cur:
            print(' - '.join([str(item) for item in row]))

        con.close()

        # table = list()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    import sys
    run_command(str(sys.argv[1].replace('_', ' ')), str(sys.argv[2]), str(sys.argv[3]), str(sys.argv[4]),
                str(sys.argv[5]))
    # run_command()
