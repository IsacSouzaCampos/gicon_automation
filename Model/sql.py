import os
from Model.constants import SYS_PATH
from Model.launch import LCTOFISENTData
from Model.invoice import Invoice


class SQLCommands:
    def __init__(self):
        self.run = SQLRun()

    def launched(self, invoice: Invoice) -> str:
        if invoice.service_type:
            company_code = self.get_company_code(invoice.taker.cnpj, 0)
            person_code = self.get_company_code(invoice.provider.cnpj, 1)
        else:
            person_code = self.get_company_code(invoice.provider.cnpj, 0)
            company_code = self.get_company_code(invoice.taker.cnpj, 1)

        command = f'SELECT {invoice.taker.cnpj}, {invoice.provider.cnpj}, NUMERONF FROM LCTOFISENT ' \
                  f'WHERE CODIGOEMPRESA = ({company_code}) AND ' \
                  f'CODIGOPESSOA = ({person_code}) ' \
                  f'AND NUMERONF = {invoice.serial_number} AND ESPECIENF = \'NFSE\' AND SERIENF = \'U\''

        return command

    @staticmethod
    def get_company_code(cnpj: str, _type: int) -> str:
        """
        Retorna o código da empresa com base no seu nome.

        :param cnpj:  CNPJ da empresa.
        :type cnpj:   (str)
        :param _type: Se a empresa em questão é o cliente da gicon[0] ou não[1].
        :type _type:  (int)
        """

        cnpj = f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'
        if _type:
            return f'SELECT CODIGOPESSOA FROM PESSOA WHERE INSCRFEDERAL = \'{cnpj}\''
        return f'SELECT CODIGOCLIENTE FROM CLIENTE WHERE INSCRFEDERAL = \'{cnpj}\''

    # @staticmethod
    # def get_city_code(self, city):
    #     command = f'SELECT CODIGOMUNIC FROM MUNICIPIO WHERE LOWER(NOMEMUNIC) LIKE LOWER(\'%{city}%\')'
    #     return command

    @staticmethod
    def lctofisent_key(company_code) -> str:
        command = f'SELECT MAX(CHAVELCTOFISENT) FROM LCTOFISENT WHERE CODIGOEMPRESA = {company_code}'

        return command

    @staticmethod
    def lctofisentretido_key(company_code) -> str:
        command = f'SELECT MAX(CHAVELCTOFISENTRETIDO) FROM LCTOFISENTRETIDO WHERE CODIGOEMPRESA = {company_code}'
        # self.run_command(command)

        # return int(self.result()[0]) + 1
        return command

    def lctofisent(self, launch: LCTOFISENTData) -> str:

        # INSERT INTO LCTOFISENT(CODIGOEMPRESA, CHAVELCTOFISENT, CODIGOESTAB, CODIGOPESSOA, NUMERONF,
        # ESPECIENF, SERIENF, DATALCTOFIS, DATAEMISSAO, VALORCONTABIL, BASECALCULOIPI, VALORIPI, ISENTASIPI,
        # OUTRASIPI, BASECALCULOFUNRURAL, ALIQFUNRURAL, VALORFUNRURAL, CODIGOTIPODCTOSINTEGRA, CDMODELO,
        # VERSAONFE, EMITENTENF, FINALIDADEOPERACAO, MEIOPAGAMENTO, MODALIDADEFRETE, CDSITUACAO, CANCELADA,
        # CONCILIADA, CODIGOUSUARIO, DATAHORALCTOFIS, ORIGEMDADO)
        # SELECT L.CODIGOEMPRESA, ((SELECT MAX(CHAVELCTOFISENT) FROM LCTOFISENT WHERE CODIGOEMPRESA = 421) + 1),
        # 1, L.CODIGOPESSOA, 12345, 'NFSE', 'U', '2021-07-30', '2021-07-30', 3952.0, 0, 0, 0, 0, 0, 0, 0,
        # 99, 99, 4.0, 'T', 1, 99, 9, 0, 0, 0, 238, '2021-10-8 16:21:32', 2
        # FROM LCTOFISENT L
        # WHERE NOT EXISTS(SELECT * FROM LCTOFISENT
        # WHERE CODIGOEMPRESA = 421 AND CODIGOPESSOA = 25287 AND NUMERONF = 12345 AND ESPECIENF = 'NFSE'
        # AND SERIENF = 'U') AND CODIGOEMPRESA = 421 AND CODIGOPESSOA = 25287
        # GROUP BY L.CODIGOEMPRESA, L.CODIGOPESSOA

        now = self.current_datetime()

        inv = launch.invoice
        if launch.type:  # tomado
            company_cnpj = inv.taker.cnpj
            person_cnpj = inv.provider.cnpj
        else:  # prestado
            person_cnpj = inv.taker.cnpj
            company_cnpj = inv.provider.cnpj

        company_cnpj = f'{company_cnpj[:2]}.{company_cnpj[2:5]}.{company_cnpj[5:8]}' \
                       f'/{company_cnpj[8:12]}-{company_cnpj[12:]}'
        person_cnpj = f'{person_cnpj[:2]}.{person_cnpj[2:5]}.{person_cnpj[5:8]}' \
                      f'/{person_cnpj[8:12]}-{person_cnpj[12:]}'

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        lctofisent_key = f'(({self.lctofisent_key("CODEMPRESA")}) + 1)'

        command = str()
        if str(inv.service_nature)[-3:] == '308':
            command = f'INSERT INTO ' \
                      f'LCTOFISENT(CODIGOEMPRESA,             CHAVELCTOFISENT,          CODIGOESTAB, ' \
                      f'           CODIGOPESSOA,              NUMERONF,                 ESPECIENF, ' \
                      f'           SERIENF,                   DATALCTOFIS,              DATAEMISSAO, ' \
                      f'           VALORCONTABIL,             BASECALCULOIPI,           VALORIPI, ' \
                      f'           ISENTASIPI,                OUTRASIPI,                BASECALCULOFUNRURAL, ' \
                      f'           ALIQFUNRURAL,              VALORFUNRURAL,            CODIGOTIPODCTOSINTEGRA, ' \
                      f'           CDMODELO,                  VERSAONFE,                EMITENTENF, ' \
                      f'           FINALIDADEOPERACAO,        MEIOPAGAMENTO,            MODALIDADEFRETE, ' \
                      f'           CDSITUACAO,                CANCELADA,                CONCILIADA, ' \
                      f'           CODIGOUSUARIO,             DATAHORALCTOFIS,          ORIGEMDADO)\n' \
                      f'SELECT     CODEMPRESA,                {lctofisent_key},         {int(inv.taker.cnpj[-6:-2])}, '\
                      f'           CODPESSOA,                 {inv.serial_number},      \'NFSE\', ' \
                      f'           \'U\',                     \'{issuance_date}\',      \'{issuance_date}\', ' \
                      f'           {inv.gross_value},         {launch.ipi.base},        {launch.ipi.value}, ' \
                      f'           {launch.ipi.exemption},    {launch.ipi.others},      {launch.funrural.base}, ' \
                      f'           {launch.funrural.aliquot}, {launch.funrural.value},  {99}, ' \
                      f'           {inv.doc_type},            {4.00},                   \'{inv.issuer}\', ' \
                      f'           {inv.operation_purpose},   {launch.payment_method},  {launch.freight_category}, ' \
                      f'           {inv.invoice_situation},   {int(inv.is_canceled)},   {0}, ' \
                      f'           {238},                     ({now}),                  {2}\n' \
                      f'FROM (\n' \
                      f'    SELECT C.CODIGOEMPRESA AS CODEMPRESA, P.CODIGOPESSOA AS CODPESSOA ' \
                      f'    FROM CLIENTE C, PESSOA P ' \
                      f'    WHERE (C.INSCRFEDERAL = \'{company_cnpj}\' AND P.INSCRFEDERAL = \'{person_cnpj}\')' \
                      f'\n)\n' \
                      f'WHERE NOT EXISTS(SELECT * FROM LCTOFISENT WHERE CODIGOEMPRESA = CODEMPRESA AND ' \
                      f'CODIGOPESSOA = CODPESSOA AND NUMERONF = {inv.serial_number} AND ' \
                      f'ESPECIENF = \'NFSE\' AND SERIENF = \'U\')\n' \
                      f'GROUP BY CODEMPRESA, CODPESSOA'

        # print(command)
        return command

    def lctofisentcfop(self, launch: LCTOFISENTData) -> str:
        inv = launch.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        tax_aliquot = float(inv.aliquot) * 100
        tax_value = float(inv.gross_value) * float(inv.aliquot)
        lctofisent_key = f'({self.lctofisent_key(inv.taker.code)})'

        command = str()
        if str(inv.service_nature)[-3:] == '308':
            command = f'INSERT INTO ' \
                      f'LCTOFISENTCFOP(CODIGOEMPRESA,                CHAVELCTOFISENT,           CODIGOCFOP, ' \
                      f'               TIPOIMPOSTO,                  ALIQIMPOSTO,               DATALCTOFIS, ' \
                      f'               CODIGOESTAB,                  VALORCONTABILIMPOSTO,      BASECALCULOIMPOSTO,' \
                      f'               VALORIMPOSTO,                 ISENTASIMPOSTO,            OUTRASIMPOSTO, ' \
                      f'               VALOREXVALORADICIONAL) ' \
                      f'VALUES(        {inv.taker.code},             {lctofisent_key},          {inv.service_nature}, '\
                      f'               {2},                          {tax_aliquot},             \'{issuance_date}\', '\
                      f'               {int(inv.taker.cnpj[-6:-2])}, {inv.gross_value},         {inv.gross_value}, ' \
                      f'               {tax_value},                  {0},                       {0}, ' \
                      f'               {0})'

        # print(command)
        return command

    def lctofisentretido(self, launch: LCTOFISENTData):
        now = self.current_datetime()

        inv = launch.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        taker_comp_num = int(inv.taker.cnpj[-6:-2])
        issqn_value = float(inv.gross_value) * float(inv.aliquot)
        issqn_aliquot = float(inv.aliquot) * 100

        lctofisentretido_key = f'(({self.lctofisentretido_key(inv.taker.code)}) + 1)'
        lctofisent_key = f'({self.lctofisent_key(inv.taker.code)})'

        command = str()
        if str(inv.service_nature)[-3:] == '308':
            command = f'INSERT INTO ' \
                      f'LCTOFISENTRETIDO(CODIGOEMPRESA,         CHAVELCTOFISENTRETIDO,          CODIGOPESSOA, ' \
                      f'                 NUMERONF,              ESPECIENF,                      SERIENF, ' \
                      f'                 DATALCTOFIS,           DATAEMISSAO,                    VALORCONTABIL, ' \
                      f'                 CODIGOESTAB,           CHAVELCTOFISENT,                CODIGOCFOP, ' \
                      f'                 BASECALCULOINSS,       ALIQINSS,                       VALORINSS, ' \
                      f'                 BASECALCULOISSQN,      ALIQISSQN,                      VALORISSQN, ' \
                      f'                 BASECALCULOIRPJ,       ALIQIRPJ,                       VALORIRPJ,' \
                      f'                 APURADOIRPJ,' \
                      f'                 BASECALCULOIRRF, ' \
                      f'                 ALIQIRRF,              VALORIRRF,                      ' \
                      f'                 APURADOIRRF,           TOTALPISCOFINSCSLL,             TIPORETPISCOFINSCSLL,' \
                      f'                 BASECALCULOPIS, ' \
                      f'                 ALIQPIS,               VALORPIS,                       BASECALCULOCOFINS, ' \
                      f'                 ALIQCOFINS,            VALORCOFINS,                    BASECALCULOCSLL, ' \
                      f'                 ALIQCSLL,              VALORCSLL,                      APURADOPISCOFINSCSLL, '\
                      f'                 CONCILIADA,            CODIGOUSUARIO,                  DATAHORALCTOFIS, ' \
                      f'                 ORIGEMDADO,            CODIGOTABCTBFIS) ' \
                      f'VALUES(         {inv.taker.code},       {lctofisentretido_key},         {inv.provider.code}, ' \
                      f'                {inv.serial_number},    \'NFSE\',                       \'U\', ' \
                      f'                \'{issuance_date}\',    \'{issuance_date}\',            {inv.gross_value}, ' \
                      f'                {taker_comp_num},       {lctofisent_key},               {inv.service_nature}, '\
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {inv.gross_value},      {issqn_aliquot},                {issqn_value}, ' \
                      f'                {0},                    {0},                            {0},' \
                      f'                {0},' \
                      f'                {0}, ' \
                      f'                {0},                    {0},                            ' \
                      f'                {0},                    {0},                            {0},' \
                      f'                {0}, ' \
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {0},                    {238},                          \'{now}\', ' \
                      f'                {2},                    {838})'

        return command

    def lctofisentvaloriss(self, launch: LCTOFISENTData):
        inv = launch.invoice
        iss_aliquot = str(float(inv.aliquot) * 100).replace('.', ',')

        lctofisent_key = f'({self.lctofisent_key(inv.taker.code)})'

        command = str()
        if str(inv.service_nature)[-3:] == '308':
            command = f'INSERT INTO LCTOFISENTVALORISS(' \
                      f'CODIGOEMPRESA,          CHAVELCTOFISENT,            CODIGOCAMPO,            VALOR) ' \
                      f'VALUES(' \
                      f'{inv.taker.code},       {lctofisent_key},           {125},                  {inv.full_cnae});' \
                      f'\n\n' \
                      f'INSERT INTO LCTOFISENTVALORISS(' \
                      f'CODIGOEMPRESA,          CHAVELCTOFISENT,            CODIGOCAMPO,            VALOR) ' \
                      f'VALUES(' \
                      f'{inv.taker.code},       {lctofisent_key},           {126},                  {inv.cst});' \
                      f'\n\n' \
                      f'INSERT INTO LCTOFISENTVALORISS(' \
                      f'CODIGOEMPRESA,          CHAVELCTOFISENT,            CODIGOCAMPO,            VALOR) ' \
                      f'VALUES(' \
                      f'{inv.taker.code},       {lctofisent_key},           {131},                  \'{iss_aliquot}\')'

        return command

    @staticmethod
    def current_datetime():
        return 'SELECT CAST(\'NOW\' AS TIMESTAMP) FROM RDB$DATABASE'


class SQLRun:
    def __init__(self, host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB', user='SYSDBA',
                 password='masterkey'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def run(self, commands):
        commands = [command.replace(' ', '_') for command in commands]
        commands = ';'.join(commands)
        os.system(fr'py -2 Model\sql_run.py {commands} {self.host} {self.database} {self.user} '
                  fr'{self.password}')

    @staticmethod
    def result() -> list:
        with open(fr'{SYS_PATH}\bd_results.bin', 'rb') as fin:
            arr = fin.read().decode('utf8')
        return arr.split()
