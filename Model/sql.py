# import os
# from Model.constants import SYS_PATH
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

    def lctofis_key(self, company_code, index=1) -> str:
        command = f'SELECT MAX(CHAVELCTOFIS{self.type_str}) + {index} FROM LCTOFIS{self.type_str} ' \
                  f'WHERE CODIGOEMPRESA = ({company_code})'
        return command

    def lctofisretido_key(self, company_code) -> str:
        if self.service_type:
            command = f'SELECT MAX(CHAVELCTOFIS{self.type_str}RETIDO) + 1 FROM LCTOFIS{self.type_str}RETIDO ' \
                      f'WHERE CODIGOEMPRESA = ({company_code})'
        else:
            command = f'SELECT MAX(CHAVELCTOFIS{self.type_str}) + 1 FROM LCTOFIS{self.type_str}RETIDO ' \
                      f'WHERE CODIGOEMPRESA = ({company_code})'

        return command

    def lctofis(self, launch: LCTOFISData, key) -> str:
        now = self.current_datetime()

        inv = launch.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        ts = self.type_str

        client = inv.client
        # client_id = inv.taker.fed_id if self.service_type else inv.provider.fed_id
        # client_code = inv.taker.code if self.service_type else inv.provider.code
        # person_id = inv.provider.fed_id if not self.service_type else inv.taker.fed_id
        person_code = inv.provider.code if self.service_type else inv.taker.code
        if self.service_type:
            command = f'INSERT INTO ' \
                  f'LCTOFIS{ts}(CODIGOEMPRESA,            CHAVELCTOFIS{ts},         CODIGOESTAB, ' \
                  f'           CODIGOPESSOA,              NUMERONF,                 ESPECIENF, ' \
                  f'           SERIENF,                   DATALCTOFIS,              DATAEMISSAO, ' \
                  f'           VALORCONTABIL,             BASECALCULOIPI,           VALORIPI, ' \
                  f'           ISENTASIPI,                OUTRASIPI,                BASECALCULOFUNRURAL, ' \
                  f'           ALIQFUNRURAL,              VALORFUNRURAL,            CODIGOTIPODCTOSINTEGRA, ' \
                  f'           CDMODELO,                  EMITENTENF, ' \
                  f'           FINALIDADEOPERACAO,        MEIOPAGAMENTO,            MODALIDADEFRETE, ' \
                  f'           CDSITUACAO,                CANCELADA,                CONCILIADA, ' \
                  f'           CODIGOUSUARIO,             DATAHORALCTOFIS,          ORIGEMDADO) ' \
                  f'VALUES     (({client.code}),          ({key}),                  {client.estab_num}, '\
                  f'           ({person_code}),           {inv.serial_number},      \'NFSE\', ' \
                  f'           {inv.serie},               \'{issuance_date}\',      \'{issuance_date}\', ' \
                  f'           {inv.gross_value},         {launch.ipi.base},        {launch.ipi.value}, ' \
                  f'           {launch.ipi.exemption},    {launch.ipi.others},      {launch.funrural.base}, ' \
                  f'           {launch.funrural.aliquot}, {launch.funrural.value},  {99}, ' \
                  f'           {inv.doc_type},            \'{inv.issuer}\', ' \
                  f'           {inv.operation_purpose},   {launch.payment_method},  {launch.freight_category}, ' \
                  f'           {inv.invoice_situation},   {int(inv.is_canceled)},   {0}, ' \
                  f'           {238},                     ({now}),                  {3})'

        else:
            command = 'INSERT INTO LCTOFISSAI(' \
                      '                     CODIGOEMPRESA,                      CHAVELCTOFISSAI, ' \
                      '                     CODIGOESTAB,                        CODIGOPESSOA, ' \
                      '                     NUMERONF,                           NUMERONFFINAL, ' \
                      '                     ESPECIENF,                          SERIENF, ' \
                      '                     DATALCTOFIS,                        VALORCONTABIL, ' \
                      '                     BASECALCULOIPI,                     VALORIPI, ' \
                      '                     ISENTASIPI,                         OUTRASIPI, ' \
                      '                     CODIGOTIPODCTOSINTEGRA,             CDMODELO, ' \
                      '                     VERSAONFE,                          EMITENTENF, ' \
                      '                     FINALIDADEOPERACAO,                 MEIOPAGAMENTO, ' \
                      '                     MODALIDADEFRETE,                    CDSITUACAO, ' \
                      '                     CANCELADA,                          CONCILIADA, ' \
                      '                     CODIGOUSUARIO,                      DATAHORALCTOFIS, ' \
                      '                     ORIGEMDADO,                         ACRESCIMOFINANCEIRO, ' \
                      '                     CONTRIBUINTE) ' \
                      f'VALUES              (({client.code}),                   ({key}), ' \
                      f'                    {client.estab_num},                 ({person_code}), ' \
                      f'                    {inv.serial_number},                {inv.serial_number}, ' \
                      f'                    \'NFSE\',                           {inv.serie}, ' \
                      f'                    \'{issuance_date}\',                {inv.gross_value}, ' \
                      f'                    {launch.ipi.base},                  {launch.ipi.value}, ' \
                      f'                    {launch.ipi.exemption},             {launch.ipi.others}, ' \
                      f'                    {99},                               {inv.doc_type}, ' \
                      f'                    {4.00},                             \'{inv.issuer}\', ' \
                      f'                    {inv.operation_purpose},            {launch.payment_method}, ' \
                      f'                    {launch.freight_category},          {inv.invoice_situation}, ' \
                      f'                    {int(inv.is_canceled)},             {0}, ' \
                      f'                    {238},                              ({now}), ' \
                      f'                    {3},                                {0}, ' \
                      f'                    {0})'

        return command

    def lctofiscfop(self, launch: LCTOFISData, key) -> str:
        inv = launch.invoice

        issuance_date = inv.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        tax_aliquot = float(inv.taxes.iss.aliquot) * 100
        tax_value = float(inv.gross_value) * float(inv.taxes.iss.aliquot)

        ts = self.type_str
        client = inv.client
        # client_id = inv.taker.fed_id if self.service_type else inv.provider.fed_id
        # client_code = inv.taker.code if self.service_type else inv.provider.code

        # print(f'{inv.taxes.iss.value = }')
        if inv.taxes.iss.value != '' and float(inv.taxes.iss.value) > 0:
            command = f'INSERT INTO ' \
                      f'LCTOFIS{ts}CFOP(CODIGOEMPRESA,               CHAVELCTOFIS{ts},          CODIGOCFOP, ' \
                      f'               TIPOIMPOSTO,                  ALIQIMPOSTO,               DATALCTOFIS, ' \
                      f'               CODIGOESTAB,                  VALORCONTABILIMPOSTO,      BASECALCULOIMPOSTO,' \
                      f'               VALORIMPOSTO,                 ISENTASIMPOSTO,            OUTRASIMPOSTO, ' \
                      f'               VALOREXVALORADICIONAL) ' \
                      f'VALUES         (({client.code}),             ({key}),                   {inv.nature}, '\
                      f'               {2},                          {tax_aliquot},             \'{issuance_date}\', '\
                      f'               {client.estab_num},           {inv.gross_value},         {inv.gross_value}, ' \
                      f'               {tax_value},                  {0},                       {inv.gross_value}, ' \
                      f'               {0})'
        else:
            command = f'INSERT INTO ' \
                      f'LCTOFIS{ts}CFOP(CODIGOEMPRESA,               CHAVELCTOFIS{ts},          CODIGOCFOP, ' \
                      f'               TIPOIMPOSTO,                  ALIQIMPOSTO,               DATALCTOFIS, ' \
                      f'               CODIGOESTAB,                  VALORCONTABILIMPOSTO,      BASECALCULOIMPOSTO,' \
                      f'               VALORIMPOSTO,                 ISENTASIMPOSTO,            OUTRASIMPOSTO, ' \
                      f'               VALOREXVALORADICIONAL) ' \
                      f'VALUES         (({client.code}),             ({key}),                   {inv.nature}, ' \
                      f'               {2},                          {0},                       \'{issuance_date}\', ' \
                      f'               {client.estab_num},           {inv.gross_value},         {0}, ' \
                      f'               {0},                          {0},                       {inv.gross_value}, ' \
                      f'               {0})'

        return command

    def lctofisretido(self, launch: LCTOFISData, key):
        now = self.current_datetime()

        invoice = launch.invoice

        issuance_date = invoice.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        # client_comp_num = int(inv.taker.fed_id[-6:-2]) if self.service_type else int(inv.provider.fed_id[-6:-2])

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

        iss.aliquot = round((iss.value / invoice.gross_value) * 100, 2)
        irrf.aliquot = round((irrf.value / invoice.gross_value) * 100, 2)
        csrf.aliquot = round((csrf.value / invoice.gross_value) * 100, 2)
        pis.aliquot = round((pis.value / invoice.gross_value) * 100, 2)
        cofins.aliquot = round((cofins.value / invoice.gross_value) * 100, 2)
        csll.aliquot = round((csll.value / invoice.gross_value) * 100, 2)

        # iss_situation = 3 if iss_value else 1
        # irrf_situation = 3 if irrf_value else 1
        # irpj_situation = 1
        # pis_situation = 3 if pis_value else 1
        # cofins_situation = 3 if cofins_value else 1
        # csll_situation = 3 if csll_value else 1

        iss_situation = 1
        irrf_situation = 1
        irpj_situation = 1
        pis_situation = 1
        cofins_situation = 1
        csll_situation = 1

        ts = self.type_str
        client = invoice.client
        person = invoice.person
        # client_code = inv.taker.code if self.service_type else inv.provider.code
        # person_code = inv.provider.code if self.service_type else inv.taker.code

        if self.service_type:  # se tomado
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

    def lctofisretido2(self, launch: LCTOFISData):
        invoice = launch.invoice
        now = self.current_datetime()

        issuance_date = invoice.issuance_date.split('/')
        issuance_date = f'{issuance_date[2]}-{issuance_date[1]}-{issuance_date[0]}'

        # client_comp_num = int(inv.taker.fed_id[-6:-2]) if self.service_type else int(inv.provider.fed_id[-6:-2])

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

        iss.aliquot = round((iss.value / invoice.gross_value) * 100, 2)
        irrf.aliquot = round((irrf.value / invoice.gross_value) * 100, 2)
        csrf.aliquot = round((csrf.value / invoice.gross_value) * 100, 2)
        pis.aliquot = round((pis.value / invoice.gross_value) * 100, 2)
        cofins.aliquot = round((cofins.value / invoice.gross_value) * 100, 2)
        csll.aliquot = round((csll.value / invoice.gross_value) * 100, 2)

        # iss_situation = 3 if iss_value else 1
        # irrf_situation = 3 if irrf_value else 1
        # irpj_situation = 1
        # pis_situation = 3 if pis_value else 1
        # cofins_situation = 3 if cofins_value else 1
        # csll_situation = 3 if csll_value else 1

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

    def lctofisretido_update(self, invoice: Invoice):
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

        iss.aliquot = round((iss.value / invoice.gross_value) * 100, 2)
        irrf.aliquot = round((irrf.value / invoice.gross_value) * 100, 2)
        csrf.aliquot = round((csrf.value / invoice.gross_value) * 100, 2)
        pis.aliquot = round((pis.value / invoice.gross_value) * 100, 2)
        cofins.aliquot = round((cofins.value / invoice.gross_value) * 100, 2)
        csll.aliquot = round((csll.value / invoice.gross_value) * 100, 2)

        ts = self.type_str

        if self.service_type:  # se tomado
            command = ''
        else:
            command = f'UPDATE LCTOFIS{ts}RETIDO SET ' \
                      f'BASECALCULOISSQN = {iss.calc_basis}, ALIQISSQN = {iss.aliquot}, VALORISSQN = {iss.value}, ' \
                      f'DATAPREVISSQN = \'{issuance_date}\', ' \
                      f'BASECALCULOIRRF = {irrf.calc_basis}, ALIQIRRF = {irrf.aliquot}, VALORIRRF = {irrf.value}, ' \
                      f'DATAPREVIRRFIRPJ = \'{issuance_date}\', CODIGOIMPOSTOIRRF = {irrf.code}, ' \
                      f'VARIACAOIMPOSTOIRRF = {irrf.variation}, ' \
                      f'TOTALPISCOFINSCSLL = {csrf.value}, ' \
                      f'BASECALCULOPIS = {pis.calc_basis}, ALIQPIS = {pis.aliquot}, VALORPIS = {pis.value}, ' \
                      f'CODIGOIMPOSTOPIS = {csrf.code}, VARIACAOIMPOSTOPIS = {csrf.variation}, ' \
                      f'BASECALCULOCOFINS = {cofins.calc_basis}, ALIQCOFINS = {cofins.aliquot}, ' \
                      f'VALORCOFINS = {cofins.value}, CODIGOIMPOSTOCOFINS = {csrf.code}, ' \
                      f'VARIACAOIMPOSTOCOFINS = {csrf.variation}, ' \
                      f'BASECALCULOCSLL = {csll.calc_basis}, ALIQCSLL = {csll.aliquot}, VALORCSLL = {csll.value}, ' \
                      f'CODIGOIMPOSTOCSLL = {csrf.code}, VARIACAOIMPOSTOCSLL = {csrf.variation}, ' \
                      f'DATAPREVPISCOFINSCSLL = \'{issuance_date}\' ' \
                      f'WHERE CODIGOEMPRESA = {invoice.client.code} AND '

        return command

    def lctofisvaloriss(self, launch: LCTOFISData, key):
        inv = launch.invoice
        iss_aliquot = str(float(inv.taxes.iss.aliquot) * 100).replace('.', ',')

        company_code = inv.taker.code if self.service_type else inv.provider.code

        ts = self.type_str
        # if self.service_type:  # se tomado
        command = f'INSERT INTO LCTOFIS{ts}VALORISS(' \
                  f'CODIGOEMPRESA,          CHAVELCTOFIS{ts},           CODIGOCAMPO,            VALOR) ' \
                  f'VALUES(' \
                  f'({company_code}),         ({key}),                  {125},              {inv.cnae.full_code});'\
                  f'\n\n' \
                  f'INSERT INTO LCTOFIS{ts}VALORISS(' \
                  f'CODIGOEMPRESA,          CHAVELCTOFIS{ts},           CODIGOCAMPO,            VALOR) ' \
                  f'VALUES(' \
                  f'({company_code}),         ({key}),                  {126},                  {inv.cst});' \
                  f'\n\n' \
                  f'INSERT INTO LCTOFIS{ts}VALORISS(' \
                  f'CODIGOEMPRESA,          CHAVELCTOFIS{ts},           CODIGOCAMPO,            VALOR) ' \
                  f'VALUES(' \
                  f'({company_code}),         ({key}),                  {131},                  \'{iss_aliquot}\')'

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


# class SQLRun:
#     def __init__(self, host='10.0.4.92', database=r'C:\Questor\db_questor\Saraiva_teste.FDB', user='SYSDBA',
#                  password='masterkey'):
#         self.host = host
#         self.database = database
#         self.user = user
#         self.password = password
#
#     def run(self, commands):
#         if not commands:
#             return
#
#         # transforma uma possível matriz em uma lista
#         temp_commands = commands
#         commands = list()
#         for element in temp_commands:
#             if type(element) == list:
#                 for cmd in element:
#                     commands.append(cmd)
#             else:
#                 commands.append(element)
#
#         commands = ';'.join(commands)
#         with open(SYS_PATH + r'\commands.bin', 'w') as fout:
#             print(commands, file=fout)
#         os.system(fr'py -2 Model\sql_run.py {self.host} {self.database} {self.user} '
#                   fr'{self.password}')
#
#     @staticmethod
#     def result() -> list:
#         with open(fr'{SYS_PATH}\bd_results.bin', 'rb') as fin:
#             arr = fin.read().decode('utf8')
#         return arr.split()
