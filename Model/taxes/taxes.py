# from Model.invoice import Invoice

from Model.constants import *
from Model.inspection_lib import clear_string

from Model.taxes.iss import ISS
from Model.taxes.irrf import IRRF
from Model.taxes.csrf import CSRF


class Taxes:
    def __init__(self, taker, provider, service_description, aditional_data, cfps, cst, gross_value, data: dict):
        self.taker = taker
        self.provider = provider
        self.service_description = service_description
        self.aditional_data = aditional_data
        self.cfps = cfps
        self.cst = cst
        self.gross_value = gross_value
        self.data = data

        self.iss = ISS(self)
        self.irrf = IRRF(self)
        self.csrf = CSRF(self)

    def is_fed_tax_withheld(self, tax_type):
        """Verifica se há retenção de imposto federal com base em palavras chave"""

        if tax_type not in [0, 1]:  # 0 = IR / 1 = CSRF
            raise Exception('Imposto não reconhecido')

        keywords = IR_KEYWORDS if tax_type == 0 else (PIS_KEYWORDS + CSRF_KEYWORDS + COFINS_KEYWORDS + CSLL_KEYWORDS)

        for text in [self.service_description, self.aditional_data]:
            clean_values = list()
            temp_value = text.lower()
            while '  ' in temp_value:
                temp_value = temp_value.replace('  ', ' ')
            clean_values.append(temp_value)
            clean_values.append(clear_string(text))

            for clean_value in clean_values:
                for kw in keywords:
                    if kw in clean_value:
                        return True

        return False

    def extract_tax_value(self, service_description, aditional_data, tax_type):
        """Encontra e extrai o valor do imposto federal solicitado"""

        # 0 = IR / 1 = PIS / 2 = COFINS / 3 = CSLL / 4 = CSRF
        keywords = ALL_KEYWORDS[tax_type]

        for text in [service_description, aditional_data]:
            clean_values = list()
            temp_value = text.lower()
            while '  ' in temp_value:
                temp_value = temp_value.replace('  ', ' ')
            clean_values.append(temp_value)
            clean_values.append(clear_string(text))

            # if self.data['numeroserie'] == '90705':
            #     print(f'{clean_values = }')

            for clean_value in clean_values:
                for tax_kw in keywords:
                    # print(tax_kw) if self.data['numeroserie'] == '90705' else None
                    if tax_kw in clean_value:
                        splitted_string = clean_value.split(tax_kw)
                        # if tax_kw == ' ir ':
                        #     print(f'{self.data["numeroserie"]}, {splitted_string = }')

                        for s in splitted_string[1:]:
                            # aux serve para que o algoritmo saiba quando o valor realmente começou a ser lido
                            aux = False
                            tax_value = str()

                            i = 0
                            while i < len(s):
                                c = s[i]
                                if (i + 1) >= len(s):
                                    # não encontrou valor referente ao imposto em análise
                                    if c.isnumeric():
                                        tax_value += c
                                    if not tax_value:
                                        return -1
                                    return self.to_float(tax_value)

                                next_c = s[i + 1]
                                if c.isnumeric() or c in [',', '.']:
                                    tax_value += c

                                    # reinicia a variável tax_value caso o valor extraído até aqui tenha
                                    # sido o de porcentagem da cobrança
                                    if next_c == '%':
                                        tax_value = ''
                                        aux = False
                                        i += 1
                                        continue

                                    if not next_c.isnumeric() and next_c not in [',', '.'] and aux:
                                        return self.to_float(tax_value)

                                if next_c.isnumeric() and not aux:
                                    aux = True
                                i += 1
        return -1

    def extract_tax_from_percentage(self, service_description, aditional_data, gross_value, tax_type):
        """Encontra e extrai o valor do imposto federal solicitado com base no seu percentual"""

        keywords = list()
        if not tax_type:
            keywords = ['porcentagemir', 'porcentagemdeir', 'percentualir', 'percentualdeir']
        elif tax_type == 1:
            keywords = ['porcentagempis', 'porcentagemdepis', 'percentualpis', 'percentualdepis']
        elif tax_type == 2:
            keywords = ['porcentagemcofins', 'porcentagemdecofins', 'percentualcofins', 'percentualdecofins']
        elif tax_type == 3:
            keywords = ['porcentagemcsll', 'porcentagemdecsll', 'percentualcsll', 'percentualdecsll']
        elif tax_type == 4:
            keywords = ['porcentagemcsrf', 'porcentagemdecsrf', 'percentualcsrf', 'percentualdecsrf',
                        'porcentagemcrf', 'porcentagemdecrf', 'percentualcrf', 'percentualdecrf',
                        'porcentagempcc', 'porcentagemdepcc', 'percentualpcc', 'percentualdepcc']

        for kw in keywords:
            for text in [clear_string(service_description), clear_string(aditional_data)]:
                if kw in text:
                    str_percentage = self.extract_first_value(text.split(kw)[1])
                    percentage = self.to_float(str_percentage)
                    value = self.gross_value * (percentage / 100) if percentage > 0.2 else self.gross_value * percentage
                    value = round(value, 2)
                    return value

        # 0 = IR / 1 = PIS / 2 = COFINS / 3 = CSLL / 4 = CSRF
        keywords = ALL_KEYWORDS[tax_type]

        for text in [service_description, aditional_data]:
            clean_value = clear_string(text)
            for tax_kw in keywords:
                if tax_kw in clean_value:
                    splitted_string = clean_value.split(tax_kw)

                    for s in splitted_string[1:]:
                        tax_value = str()

                        i = 0
                        s_len = len(s)
                        while i < s_len:
                            c = s[i]
                            if (i + 1) >= s_len and c != '%':
                                break

                            next_c = s[i + 1]
                            if c.isnumeric() or c in [',', '.']:
                                tax_value += c

                                # reinicia a variável tax_value caso o valor extraído até aqui tenha
                                # sido o de porcentagem da cobrança
                                if next_c == '%':
                                    percentage = tax_value
                                    percentage = self.to_float(percentage)
                                    tax_value = round(float((percentage / 100) * gross_value), 2)

                                    return tax_value

                            i += 1

        return -1

    @staticmethod
    def extract_first_value(text: str) -> str:
        value = ''

        i = 0
        while not text[i].isnumeric():
            i += 1
        for c in text[i:]:
            if not c.isnumeric() and c not in ['.', ',']:
                break
            value += c

        return value

    @staticmethod
    def tax_percentage(tax_value: float, gross_value: float) -> float:
        return round((tax_value / gross_value) * 100, 2)

    @staticmethod
    def to_float(tax_value):
        """Converte a string tax_value extraída da nota para o formato float"""
        if not tax_value[-1].isnumeric():
            tax_value = tax_value[:-1]
        if not tax_value[0].isnumeric():
            tax_value = tax_value[1:]

        dot = tax_value.find('.')
        comma = tax_value.find(',')
        if dot > 0 and comma > 0:
            if dot < comma:
                return round(float(tax_value.replace('.', '').replace(',', '.')), 2)
        else:
            return round(float(tax_value.replace(',', '.')), 2)
