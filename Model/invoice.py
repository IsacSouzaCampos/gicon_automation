import xml.etree.ElementTree
from Model.constants import *


class Invoice:

    def __init__(self, folder: str, file: str):
        # self.folder = folder
        # self.file = file
        # self.file_path = f'{XML_DIR}\\{file}'
        self.file_path = f'{folder}\\{file}'

        self.d = self.get_xml_tags_dict()

    def excel_data_list(self) -> list:
        """Gera a linha com os dados de retencao referentes a nota contida no arquivo 
        invoice_file."""

        number = int(self.get_serial_number())
        issuance_date = self.get_issuance_date()
        gross_value = self.get_gross_value()

        iss_withheld = self.iss_withheld()
        iss_value = self.get_iss_value() if iss_withheld else ''

        # 0 = IR / 1 = CSRF
        is_ir_withheld = self.is_fed_tax_withheld(0)
        try:
            ir_value = self.get_ir_value() if is_ir_withheld else ''
        except Exception as e:
            print(self.d['numeroserie'], e)
            ir_value = '***ERRO***'

        is_csrf_withheld = self.is_fed_tax_withheld(1)
        try:
            csrf_value = self.get_csrf_value() if is_csrf_withheld else ''
        except Exception as e:
            print(self.d['numeroserie'], e)
            csrf_value = '***ERRO***'

        net_value = gross_value
        for tax in [iss_value, ir_value, csrf_value]:
            if type(tax) != str:
                net_value -= tax

        service_nature = self.generate_service_nature(iss_withheld, is_ir_withheld, is_csrf_withheld)

        row = list([number, issuance_date, gross_value, iss_value, ir_value, csrf_value, net_value, service_nature])

        if self.is_canceled():
            row.append('CANCELADA')

        return row

    def iss_withheld(self) -> bool:
        """Verifica se há retencao de ISS com base no CFPS e CST"""

        iss_withheld = False
        try:
            if self.d['nomemunicipioprestador'] == 'FLORIANOPOLIS':
                if self.d['cst'] in ['2', '4', '6', '10']:
                    iss_withheld = True

            elif self.d['cfps'] in ['9205', '9206'] and self.d['cst'] in ['0', '1']:
                iss_withheld = True

        except Exception as e:
            print(f'Erro: {e} - Arquivo: {self.file_path}')

        return iss_withheld

    def is_fed_tax_withheld(self, tax_type: int) -> bool:
        """Verifica se há retenção de imposto federal com base em palavras chave"""

        if tax_type not in [0, 1]:  # 0 = IR / 1 = CSRF
            raise Exception('Imposto não reconhecido')

        keywords = IR_KEYWORDS if tax_type == 0 else (PIS_KEYWORDS + CSRF_KEYWORDS + COFINS_KEYWORDS + CSLL_KEYWORDS)

        for tag in ['descricaoservico', 'dadosadicionais']:
            if tag in self.d and self.d[tag] is not None:
                value = self.d[tag]

                # procurar indícios de retencao do tax_type na tag
                # '(' não pode ser removido diretamente no método clear_string pois será necessário para o
                # método de extração do valor do imposto usado posteriormente.
                clean_value = self.clear_string(value).replace('(', '')

                for ir_note in keywords:
                    if ir_note in clean_value or ('retencao' + ir_note) in clean_value:
                        return True
        
        return False

    def is_canceled(self) -> bool:
        """Verifica se a nota foi cancelada"""
        return 'datacancelamento' in self.d and self.d['datacancelamento'] is not None

    @staticmethod
    def clear_string(s: str) -> str:
        """Altera a string a ser analisada de maneira conveniente para a detecção de 
        possíveis retenções"""
        s = s.lower()

        s = s.replace(' ', '')
        # s = s.replace('(', '')
        s = s.replace('=', '')
        s = s.replace('-', '')
        s = s.replace(':', '')
        s = s.replace('/', '')
        s = s.replace('\\', '')
        
        s = s.replace('ç', 'c')
        
        s = s.replace('ã', 'a')
        s = s.replace('õ', 'o')
        
        s = s.replace('á', 'a')
        s = s.replace('é', 'e')
        s = s.replace('í', 'i')
        s = s.replace('ó', 'o')
        s = s.replace('ú', 'u')

        s = s.replace('â', 'a')
        s = s.replace('ê', 'e')
        s = s.replace('ó', 'o')

        if s.count('leidatransparencia') > 1:
            before = s[: s.find('leidatransparencia') + 1]
            after = s[s.find('leidatransparencia') + len('leidatransparencia'): len(s)]
            after = after[after.find('leidatransparencia') + len('leidatransparencia'): len(after)]
            s = before + after

        return s

    def get_xml_tags_dict(self) -> dict:
        """Retorna o dicionário referente as tags do xml e seus valores associados"""
        tree = xml.etree.ElementTree.parse(self.file_path)
        root = tree.getroot()

        d = dict()
        for child in root.iter():
            d[child.tag.lower()] = child.text
        
        return d

    def get_serial_number(self):
        """Retorna o número da nota"""
        return self.d['numeroserie']

    def get_taker_business_name(self) -> str:
        """Retorna a razão social do tomador do serviço"""
        return self.d['razaosocialtomador']

    def get_provider_business_name(self) -> str:
        """Retorna a razão social do prestador do serviço"""
        return self.d['razaosocialprestador']

    def get_issuance_date(self) -> str:
        """Retorna a data de emissão no formato nacional de datas"""
        issuance_date = self.d['dataemissao'][:10].split('-')
        return f'{issuance_date[2]}/{issuance_date[1]}/{issuance_date[0]}'

    def get_gross_value(self) -> float:
        """Retorna o valor bruto do serviço"""
        return float(self.d['valortotalservicos'])

    def get_iss_value(self) -> float:
        """Retorna o valor do ISS"""
        return float(self.d['valorissqn'])

    def get_ir_value(self) -> float:
        """Retorna o valor do IR"""
        return self.extract_tax_value(0)

    def get_csrf_value(self) -> float:
        """Retorna o valor do CSRF"""
        pis_value = self.extract_tax_value(1)
        cofins_value = self.extract_tax_value(2)
        csll_value = self.extract_tax_value(3)

        if not pis_value + cofins_value + csll_value:
            return self.extract_tax_value(4)

        if not pis_value or not cofins_value or not csll_value:
            print(pis_value, cofins_value, csll_value)
            raise Exception('Um ou mais impostos federais não puderam ser extraídos')

        return pis_value + cofins_value + csll_value

    def extract_tax_value(self, tax_type: int) -> float:
        """Encontra e extrai o valor do imposto federal solicitado"""

        # 0 = IR / 1 = PIS / 2 = COFINS / 3 = CSLL / 4 = CSRF
        keywords = ALL_KEYWORDS[tax_type]

        for tag in ['descricaoservico', 'dadosadicionais']:
            if tag in self.d and self.d[tag] is not None:
                value = self.d[tag]

                clean_value = self.clear_string(value)
                for tax_kw in keywords:
                    if tax_kw in clean_value or ('retencao' + tax_kw) in clean_value:
                        splitted_string = clean_value.split(tax_kw)

                        for s in splitted_string[1:]:
                            aux = False
                            tax_value = str()

                            i = 0

                            while i < len(s):
                                c = s[i]
                                try:
                                    next_c = s[i + 1]
                                except Exception as e:
                                    print(self.d['numeroserie'], e)
                                    if c.isnumeric():
                                        tax_value += c
                                    return self.convert_s_tax_value_to_float(tax_value)

                                if c.isnumeric() or c in [',', '.']:
                                    tax_value += c
                                    if not next_c.isnumeric() and next_c not in [',', '.'] and aux:
                                        return self.convert_s_tax_value_to_float(tax_value)

                                if next_c.isnumeric() and not aux:
                                    aux = True
                                i += 1
        return 0

    @staticmethod
    def convert_s_tax_value_to_float(tax_value: str) -> float:
        """Converte a string tax_value extraída da nota para o formato float"""
        if not tax_value[-1].isnumeric():
            tax_value = tax_value[:-1]
        if not tax_value[0].isnumeric():
            tax_value = tax_value[1:]

        dot = tax_value.find('.')
        comma = tax_value.find(',')
        if dot > 0 and comma > 0:
            if dot < comma:
                return float(tax_value.replace('.', '').replace(',', '.'))
        else:
            return float(tax_value.replace(',', '.'))

    def generate_service_nature(self, iss_withheld: bool, is_ir_withheld: bool, is_csrf_withheld: bool) -> int:
        """Gera o código da natureza do serviço *tomado* baseado nos impostos retidos e no
           CFPS fornecido na nota"""

        cfps = self.d['cfps']

        if iss_withheld and is_ir_withheld and is_csrf_withheld:
            return int(cfps + '302')
        if iss_withheld and is_ir_withheld:
            return int(cfps + '304')
        if iss_withheld and is_csrf_withheld:
            return int(cfps + '302')
        if is_ir_withheld and is_csrf_withheld:
            return int(cfps + '302')
        if iss_withheld:
            return int(cfps + '308')
        if is_ir_withheld:
            return int(cfps + '304')
        if is_csrf_withheld:
            return int(cfps + '306')

        return int(cfps + '300')
