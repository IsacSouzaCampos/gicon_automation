import os
from Model.constants import SYS_PATH


class SQL:
    def __init__(self, host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB', user='SYSDBA',
                 password='masterkey'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def invoice_in_bd(self, taker_code, provider_code, inv_number):
        command = f'SELECT CODIGOEMPRESA CODIGOPESSOA NUMERONF FROM LCTOFISENT ' \
                  f'WHERE CODIGOEMPRESA = {taker_code} and CODIGOPESSOA = {provider_code} ' \
                  f'and NUMERONF = {inv_number} and ESPECIENF = \'NFSE\' and SERIENF = \'U\''

        self.run_command(command)

    def get_company_code(self, cnpj: str) -> str:
        """
        Retorna o código da empresa com base no seu nome.

        :param cnpj:  CNPJ da empresa.
        :type cnpj:   (str)
        :param _type: Tipo da empresa (cliente[0] ou não[1])
        :type _type:  (int)
        """

        cnpj = f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'
        command = f'SELECT CODIGOPESSOA FROM PESSOA WHERE INSCRFEDERAL = \'{cnpj}\''

        # print('command:', command)
        self.run_command(command)
        return self.result()[0]

    def get_city_code(self, city):
        command = f'SELECT CODIGOMUNIC FROM MUNICIPIO WHERE LOWER(NOMEMUNIC) LIKE LOWER(\'%{city}%\')'
        self.run_command(command)
        return self.result()[0]

    def run_command(self, command) -> None:
        os.system(fr'py -2 Model\sql_run.py {command.replace(" ", "_")} {self.host} {self.database} {self.user} '
                  fr'{self.password}')

    @staticmethod
    def result() -> list:
        with open(fr'{SYS_PATH}\bd_results.bin', 'rb') as fin:
            arr = fin.read().decode('utf8')
        return arr.split(';')
