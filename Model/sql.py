import os


class SQL:
    def __init__(self, host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB', user='SYSDBA',
                 password='masterkey'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def select(self, _select: list, _from: list, _where: dict):
        command = f'SELECT {",".join([s for s in _select])} ' \
                  f'FROM {",".join([f for f in _from])} ' \
                  f'WHERE CODIGOEMPRESA = {_where["CODIGOEMPRESA"]} and CODIGOPESSOA = {_where["CODIGOPESSOA"]} ' \
                  f'and NUMERONF = {_where["NUMERONF"]} and ESPECIENF = \'{_where["ESPECIENF"]}\' and SERIENF = ' \
                  f'\'{_where["SERIENF"]}\''

        # print('SQL command:', command)

        os.system(fr'py -2 Model\sql_run.py {command} {self.host} {self.database} {self.user} {self.password}')
