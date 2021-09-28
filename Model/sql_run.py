import fdb
# import sys


def run_command(command):
    try:
        con = fdb.connect(
            host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB',
            user='SYSDBA', password='masterkey'
        )

        # Create a Cursor object that operates in the context of Connection con:
        cur = con.cursor()

        # Execute the SELECT statement:
        cur.execute(command)

        con.close()
        return cur

    except Exception as e:
        print(e)


if __name__ == '__main__':
    import sys
    run_command(str(sys.argv[1]))
