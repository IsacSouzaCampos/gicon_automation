from Model.launch import LCTOFISData
from Model.invoice import Invoice


class SQLCommands:
    def __init__(self, service_type):
        self.service_type = service_type
        self.type_str = 'ENT' if self.service_type else 'SAI'
        # self.run = SQLRun()

    def get_company_code(self, fed_id: str, company_type) -> str:
        """
        Retorna o código da empresa com base no seu nome.

        :param fed_id:       CPF/CNPJ da empresa/pessoa.
        :type fed_id:        (str)
        :param company_type: Se a empresa a ser selecionada é a tomadora ou prestadora do serviço
        :type company_type:  (int)
        """

        fed_id = self.format_fed_id(fed_id)

        client_command = f'SELECT CODIGOEMPRESA FROM CLIENTE WHERE INSCRFEDERAL = \'{fed_id}\''
        person_command = f'SELECT CODIGOPESSOA FROM PESSOA WHERE INSCRFEDERAL = \'{fed_id}\''

        # CORRIGIR ESSE RETORNO
        return client_command if self.service_type == company_type else person_command

    def lctofisretido(self, launch: LCTOFISData):
        invoice = launch.invoice
        now = self.current_datetime()

        issuance_date = invoice.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        iss = invoice.taxes.iss
        irrf = invoice.taxes.irrf
        csrf = invoice.taxes.csrf
        pis = csrf.pis
        cofins = csrf.cofins
        csll = csrf.csll

        iss.value = float(0 if (not iss.value or invoice.is_canceled) else iss.value)
        irrf.value = 0 if (not irrf.value or invoice.is_canceled) else irrf.value
        csrf.value = 0 if (not csrf.value or invoice.is_canceled) else csrf.value
        pis.value = 0 if (not pis.value or invoice.is_canceled) else pis.value
        cofins.value = 0 if (not cofins.value or invoice.is_canceled) else cofins.value
        csll.value = 0 if (not csll.value or invoice.is_canceled) else csll.value

        iss.aliquot = round((iss.value / invoice.gross_value), 2)
        irrf.aliquot = round((irrf.value / invoice.gross_value) * 100, 2)
        csrf.aliquot = round((csrf.value / invoice.gross_value) * 100, 2)
        pis.aliquot = round((pis.value / invoice.gross_value) * 100, 2)
        cofins.aliquot = round((cofins.value / invoice.gross_value) * 100, 2)
        csll.aliquot = round((csll.value / invoice.gross_value) * 100, 2)

        iss.calc_basis = invoice.gross_value if iss.value else 0
        irrf.calc_basis = invoice.gross_value if irrf.value else 0
        csrf.calc_basis = invoice.gross_value if csrf.value else 0
        pis.calc_basis = invoice.gross_value if pis.value else 0
        cofins.calc_basis = invoice.gross_value if cofins.value else 0
        csll.calc_basis = invoice.gross_value if csll.value else 0

        iss_situation = 1
        irrf_situation = 1
        irpj_situation = 1
        pis_situation = 1
        cofins_situation = 1
        csll_situation = 1

        ts = self.type_str
        client = invoice.client
        person = invoice.person

        if self.service_type:  # se tomado
            key = f'SELECT CHAVELCTOFISSAI FROM LCTOFISSAI WHERE CODIGOEMPRESA = {client.code} AND ' \
                  f'CODIGOPESSOA = ({person.code}) AND NUMERONF = {invoice.serial_number}'
            command = f'INSERT INTO ' \
                      f'LCTOFIS{ts}RETIDO(CODIGOEMPRESA,        CHAVELCTOFIS{ts}RETIDO,         CODIGOPESSOA, ' \
                      f'                 NUMERONF,              ESPECIENF,                      SERIENF, ' \
                      f'                 DATALCTOFIS,           DATAEMISSAO,                    VALORCONTABIL, ' \
                      f'                 CODIGOESTAB,           CHAVELCTOFIS{ts},               CODIGOCFOP, ' \
                      f'                 BASECALCULOINSS,       ALIQINSS,                       VALORINSS, ' \
                      f'                 BASECALCULOISSQN,      ALIQISSQN,                      VALORISSQN, ' \
                      f'                 DATAPREVISSQN, ' \
                      f'                 BASECALCULOIRPJ,       ALIQIRPJ,                       VALORIRPJ,' \
                      f'                 APURADOIRPJ,' \
                      f'                 BASECALCULOIRRF, ' \
                      f'                 ALIQIRRF,              VALORIRRF,                      DATAPREVIRRFIRPJ, ' \
                      f'                 CODIGOIMPOSTOIRRF, ' \
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
                      f'                 APURADOPISCOFINSCSLL,  DATAPREVPISCOFINSCSLL, '\
                      f'                 CONCILIADA,            CODIGOUSUARIO,                  DATAHORALCTOFIS, ' \
                      f'                 ORIGEMDADO,            CODIGOTABCTBFIS) \n' \
                      f'VALUES          (({client.code}),       ({key}),                        ({person.code}), ' \
                      f'                {invoice.serial_number},\'NFSE\',                       {invoice.serie}, ' \
                      f'                \'{issuance_date}\',    \'{issuance_date}\',           {invoice.gross_value}, '\
                      f'                {client.estab_num},     ({key}),                        {invoice.nature}, '\
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {iss.calc_basis},       {float(iss.aliquot) * 100},     {iss.value}, ' \
                      f'                \'{issuance_date}\'' \
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {0}, ' \
                      f'                {irrf.calc_basis}, ' \
                      f'                {irrf.aliquot},         {irrf.value},                   \'{issuance_date}\', ' \
                      f'                {irrf.code}, ' \
                      f'                {irrf.variation}, ' \
                      f'                {0},                    {csrf.value},                   {1}, ' \
                      f'                {pis.calc_basis}, ' \
                      f'                {pis.aliquot},          {pis.value},                    {csrf.code}, ' \
                      f'                {csrf.variation}, ' \
                      f'                {cofins.calc_basis}, ' \
                      f'                {cofins.aliquot},       {cofins.value},                 {csrf.code}, ' \
                      f'                {csrf.variation}, ' \
                      f'                {csll.calc_basis}, ' \
                      f'                {csll.aliquot},         {csll.value},                   {csrf.code}, ' \
                      f'                {csrf.variation}, ' \
                      f'                {0},                    \'{issuance_date}\', ' \
                      f'                {0},                    {238},                          ({now}), ' \
                      f'                {3},                    {838})'

        else:
            key = f'SELECT CHAVELCTOFISSAI FROM LCTOFISSAI WHERE CODIGOEMPRESA = {client.code} AND ' \
                  f'CODIGOPESSOA = ({person.code}) AND NUMERONF = {invoice.serial_number}'
            withheld_type = invoice.withheld_type
            command = f'INSERT INTO ' \
                      f'LCTOFIS{ts}RETIDO(CODIGOEMPRESA,        CHAVELCTOFIS{ts}, ' \
                      f'                 DATALCTOFIS,           TIPORETENCAO, ' \
                      f'                 CODIGOESTAB, ' \
                      f'                 BASECALCULOINSS,       ALIQINSS,                       VALORINSS, ' \
                      f'                 BASECALCULOISSQN,      ALIQISSQN,                      VALORISSQN, ' \
                      f'                 DATAPREVISSQN, ' \
                      f'                 BASECALCULOIRPJ,       ALIQIRPJ,                       VALORIRPJ,' \
                      f'                 BASECALCULOIRRF, ' \
                      f'                 ALIQIRRF,              VALORIRRF,                      DATAPREVIRRFIRPJ, ' \
                      f'                 CODIGOIMPOSTOIRRF, ' \
                      f'                 VARIACAOIMPOSTOIRRF, ' \
                      f'                 TOTALPISCOFINSCSLL, ' \
                      f'                 BASECALCULOPIS, ' \
                      f'                 ALIQPIS,               VALORPIS,                       CODIGOIMPOSTOPIS, ' \
                      f'                 VARIACAOIMPOSTOPIS, ' \
                      f'                 BASECALCULOCOFINS, ' \
                      f'                 ALIQCOFINS,            VALORCOFINS,                    CODIGOIMPOSTOCOFINS, ' \
                      f'                 VARIACAOIMPOSTOCOFINS, ' \
                      f'                 BASECALCULOCSLL, ' \
                      f'                 ALIQCSLL,              VALORCSLL,                      CODIGOIMPOSTOCSLL, ' \
                      f'                 VARIACAOIMPOSTOCSLL, ' \
                      f'                 DATAPREVPISCOFINSCSLL, ' \
                      f'                 CONCILIADA,            CODIGOUSUARIO,                  DATAHORALCTOFIS, ' \
                      f'                 SITUACAOISSQN,         SITUACAOIRRF,                   SITUACAOIRPJ, ' \
                      f'                 SITUACAOPIS,           SITUACAOCOFINS,                 SITUACAOCSLL) \n' \
                      f'VALUES          (({client.code}),       ({key}), ' \
                      f'                \'{issuance_date}\',    ({withheld_type}), ' \
                      f'                {client.estab_num}, ' \
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {iss.calc_basis},       {float(iss.aliquot) * 100},     {iss.value}, ' \
                      f'                \'{issuance_date}\', ' \
                      f'                {0},                    {0},                            {0}, ' \
                      f'                {irrf.calc_basis}, ' \
                      f'                {irrf.aliquot},         {irrf.value},                   \'{issuance_date}\', ' \
                      f'                {irrf.code}, ' \
                      f'                {irrf.variation}, ' \
                      f'                {csrf.value}, ' \
                      f'                {pis.calc_basis}, ' \
                      f'                {pis.aliquot},          {pis.value},                    {csrf.code}, ' \
                      f'                {csrf.variation}, ' \
                      f'                {cofins.calc_basis}, ' \
                      f'                {cofins.aliquot},       {cofins.value},                 {csrf.code}, ' \
                      f'                {csrf.variation}, ' \
                      f'                {csll.calc_basis}, ' \
                      f'                {csll.aliquot},         {csll.value},                   {csrf.code}, ' \
                      f'                {csrf.variation}, ' \
                      f'                \'{issuance_date}\', ' \
                      f'                {0},                    {238},                          ({now}), ' \
                      f'                {iss_situation},        {irrf_situation},               {irpj_situation}, ' \
                      f'                {pis_situation},        {cofins_situation},             {csll_situation})'

        return command

    @staticmethod
    def update_lctofiscfop(invoice: Invoice):
        command = f'UPDATE LCTOFISSAICFOP ' \
                  f'SET VALORCONTABILIMPOSTO = 0, BASECALCULOIMPOSTO = 0, ALIQIMPOSTO = 0, VALORIMPOSTO = 0, ' \
                  f'ISENTASIMPOSTO = 0, OUTRASIMPOSTO = 0, VALOREXVALORADICIONAL = 0 ' \
                  f'WHERE CODIGOEMPRESA = ({invoice.client.code}) AND CHAVELCTOFISSAI = ' \
                  f'(SELECT CHAVELCTOFISSAI FROM LCTOFISSAI ' \
                  f'WHERE CODIGOEMPRESA = ({invoice.client.code}) AND ' \
                  f'CODIGOPESSOA = ({invoice.person.code}) AND NUMERONF = {invoice.serial_number})'

        return command

    @staticmethod
    def current_datetime():
        return 'SELECT CAST(\'NOW\' AS TIMESTAMP) FROM RDB$DATABASE'

    @staticmethod
    def format_fed_id(fed_id):
        if len(fed_id) == 14:
            fed_id = f'{fed_id[:2]}.{fed_id[2:5]}.{fed_id[5:8]}/{fed_id[8:12]}-{fed_id[12:]}'
        elif len(fed_id) == 11:
            fed_id = f'{fed_id[:3]}.{fed_id[3:6]}.{fed_id[6:9]}-{fed_id[9:]}'
        return fed_id
