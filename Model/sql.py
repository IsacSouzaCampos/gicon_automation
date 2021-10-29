import os
from Model.constants import SYS_PATH
from Model.launch import LCTOFISData
from Model.invoice import Invoice


class SQLCommands:
    def __init__(self, service_type):
        self.service_type = service_type
        self.type_str = 'ENT' if self.service_type else 'SAI'
        self.run = SQLRun()

    def is_launched(self, invoice: Invoice) -> str:
        company_code = self.get_company_code(invoice.taker.fed_id)

        # person_type = 0 if invoice.service_type else 1
        person_code = self.get_company_code(invoice.provider.fed_id)

        command = f'SELECT \'{invoice.taker.fed_id}\', \'{invoice.provider.fed_id}\', NUMERONF ' \
                  f'FROM LCTOFIS{self.type_str} ' \
                  f'WHERE CODIGOEMPRESA = ({company_code}) AND ' \
                  f'CODIGOPESSOA = ({person_code}) ' \
                  f'AND NUMERONF = {invoice.serial_number} AND ESPECIENF = \'NFSE\' AND SERIENF = \'U\''

        # print(command)
        return command

    @staticmethod
    def get_companies_code(launch: LCTOFISData):
        inv = launch.invoice
        if launch.type:  # tomado
            company_id = inv.taker.fed_id
            person_id = inv.provider.fed_id
        else:  # prestado
            person_id = inv.taker.fed_id
            company_id = inv.provider.fed_id

        if len(company_id) == 14:  # CNPJ
            company_id = f'{company_id[:2]}.{company_id[2:5]}.{company_id[5:8]}' \
                         f'/{company_id[8:12]}-{company_id[12:]}'
        elif len(company_id) == 11:  # CPF
            company_id = f'{company_id[:3]}.{company_id[3:6]}.{company_id[6:9]}-{company_id[9:]}'

        if len(person_id) == 14:  # CNPJ
            person_id = f'{person_id[:2]}.{person_id[2:5]}.{person_id[5:8]}' \
                        f'/{person_id[8:12]}-{person_id[12:]}'
        elif len(person_id) == 11:  # CPF
            person_id = f'{person_id[:3]}.{person_id[3:6]}.{person_id[6:9]}-{person_id[9:]}'

        command = f'SELECT C.CODIGOEMPRESA AS CODEMPRESA, P.CODIGOPESSOA AS CODPESSOA ' \
                  f'FROM CLIENTE C, PESSOA P ' \
                  f'WHERE (C.INSCRFEDERAL = \'{company_id}\' AND P.INSCRFEDERAL = \'{person_id}\') '

        return command

    @staticmethod
    def get_company_code(fed_id: str) -> str:
        """
        Retorna o código da empresa com base no seu nome.

        :param fed_id:  CPF/CNPJ da empresa/pessoa.
        :type fed_id:   (str)
        """

        if len(fed_id) == 14:
            fed_id = f'{fed_id[:2]}.{fed_id[2:5]}.{fed_id[5:8]}/{fed_id[8:12]}-{fed_id[12:]}'
        elif len(fed_id) == 11:
            fed_id = f'{fed_id[:3]}.{fed_id[3:6]}.{fed_id[6:9]}-{fed_id[9:]}'

        return f'SELECT CODIGOEMPRESA FROM CLIENTE WHERE INSCRFEDERAL = \'{fed_id}\''

    def lctofis_key(self, company_id) -> str:
        command = f'SELECT MAX(CHAVELCTOFIS{self.type_str}) + 1 FROM LCTOFIS{self.type_str} WHERE CODIGOEMPRESA = ' \
                  f'({self.get_company_code(company_id)})'
        return command

    def lctofisretido_key(self, company_id) -> str:
        if self.service_type:
            command = f'SELECT MAX(CHAVELCTOFIS{self.type_str}RETIDO) + 1 FROM LCTOFIS{self.type_str}RETIDO ' \
                      f'WHERE CODIGOEMPRESA = ({self.get_company_code(company_id)})'
        else:
            command = f'SELECT MAX(CHAVELCTOFIS{self.type_str}) + 1 FROM LCTOFIS{self.type_str}RETIDO ' \
                      f'WHERE CODIGOEMPRESA = ({self.get_company_code(company_id)})'

        return command

    def lctofis(self, launch: LCTOFISData) -> str:
        now = self.current_datetime()

        inv = launch.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        ts = self.type_str
        taker_id = inv.taker.fed_id
        # if str(inv.nature)[-3:] == '308':
        command = f'INSERT INTO ' \
                  f'LCTOFIS{ts}(CODIGOEMPRESA,            CHAVELCTOFIS{ts},         CODIGOESTAB, ' \
                  f'           CODIGOPESSOA,              NUMERONF,                 ESPECIENF, ' \
                  f'           SERIENF,                   DATALCTOFIS,              DATAEMISSAO, ' \
                  f'           VALORCONTABIL,             BASECALCULOIPI,           VALORIPI, ' \
                  f'           ISENTASIPI,                OUTRASIPI,                BASECALCULOFUNRURAL, ' \
                  f'           ALIQFUNRURAL,              VALORFUNRURAL,            CODIGOTIPODCTOSINTEGRA, ' \
                  f'           CDMODELO,                  VERSAONFE,                EMITENTENF, ' \
                  f'           FINALIDADEOPERACAO,        MEIOPAGAMENTO,            MODALIDADEFRETE, ' \
                  f'           CDSITUACAO,                CANCELADA,                CONCILIADA, ' \
                  f'           CODIGOUSUARIO,             DATAHORALCTOFIS,          ORIGEMDADO)\n' \
                  f'SELECT     CODEMPRESA,                {launch.key},             {int(taker_id[-6:-2])}, '\
                  f'           CODPESSOA,                 {inv.serial_number},      \'NFSE\', ' \
                  f'           \'U\',                     \'{issuance_date}\',      \'{issuance_date}\', ' \
                  f'           {inv.gross_value},         {launch.ipi.base},        {launch.ipi.value}, ' \
                  f'           {launch.ipi.exemption},    {launch.ipi.others},      {launch.funrural.base}, ' \
                  f'           {launch.funrural.aliquot}, {launch.funrural.value},  {99}, ' \
                  f'           {inv.doc_type},            {4.00},                   \'{inv.issuer}\', ' \
                  f'           {inv.operation_purpose},   {launch.payment_method},  {launch.freight_category}, ' \
                  f'           {inv.invoice_situation},   {int(inv.is_canceled)},   {0}, ' \
                  f'           {238},                     ({now}),                  {2} \n' \
                  f'FROM (\n' \
                  f'    {self.get_companies_code(launch)}' \
                  f'\n)'

        return command

    def lctofiscfop(self, launch: LCTOFISData) -> str:
        inv = launch.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        tax_aliquot = float(inv.taxes.iss.aliquot) * 100
        tax_value = float(inv.gross_value) * float(inv.taxes.iss.aliquot)

        ts = self.type_str
        # if str(inv.nature)[-3:] == '308':
        taker_id = inv.taker.fed_id
        command = f'INSERT INTO ' \
                  f'LCTOFIS{ts}CFOP(CODIGOEMPRESA,               CHAVELCTOFIS{ts},          CODIGOCFOP, ' \
                  f'               TIPOIMPOSTO,                  ALIQIMPOSTO,               DATALCTOFIS, ' \
                  f'               CODIGOESTAB,                  VALORCONTABILIMPOSTO,      BASECALCULOIMPOSTO,' \
                  f'               VALORIMPOSTO,                 ISENTASIMPOSTO,            OUTRASIMPOSTO, ' \
                  f'               VALOREXVALORADICIONAL) \n' \
                  f'SELECT         CODEMPRESA,                   {launch.key},              {inv.nature}, '\
                  f'               {2},                          {tax_aliquot},             \'{issuance_date}\', '\
                  f'               {int(taker_id[-6:-2])},       {inv.gross_value},         {inv.gross_value}, ' \
                  f'               {tax_value},                  {0},                       {0}, ' \
                  f'               {0} \n' \
                  f'FROM (\n' \
                  f'    {self.get_companies_code(launch)}' \
                  f'\n)'

        # print(command)
        return command

    def lctofisretido(self, launch: LCTOFISData, withheld_key):
        now = self.current_datetime()

        inv = launch.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        taker_comp_num = int(inv.taker.fed_id[-6:-2])

        iss = inv.taxes.iss
        irrf = inv.taxes.irrf
        csrf = inv.taxes.csrf
        pis = csrf.pis
        cofins = csrf.cofins
        csll = csrf.csll

        irrf_value = 0 if not irrf.value else irrf.value
        csrf_value = 0 if not csrf.value else csrf.value
        pis_value = 0 if not pis.value else pis.value
        cofins_value = 0 if not cofins.value else cofins.value
        csll_value = 0 if not csll.value else csll.value

        ts = self.type_str
        command = f'INSERT INTO ' \
                  f'LCTOFIS{ts}RETIDO(CODIGOEMPRESA,        CHAVELCTOFIS{ts}RETIDO,         CODIGOPESSOA, ' \
                  f'                 NUMERONF,              ESPECIENF,                      SERIENF, ' \
                  f'                 DATALCTOFIS,           DATAEMISSAO,                    VALORCONTABIL, ' \
                  f'                 CODIGOESTAB,           CHAVELCTOFIS{ts},               CODIGOCFOP, ' \
                  f'                 BASECALCULOINSS,       ALIQINSS,                       VALORINSS, ' \
                  f'                 BASECALCULOISSQN,      ALIQISSQN,                      VALORISSQN, ' \
                  f'                 BASECALCULOIRPJ,       ALIQIRPJ,                       VALORIRPJ,' \
                  f'                 APURADOIRPJ,' \
                  f'                 BASECALCULOIRRF, ' \
                  f'                 ALIQIRRF,              VALORIRRF,                      CODIGOIMPOSTOIRRF, ' \
                  f'                 VARIACAOIMPOSTOIRRF, ' \
                  f'                 APURADOIRRF,           TOTALPISCOFINSCSLL,             TIPORETPISCOFINSCSLL,' \
                  f'                 BASECALCULOPIS, ' \
                  f'                 ALIQPIS,               VALORPIS,                       CODIGOIMPOSTOPIS, ' \
                  f'                 VARIACAOIMPOSTOPIS, ' \
                  f'                 BASECALCULOCOFINS, ' \
                  f'                 ALIQCOFINS,            VALORCOFINS,                    CODIGOIMPOSTOCOFINS, ' \
                  f'                 VARIACAOIMPOSTOCOFINS, ' \
                  f'                 BASECALCULOCSLL, ' \
                  f'                 ALIQCSLL,              VALORCSLL,                      CODIGOIMPOSTOCSLL, ' \
                  f'                 VARIACAOIMPOSTOCSLL, ' \
                  f'                 APURADOPISCOFINSCSLL,  DATAPGTOPISCOFINSCSLL, '\
                  f'                 CONCILIADA,            CODIGOUSUARIO,                  DATAHORALCTOFIS, ' \
                  f'                 ORIGEMDADO,            CODIGOTABCTBFIS) \n' \
                  f'SELECT          CODEMPRESA,             {withheld_key},                 CODPESSOA, ' \
                  f'                {inv.serial_number},    \'NFSE\',                       \'U\', ' \
                  f'                \'{issuance_date}\',    \'{issuance_date}\',            {inv.gross_value}, ' \
                  f'                {taker_comp_num},       {launch.key},                   {inv.nature}, '\
                  f'                {0},                    {0},                            {0}, ' \
                  f'                {iss.calc_basis},       {float(iss.aliquot) * 100},     {iss.value}, ' \
                  f'                {0},                    {0},                            {0}, ' \
                  f'                {0}, ' \
                  f'                {irrf.calc_basis}, ' \
                  f'                {irrf.aliquot},         {irrf_value},                   {irrf.code}, ' \
                  f'                {irrf.variation}, ' \
                  f'                {0},                    {csrf_value},                   {1}, ' \
                  f'                {pis.calc_basis}, ' \
                  f'                {pis.aliquot},          {pis_value},                    {csrf.code}, ' \
                  f'                {csrf.variation}, ' \
                  f'                {cofins.calc_basis}, ' \
                  f'                {cofins.aliquot},       {cofins_value},                 {csrf.code}, ' \
                  f'                {csrf.variation}, ' \
                  f'                {csll.calc_basis}, ' \
                  f'                {csll.aliquot},         {csll_value},                   {csrf.code}, ' \
                  f'                {csrf.variation}, ' \
                  f'                {0},                    \'{issuance_date}\', ' \
                  f'                {0},                    {238},                          ({now}), ' \
                  f'                {2},                    {838} \n' \
                  f'FROM (\n' \
                  f'    {self.get_companies_code(launch)}' \
                  f'\n)'

        return command

    def lctofisvaloriss(self, launch: LCTOFISData):
        inv = launch.invoice
        iss_aliquot = str(float(inv.taxes.iss.aliquot) * 100).replace('.', ',')

        taker_code = self.get_company_code(inv.taker.fed_id)

        ts = self.type_str
        # if str(inv.nature)[-3:] == '308':
        command = f'INSERT INTO LCTOFIS{ts}VALORISS(' \
                  f'CODIGOEMPRESA,          CHAVELCTOFIS{ts},           CODIGOCAMPO,            VALOR) ' \
                  f'VALUES(' \
                  f'({taker_code}),         {launch.key},               {125},                  {inv.full_cnae});' \
                  f'\n\n' \
                  f'INSERT INTO LCTOFIS{ts}VALORISS(' \
                  f'CODIGOEMPRESA,          CHAVELCTOFIS{ts},           CODIGOCAMPO,            VALOR) ' \
                  f'VALUES(' \
                  f'({taker_code}),         {launch.key},               {126},                  {inv.cst});' \
                  f'\n\n' \
                  f'INSERT INTO LCTOFIS{ts}VALORISS(' \
                  f'CODIGOEMPRESA,          CHAVELCTOFIS{ts},           CODIGOCAMPO,            VALOR) ' \
                  f'VALUES(' \
                  f'({taker_code}),         {launch.key},               {131},                  \'{iss_aliquot}\')'

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
        if not commands:
            return

        # commands = [command.replace(' ', '_') for command in commands]
        commands = ';'.join(commands)
        with open(SYS_PATH + r'\commands.bin', 'w') as fout:
            print(commands, file=fout)
        os.system(fr'py -2 Model\sql_run.py {self.host} {self.database} {self.user} '
                  fr'{self.password}')

    @staticmethod
    def result() -> list:
        with open(fr'{SYS_PATH}\bd_results.bin', 'rb') as fin:
            arr = fin.read().decode('utf8')
        return arr.split()
