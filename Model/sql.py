import os
from Model.constants import SYS_PATH
from Model.launch import LCTOFISENTData


class SQL:
    def __init__(self, host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB', user='SYSDBA',
                 password='masterkey'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def invoice_in_bd(self, taker_code, provider_code, inv_number) -> bool:
        command = f'SELECT * FROM LCTOFISENT ' \
                  f'WHERE CODIGOEMPRESA = {taker_code} and CODIGOPESSOA = {provider_code} ' \
                  f'and NUMERONF = {inv_number} and ESPECIENF = \'NFSE\' and SERIENF = \'U\''

        # print(command)
        self.run_command(command)

        # print(self.result())
        return self.result() != ['']

    def get_company_code(self, cnpj: str, _type: int) -> str:
        """
        Retorna o código da empresa com base no seu nome.

        :param cnpj:  CNPJ da empresa.
        :type cnpj:   (str)
        :param _type: Se a empresa em questão é cliente da empresa de contabilidade[0] ou não[1].
        :type _type:  (int)
        """

        cnpj = f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'
        command = f'SELECT CODIGOPESSOA, NOMEPESSOA FROM PESSOA WHERE INSCRFEDERAL = \'{cnpj}\''

        # print('command:', command)
        self.run_command(command)
        result = self.result()

        if not _type:  # cliente
            command = f'SELECT CODIGOEMPRESA FROM EMPRESA WHERE LOWER(NOMEEMPRESA) LIKE LOWER(\'%{result[1]}%\')'
            self.run_command(command)
            result = self.result()

        return result[0]

    def get_city_code(self, city):
        command = f'SELECT CODIGOMUNIC FROM MUNICIPIO WHERE LOWER(NOMEMUNIC) LIKE LOWER(\'%{city}%\')'
        self.run_command(command)
        return self.result()[0]

    def launch_key(self, company_code) -> int:
        command = f'SELECT MAX(CHAVELCTOFISENT) FROM LCTOFISENT WHERE CODIGOEMPRESA = {company_code}'
        self.run_command(command)

        return int(self.result()[0]) + 1

    def lctofisent(self, l: LCTOFISENTData) -> str:
        import datetime

        diff = datetime.timedelta(hours=-3)
        timezone = datetime.timezone(diff)
        now = datetime.datetime.now().astimezone(timezone)

        today = f'{now.year}-{now.month}-{now.day}'
        now_txt = f'{today} {now.hour}:{now.minute}:{now.second}'

        inv = l.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        # print('now:', now_txt)
        # print('codigo estabelecimento:', inv.taker.cnpj[-6:-2])

        command = str()
        if str(inv.service_nature)[-3:] == '308':
            command = f'INSERT INTO LCTOFISENT(CODIGOEMPRESA, CHAVELCTOFISENT, CODIGOESTAB, CODIGOPESSOA, ' \
                      f'NUMERONF, ESPECIENF, SERIENF, DATAENTRADA, DATALCTOFIS, DATAEMISSAO, VALORCONTABIL, ' \
                      f'BASECALCULOIPI, VALORIPI, ISENTASIPI, OUTRASIPI, BASECALCULOFUNRURAL, ALIQFUNRURAL, ' \
                      f'VALORFUNRURAL, CODIGOTIPODCTOSINTEGRA, CDMODELO, VERSAONFE, EMITENTENF, FINALIDADEOPERACAO, ' \
                      f'MEIOPAGAMENTO, MODALIDADEFRETE, CDSITUACAO, CANCELADA, CONCILIADA, CODIGOUSUARIO, ' \
                      f'DATAHORALCTOFIS, ORIGEMDADO) ' \
                      f'VALUES({inv.taker.code}, {l.key}, {int(inv.taker.cnpj[-6:-2])}, {inv.provider.code}, ' \
                      f'{inv.serial_number}, \'NFSE\', \'U\', \'{today}\', ' \
                      f'\'{issuance_date}\', \'{issuance_date}\', {inv.gross_value}, {l.ipi.base}, {l.ipi.value}, ' \
                      f'{l.ipi.exemption}, ' \
                      f'{l.ipi.others}, {l.funrural.base}, {l.funrural.aliquot}, {l.funrural.value}, {99}, ' \
                      f'{inv.doc_type}, {4.00}, \'{inv.issuer}\', {inv.operation_purpose}, {l.payment_method}, {l.freight_category}, ' \
                      f'{inv.invoice_situation}, {int(inv.is_canceled)}, {0}, {238}, \'{now_txt}\', {2})'

        print(command)
        return command

    def run_command(self, command) -> None:
        os.system(fr'py -2 Model\sql_run.py {command.replace(" ", "_")} {self.host} {self.database} {self.user} '
                  fr'{self.password}')

    @staticmethod
    def result() -> list:
        with open(fr'{SYS_PATH}\bd_results.bin', 'rb') as fin:
            arr = fin.read().decode('utf8')
        return arr.split(';')
