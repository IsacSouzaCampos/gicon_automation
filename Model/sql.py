import os
from Model.constants import SYS_PATH
from Model.launch import LCTOFISENTData
from Model.invoice import Invoice


class SQL:
    def __init__(self, host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB', user='SYSDBA',
                 password='masterkey'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def invoice_in_bd(self, invoice: Invoice) -> bool:
        command = f'SELECT * FROM LCTOFISENT ' \
                  f'WHERE CODIGOEMPRESA = {invoice.taker.code} and CODIGOPESSOA = {invoice.provider.code} ' \
                  f'and NUMERONF = {invoice.serial_number} and ESPECIENF = \'NFSE\' and SERIENF = \'U\''

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

    @staticmethod
    def lctofisent_key(company_code) -> str:
        command = f'SELECT MAX(CHAVELCTOFISENT) FROM LCTOFISENT WHERE CODIGOEMPRESA = {company_code}'
        # self.run_command(command)

        # return int(self.result()[0]) + 1
        return command

    @staticmethod
    def lctofisentretido_key(company_code) -> str:
        command = f'SELECT MAX(CHAVELCTOFISENTRETIDO) FROM LCTOFISENTRETIDO WHERE CODIGOEMPRESA = {company_code}'
        # self.run_command(command)

        # return int(self.result()[0]) + 1
        return command

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

        lctofisent_key = f'(({self.lctofisent_key(inv.taker.code)}) + 1)'

        command = str()
        if str(inv.service_nature)[-3:] == '308':
            command = f'INSERT INTO ' \
                      f'LCTOFISENT(CODIGOEMPRESA,           CHAVELCTOFISENT,        CODIGOESTAB,         ' \
                      f'           CODIGOPESSOA,            NUMERONF,               ESPECIENF, ' \
                      f'           SERIENF,                 DATALCTOFIS,            DATAEMISSAO, ' \
                      f'           VALORCONTABIL,           BASECALCULOIPI,         VALORIPI, ' \
                      f'           ISENTASIPI,              OUTRASIPI,              BASECALCULOFUNRURAL, ' \
                      f'           ALIQFUNRURAL,            VALORFUNRURAL,          CODIGOTIPODCTOSINTEGRA, ' \
                      f'           CDMODELO,                VERSAONFE,              EMITENTENF, ' \
                      f'           FINALIDADEOPERACAO,      MEIOPAGAMENTO,          MODALIDADEFRETE, ' \
                      f'           CDSITUACAO,              CANCELADA,              CONCILIADA, ' \
                      f'           CODIGOUSUARIO,           DATAHORALCTOFIS,        ORIGEMDADO) ' \
                      f'VALUES(    {inv.taker.code},        {lctofisent_key},       {int(inv.taker.cnpj[-6:-2])}, ' \
                      f'           {inv.provider.code},     {inv.serial_number},    \'NFSE\', ' \
                      f'           \'U\',                   \'{issuance_date}\',      \'{issuance_date}\', ' \
                      f'           {inv.gross_value},       {l.ipi.base},           {l.ipi.value}, ' \
                      f'           {l.ipi.exemption},       {l.ipi.others},         {l.funrural.base}, ' \
                      f'           {l.funrural.aliquot},    {l.funrural.value},     {99}, ' \
                      f'           {inv.doc_type},          {4.00},                 \'{inv.issuer}\', ' \
                      f'           {inv.operation_purpose}, {l.payment_method},     {l.freight_category}, ' \
                      f'           {inv.invoice_situation}, {int(inv.is_canceled)}, {0}, ' \
                      f'           {238},                   \'{now_txt}\',          {2})'

        # print(command)
        return command

    def lctofisentcfop(self, l: LCTOFISENTData) -> str:
        inv = l.invoice

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

    def lctofisentretido(self, l: LCTOFISENTData):
        import datetime

        diff = datetime.timedelta(hours=-3)
        timezone = datetime.timezone(diff)
        now = datetime.datetime.now().astimezone(timezone)

        today = f'{now.year}-{now.month}-{now.day}'
        now_txt = f'{today} {now.hour}:{now.minute}:{now.second}'

        inv = l.invoice

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
                      f'                 CONCILIADA,                     CODIGOUSUARIO,         DATAHORALCTOFIS, ' \
                      f'                 ORIGEMDADO) ' \
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
                      f'                {0},                    {238},                          \'{now_txt}\', ' \
                      f'                {2})'

        return command

    def lctofisentvaloriss(self, l: LCTOFISENTData):
        inv = l.invoice
        iss_aliquot = float(inv.aliquot) * 100

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
                      f'{inv.taker.code},       {lctofisent_key},           {131},                  {iss_aliquot})'

        return command

    def run_command(self, command) -> None:
        os.system(fr'py -2 Model\sql_run.py {command.replace(" ", "_")} {self.host} {self.database} {self.user} '
                  fr'{self.password}')

    @staticmethod
    def result() -> list:
        with open(fr'{SYS_PATH}\bd_results.bin', 'rb') as fin:
            arr = fin.read().decode('utf8')
        return arr.split(';')
