# -*- coding: utf-8 -*-
import xml.etree.ElementTree
from Model.company import Company
from Model.constants import *
from Model.inspection_lib import clear_string, extract_tax_value, extract_tax_from_percentage


class Invoice:

    def __init__(self, file_path, service_type, doc_type=99):
        self.operation_purpose = 1
        self.issuer = 'T' if service_type else 'P'
        self.doc_type = doc_type
        self.service_type = service_type  # 0: prestado / 1: tomado
        self.file_path = file_path

        d = self.get_xml_tags_dict()

        self.serial_number = int(d['numeroserie'])
        self.issuance_date = d['dataemissao'][:10].split('-')
        self.issuance_date = self.issuance_date[2] + '/' + self.issuance_date[1] + '/' + self.issuance_date[0]
        self.cst = d['cst']
        self.cfps = d['cfps']
        self.aliquot = d['aliquota']
        self.gross_value = float(d['valortotalservicos'])

        self.provider = Company(d['cnpjprestador'], d['razaosocialprestador'], d['nomemunicipioprestador'])
        self.taker = Company(d['identificacaotomador'], d['razaosocialtomador'], 'Florianópolis')

        self.iss_withheld = self.iss_withheld()
        self.iss_value = d['valorissqn'] if self.iss_withheld else ''

        if 'descricaoservico' in d and d['descricaoservico'] is not None:
            self.service_description = d['descricaoservico']
        else:
            self.service_description = ''

        if 'dadosadicionais' in d and d['dadosadicionais'] is not None:
            self.aditional_data = d['dadosadicionais']
        else:
            self.aditional_data = ''

        # 0 = IR / 1 = CSRF
        is_ir_withheld = self.is_fed_tax_withheld(0)
        self.ir_value = self.extract_ir() if is_ir_withheld else ''
        self.ir_percentage = self.tax_percentage(self.ir_value) if type(self.ir_value) == float else 0

        is_csrf_withheld = self.is_fed_tax_withheld(1)
        self.csrf_value = self.extract_csrf_value() if is_csrf_withheld else ''
        if self.csrf_value != '' and self.csrf_value < 0:
            self.csrf_value = TAX_EXTRACTION_ERROR
        self.csrf_percentage = self.tax_percentage(self.csrf_value) if type(self.csrf_value) == float else 0

        # print('IR(%):', self.ir_percentage, '- CSRF(%):', self.csrf_percentage)

        self.net_value = self.gross_value
        for tax in [self.iss_value, self.ir_value, self.csrf_value]:
            if type(tax) != str:
                self.net_value -= tax

        self.net_value = round(self.net_value, 2)
        self.service_nature = self.service_nature(self.iss_withheld, is_ir_withheld, is_csrf_withheld, self.service_type)

        self.is_canceled = 'datacancelamento' in d and d['datacancelamento'] is not None
        self.invoice_situation = 2 if self.is_canceled else 0

    def data_list(self) -> list:
        """
        Gera a linha com os dados de retencao referentes a nota contida no arquivo invoice_file.

        :return: Lista com o dados da conferência.
        :rtype:  (list)
        """

        row = list([self.serial_number, self.issuance_date, self.gross_value, self.iss_value, self.ir_value,
                    self.csrf_value, self.net_value, self.service_nature, self.service_description,
                    self.aditional_data, self.provider.cnpj, self.provider.name, self.taker.cnpj, self.taker.name])

        if self.is_canceled:
            row = row[:2] + ['-' for _ in range(len(row) - 2)]
            row.append('CANCELADA')

        return row

    def iss_withheld(self):
        """Verifica se há retencao de ISS com base no CFPS e CST"""

        iss_withheld = False
        if self.provider.city.lower() in ['florianopolis', 'florianópolis']:
            if self.cst in ['2', '4', '6', '10']:
                iss_withheld = True

        elif self.cfps in ['9205', '9206'] and self.cst in ['0', '1']:
            iss_withheld = True

        return iss_withheld

    def is_fed_tax_withheld(self, tax_type):
        """Verifica se há retenção de imposto federal com base em palavras chave"""

        if tax_type not in [0, 1]:  # 0 = IR / 1 = CSRF
            raise Exception('Imposto não reconhecido')

        keywords = IR_KEYWORDS if tax_type == 0 else (PIS_KEYWORDS + CSRF_KEYWORDS + COFINS_KEYWORDS + CSLL_KEYWORDS)

        for text in [self.service_description, self.aditional_data]:
            clean_value = clear_string(text)

            # if 'leidatransparencia' in clean_value or 'lei12.741/2012' in clean_value:
            #     if 'retencao' not in clean_value and 'retencoes' not in clean_value:
            #         return False

            for kw in keywords:
                if kw in clean_value:
                    return True

        return False

    def get_xml_tags_dict(self):
        """Retorna o dicionário referente as tags do xml e seus valores associados"""
        tree = xml.etree.ElementTree.parse(self.file_path)
        root = tree.getroot()

        d = dict()
        for child in root.iter():
            d[child.tag.lower()] = child.text
        
        return d

    def extract_ir(self):
        try:
            value = extract_tax_value(self.service_description, self.aditional_data, 0)

            if value > -1:
                ir_value = value
            else:
                ir_value = extract_tax_from_percentage(self.service_description, self.aditional_data,
                                                            float(self.gross_value), 0)

            # self.ir_value = self.get_ir_value() if is_ir_withheld else ''
            if ir_value != '' and ir_value < 0:
                ir_value = TAX_EXTRACTION_ERROR
        except Exception as e:
            print(self.serial_number, 'Erro na extração do IR', e)
            ir_value = TAX_EXTRACTION_ERROR

        return ir_value

    def extract_csrf_value(self):
        """Retorna o valor do CSRF."""

        pis_value = extract_tax_value(self.service_description, self.aditional_data, 1)
        if pis_value < 0:
            pis_value = extract_tax_from_percentage(self.service_description, self.aditional_data,
                                                    float(self.gross_value), 1)

        cofins_value = extract_tax_value(self.service_description, self.aditional_data, 2)
        if cofins_value < 0:
            cofins_value = extract_tax_from_percentage(self.service_description, self.aditional_data,
                                                       float(self.gross_value), 2)

        csll_value = extract_tax_value(self.service_description, self.aditional_data, 3)
        if csll_value < 0:
            csll_value = extract_tax_from_percentage(self.service_description, self.aditional_data,
                                                     float(self.gross_value), 3)

        if pis_value < 0 and cofins_value < 0 and csll_value < 0:
            csrf_value = extract_tax_value(self.service_description, self.aditional_data, 4)
            if csrf_value < 0:
                csrf_value = extract_tax_from_percentage(self.service_description, self.aditional_data,
                                                         float(self.gross_value), 4)

            # retorna erro se CSRF for -1 pois para o método ter sido chamado significa que
            # foi detectada retenção desse imposto anteriormente
            return -1 if csrf_value < 0 else csrf_value

        if pis_value < 0 or cofins_value < 0 or csll_value < 0:
            csrf_value = extract_tax_value(self.service_description, self.aditional_data, 4)
            if csrf_value < 0:
                csrf_value = extract_tax_from_percentage(self.service_description, self.aditional_data,
                                                         float(self.gross_value), 4)

                # retorna erro se CSRF for -1 pois para o método ter sido chamado significa que
                # foi detectada retenção desse imposto anteriormente
                return -1 if csrf_value < 0 else round(csrf_value, 2)
            else:
                return round(csrf_value, 2)

        return round(pis_value + cofins_value + csll_value, 2)

    def tax_percentage(self, tax_value: float) -> float:
        return round((tax_value / self.gross_value) * 100, 2)

    def service_nature(self, iss_withheld, is_ir_withheld, is_csrf_withheld, service_type):
        """Gera o código da natureza do serviço *tomado* baseado nos impostos retidos e no
           CFPS fornecido na nota"""

        # service_type: 0 - prestado / 1 - tomado
        # o prestado é temporário, enquanto não se acha uma solução para detectar a natureza exata para este
        # caso. Esta solução temporária gera resultados errados e serve apenas para testes.
        cfps = self.cfps + '3' if service_type else self.cfps + '0'

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
