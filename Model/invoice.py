import xml.etree.ElementTree
from Model.constants import *
from Model.invoices_inspection_lib import clear_string, extract_tax_value, extract_tax_from_percentage


class Invoice:

    def __init__(self, folder: str, file: str, service_type: int):
        self.service_type = service_type  # 0: prestado / 1: tomado
        self.file_path = f'{folder}\\{file}'
        self.d = self.get_xml_tags_dict()

    def data_list(self) -> list:
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
            if ir_value != '' and ir_value < 0:
                ir_value = TAX_EXTRACTION_ERROR
        except Exception as e:
            print(self.d['numeroserie'], e)
            ir_value = TAX_EXTRACTION_ERROR

        is_csrf_withheld = self.is_fed_tax_withheld(1)
        try:
            csrf_value = self.get_csrf_value() if is_csrf_withheld else ''
            if csrf_value != '' and csrf_value < 0:
                csrf_value = TAX_EXTRACTION_ERROR
        except Exception as e:
            print(self.d['numeroserie'], e)
            csrf_value = TAX_EXTRACTION_ERROR

        net_value = gross_value
        for tax in [iss_value, ir_value, csrf_value]:
            if type(tax) != str:
                net_value -= tax

        net_value = round(net_value, 2)
        service_nature = self.service_nature(iss_withheld, is_ir_withheld, is_csrf_withheld, self.service_type)

        row = list([number, issuance_date, gross_value, iss_value, ir_value, csrf_value, net_value, service_nature])

        row.append(self.d['razaosocialprestador'])
        row.append(self.d['razaosocialtomador'])
        if 'descricaoservico' in self.d and self.d['descricaoservico'] is not None:
            row.append(self.d['descricaoservico'])
        else:
            row.append('')
        if 'dadosadicionais' in self.d and self.d['dadosadicionais'] is not None:
            row.append(self.d['dadosadicionais'])
        else:
            row.append('')

        if self.is_canceled():
            row = row[:2] + ['-' for _ in range(len(row) - 2)]
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

                clean_value = clear_string(value)
                for kw in keywords:
                    if kw in clean_value:
                        return True
        
        return False

    def is_canceled(self) -> bool:
        """Verifica se a nota foi cancelada"""
        return 'datacancelamento' in self.d and self.d['datacancelamento'] is not None

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
        ir_value = extract_tax_value(self.d, 0)
        # if not ir_value:
        #     return TAX_EXTRACTION_ERROR
        return ir_value if ir_value > -1 else extract_tax_from_percentage(self.d, float(self.get_gross_value()), 0)

    def get_csrf_value(self) -> float:
        """Retorna o valor do CSRF"""
        gross_value = self.get_gross_value()

        pis_value = extract_tax_value(self.d, 1)
        if pis_value < 0:
            pis_value = extract_tax_from_percentage(self.d, float(gross_value), 1)

        cofins_value = extract_tax_value(self.d, 2)
        if cofins_value < 0:
            cofins_value = extract_tax_from_percentage(self.d, float(gross_value), 2)

        csll_value = extract_tax_value(self.d, 3)
        if csll_value < 0:
            csll_value = extract_tax_from_percentage(self.d, float(gross_value), 3)

        if pis_value < 0 and cofins_value < 0 and csll_value < 0:
            csrf_value = extract_tax_value(self.d, 4)
            if csrf_value < 0:
                csrf_value = extract_tax_from_percentage(self.d, float(gross_value), 4)

            # retorna erro se CSRF for -1 pois para o método ter sido chamado significa que
            # foi detectada retenção desse imposto anteriormente
            return -1 if csrf_value < 0 else csrf_value

        if pis_value < 0 or cofins_value < 0 or csll_value < 0:
            csrf_value = extract_tax_value(self.d, 4)
            if csrf_value < 0:
                csrf_value = extract_tax_from_percentage(self.d, float(gross_value), 4)

                # retorna erro se CSRF for -1 pois para o método ter sido chamado significa que
                # foi detectada retenção desse imposto anteriormente
                return -1 if csrf_value < 0 else round(csrf_value, 2)
            else:
                return round(csrf_value, 2)

        return round(pis_value + cofins_value + csll_value, 2)

    def service_nature(self, iss_withheld: bool, is_ir_withheld: bool, is_csrf_withheld: bool,
                       service_type: int) -> int:
        """Gera o código da natureza do serviço *tomado* baseado nos impostos retidos e no
           CFPS fornecido na nota"""

        # service_type: 0 - prestado / 1 - tomado
        # o prestado é temporário, enquanto não se acha uma solução para detectar a natureza exata para este
        # caso. Esta solução temporária gera resultados errados e serve apenas para testes.
        cfps = self.d['cfps'] + '3' if service_type else self.d['cfps'] + '0'

        if iss_withheld and is_ir_withheld and is_csrf_withheld:
            return int(cfps + '02')
        if iss_withheld and is_ir_withheld:
            return int(cfps + '04')
        if iss_withheld and is_csrf_withheld:
            return int(cfps + '02')
        if is_ir_withheld and is_csrf_withheld:
            return int(cfps + '02')
        if iss_withheld:
            return int(cfps + '08')
        if is_ir_withheld:
            return int(cfps + '04')
        if is_csrf_withheld:
            return int(cfps + '06')

        return int(cfps + '00')
