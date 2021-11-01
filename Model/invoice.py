# -*- coding: utf-8 -*-
import xml.etree.ElementTree
from Model.company import Company
# from Model.inspection_lib import extract_tax_from_percentage

from Model.taxes.taxes import Taxes


class Invoice:

    def __init__(self, file_path, service_type, doc_type=99):
        self.operation_purpose = 1
        self.issuer = 'T' if service_type else 'P'
        self.doc_type = doc_type
        self.service_type = service_type  # 0: prestado / 1: tomado
        self.file_path = file_path

        self.xml_data = self.get_xml_tags_dict()

        self.serial_number = int(self.xml_data['numeroserie'])
        self.issuance_date = self.xml_data['dataemissao'][:10].split('-')
        self.issuance_date = self.issuance_date[2] + '/' + self.issuance_date[1] + '/' + self.issuance_date[0]
        self.cst = self.xml_data['cst']
        self.cfps = self.xml_data['cfps']
        self.full_cnae = self.gen_cnae(self.xml_data['codigocnae'])
        self.gross_value = float(self.xml_data['valortotalservicos'])

        # if service_type:
        self.provider = Company(self.xml_data['cnpjprestador'], self.xml_data['razaosocialprestador'],
                                self.xml_data['nomemunicipioprestador'])
        self.taker = Company(self.xml_data['identificacaotomador'],
                             self.xml_data['razaosocialtomador'], 'Florianópolis')

        if 'descricaoservico' in self.xml_data and self.xml_data['descricaoservico'] is not None:
            self.service_description = self.xml_data['descricaoservico']
        else:
            self.service_description = ''

        if 'dadosadicionais' in self.xml_data and self.xml_data['dadosadicionais'] is not None:
            self.aditional_data = self.xml_data['dadosadicionais']
        else:
            self.aditional_data = ''

        self.taxes = Taxes(self.taker, self.provider, self.service_description, self.aditional_data, self.cfps,
                           self.cst, self.gross_value, self.xml_data)

        # print('IR(%):', self.ir_percentage, '- CSRF(%):', self.csrf_percentage)

        self.net_value = 0
        self.set_net_value()

        self.nature = self.service_nature(self.taxes.iss.is_withheld, self.taxes.irrf.is_withheld,
                                          self.taxes.csrf.is_withheld, self.service_type)

        self.is_canceled = 'datacancelamento' in self.xml_data and self.xml_data['datacancelamento'] is not None
        self.invoice_situation = 2 if self.is_canceled else 0
        self.to_launch = self.taxes.iss.is_withheld or self.taxes.irrf.is_withheld or self.taxes.csrf.is_withheld

    def data_list(self) -> list:
        """
        Gera a linha com os dados de retencao referentes a nota contida no arquivo invoice_file.

        :return: Lista com o dados da conferência.
        :rtype:  (list)
        """

        irrf_value = '' if not self.taxes.irrf.value else self.taxes.irrf.value
        csrf_value = '' if not self.taxes.csrf.value else self.taxes.csrf.value
        row = list([self.serial_number, self.issuance_date, self.gross_value, self.taxes.iss.value,
                    irrf_value, csrf_value, self.net_value, self.nature,
                    self.service_description, self.aditional_data, self.provider.fed_id, self.provider.name,
                    self.taker.fed_id, self.taker.name])

        if self.is_canceled:
            row = row[:2] + ['-' for _ in range(len(row) - 2)]
            row.append('CANCELADA')

        return row

    def get_xml_tags_dict(self):
        """Retorna o dicionário referente as tags do xml e seus valores associados"""
        tree = xml.etree.ElementTree.parse(self.file_path)
        root = tree.getroot()

        d = dict()
        for child in root.iter():
            d[child.tag.lower()] = child.text
        
        return d

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

    @staticmethod
    def gen_cnae(cnae):
        with open(r'Support\cnae.csv', 'r') as fin:
            for line in fin.readlines():
                values = line.split(',')
                if cnae == values[0]:
                    v = values[1].replace('\n', '')
                    return (cnae + v) if len(v) == 4 else (cnae + '0' + v)
        return cnae

    def set_nature(self, nature: str):
        self.nature = int(nature)

    def set_net_value(self):
        self.net_value = self.gross_value
        for tax in [self.taxes.iss.value, self.taxes.irrf.value, self.taxes.csrf.value]:
            if type(tax) != str:
                self.net_value -= tax
        self.net_value = round(self.net_value, 2)
