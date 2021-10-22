# from Model.invoice import Invoice

from Model.constants import *
from Model.inspection_lib import clear_string


class Taxes:
    def __init__(self, data: dict):
        self.data = data

        self.service_description = self.data['descricaoservico']
        self.aditional_data = self.data['dadosadicionais']

        self.iss = self.ISS(self)
        self.irrf = self.IRRF(self)
        self.csrf = self.CSRF(self)

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

    def extract_tax_value(self, service_description, aditional_data, tax_type):
        """Encontra e extrai o valor do imposto federal solicitado"""

        # 0 = IR / 1 = PIS / 2 = COFINS / 3 = CSLL / 4 = CSRF
        keywords = ALL_KEYWORDS[tax_type]

        for text in [service_description, aditional_data]:
            clean_value = clear_string(text)
            for tax_kw in keywords:
                if tax_kw in clean_value:
                    splitted_string = clean_value.split(tax_kw)

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

    def tax_percentage(self, tax_value: float) -> float:
        return round((tax_value / self.invoice.gross_value) * 100, 2)

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

    class ISS:
        def __init__(self, outer):
            self.outer = outer

            self.is_withheld = self.is_withheld()
            self.value = outer.data['valorissqn'] if self.is_withheld else ''

        def is_withheld(self):
            """Verifica se há retencao de ISS com base no CFPS e CST"""

            iss_withheld = False
            if self.outer.data.lower() in ['florianopolis', 'florianópolis']:
                if self.outer.invoice.xml_data['cst'] in ['2', '4', '6', '10']:
                    iss_withheld = True

            elif self.outer.invoice.cfps in ['9205', '9206'] and self.outer.invoice.cst in ['0', '1']:
                iss_withheld = True

            return iss_withheld

    class IRRF:
        def __init__(self, outer):
            # 0 = IR / 1 = CSRF
            self.outer = outer
            self.is_withheld = outer.is_fed_tax_withheld(0)
            self.value = self.extract_value() if self.is_withheld else ''
            self.percentage = outer.tax_percentage(self.value) if type(self.value) == float else 0

        def extract_value(self):
            try:
                service_description = self.outer.service_description
                aditional_data = self.outer.aditional_data
                value = self.outer.extract_tax_value(service_description, aditional_data, 0)

                if value > -1:
                    ir_value = value
                else:
                    ir_value = self.outer.extract_tax_from_percentage(service_description, aditional_data,
                                                                      float(self.outer.invoice.gross_value), 0)

                # self.ir_value = self.get_ir_value() if is_ir_withheld else ''
                if ir_value != '' and ir_value < 0:
                    ir_value = TAX_EXTRACTION_ERROR
            except Exception as e:
                print(self.outer.invoice.serial_number, 'Erro na extração do IR', e)
                ir_value = TAX_EXTRACTION_ERROR

            return ir_value

    class CSRF:
        def __init__(self, outer):
            self.outer = outer

            self.pis = self.PIS(self.outer)
            self.cofins = self.COFINS(self.outer)
            self.csll = self.CSLL(self.outer)

            self.is_withheld = self.outer.is_fed_tax_withheld(1)
            self.value = self.extract_value() if self.is_withheld else ''
            if self.value != '' and self.value < 0:
                self.csrf_value = TAX_EXTRACTION_ERROR
            self.percentage = self.outer.tax_percentage(self.value) if type(self.value) == float else 0

        def extract_value(self):
            """Retorna o valor do CSRF."""

            service_description = self.outer.data.service_description
            aditional_data = self.outer.data.aditional_data

            if self.pis.value < 0 and self.cofins.value < 0 and self.csll.value < 0:
                value = self.outer.extract_tax_value(service_description, aditional_data, 4)
                if value < 0:
                    value = self.outer.extract_tax_from_percentage(service_description, aditional_data,
                                                                   float(self.outer.gross_value), 4)

                # retorna erro se CSRF for -1 pois para o método ter sido chamado significa que
                # foi detectada retenção desse imposto anteriormente
                return -1 if value < 0 else value

            if self.pis.value < 0 or self.cofins.value < 0 or self.csll.value < 0:
                value = self.outer.extract_tax_value(service_description, aditional_data, 4)
                if value < 0:
                    value = self.outer.extract_tax_from_percentage(service_description, aditional_data,
                                                                   float(self.outer.gross_value), 4)

                    # retorna erro se CSRF for -1 pois para o método ter sido chamado significa que
                    # foi detectada retenção desse imposto anteriormente
                    return -1 if value < 0 else round(value, 2)
                else:
                    return round(value, 2)

            return round(self.pis.value + self.cofins.value + self.csll.value, 2)

        class PIS:
            def __init__(self, outest):
                self.outest = outest

                self.value = self.extract_value()

            def extract_value(self):
                value = self.outest.extract_tax_value(self.outest.invoice.service_description,
                                                      self.outest.invoice.aditional_data, 1)
                if value < 0:
                    value = self.outest.extract_tax_from_percentage(self.outest.invoice.service_description,
                                                                    self.outest.invoice.aditional_data,
                                                                    float(self.outest.gross_value), 1)
                return value

        class COFINS:
            def __init__(self, outest):
                self.outest = outest

                self.value = self.extract_value()

            def extract_value(self):
                value = self.outest.extract_tax_value(self.outest.invoice.aditional_data,
                                                      self.outest.invoice.aditional_data, 2)
                if value < 0:
                    value = self.outest.extract_tax_from_percentage(self.outest.invoice.service_description,
                                                                    self.outest.invoice.aditional_data,
                                                                    float(self.outest.invoice.gross_value), 2)
                return value

        class CSLL:
            def __init__(self, outest):
                self.outest = outest

                self.value = self.extract_value()

            def extract_value(self):
                value = self.outest.extract_tax_value(self.outest.invoice.aditional_data,
                                                      self.outest.invoice.aditional_data, 3)
                if value < 0:
                    value = self.outest.extract_tax_from_percentage(self.outest.invoice.service_description,
                                                                    self.outest.invoice.aditional_data,
                                                                    float(self.outest.gross_value), 3)
                return value
