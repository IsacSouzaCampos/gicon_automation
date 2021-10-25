from Model.constants import *


class CSRF:
    def __init__(self, outer):
        self.outer = outer

        self.pis = self.PIS(self.outer)
        self.cofins = self.COFINS(self.outer)
        self.csll = self.CSLL(self.outer)

        # print('nota:', self.outer.data["numeroserie"], 'pis:', self.pis.value, 'cofins:', self.cofins.value, 'csll:',
        #       self.csll.value)

        self.is_withheld = self.outer.is_fed_tax_withheld(1)
        self.value = self.extract_value() if self.is_withheld else ''
        if self.value != '' and self.value < 0:
            self.csrf_value = TAX_EXTRACTION_ERROR
        gross_value = self.outer.gross_value
        self.percentage = self.outer.tax_percentage(self.value, gross_value) if type(self.value) == float else 0

        if (self.pis.value + self.cofins.value + self.csll.value) <= 0 and self.percentage == 4.65:
            self.pis.value = round(self.outer.gross_value * 0.0065, 2)
            self.cofins.value = round(self.outer.gross_value * 0.03, 2)
            self.csll.value = round(self.outer.gross_value * 0.01, 2)
            self.value = self.pis.value + self.cofins.value + self.csll.value
            # print(f'nota {self.outer.data["numeroserie"]}')
            # print('pis:', self.pis.value, 'cofins:', self.cofins.value, 'csll:', self.csll.value, 'csrf:', self.value)

    def extract_value(self):
        """Retorna o valor do CSRF."""

        service_description = self.outer.service_description
        aditional_data = self.outer.aditional_data

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
            value = self.outest.extract_tax_value(self.outest.service_description,
                                                  self.outest.aditional_data, 1)
            if value < 0:
                value = self.outest.extract_tax_from_percentage(self.outest.service_description,
                                                                self.outest.aditional_data,
                                                                float(self.outest.gross_value), 1)
            return value

    class COFINS:
        def __init__(self, outest):
            self.outest = outest

            self.value = self.extract_value()

        def extract_value(self):
            value = self.outest.extract_tax_value(self.outest.aditional_data,
                                                  self.outest.aditional_data, 2)
            if value < 0:
                value = self.outest.extract_tax_from_percentage(self.outest.service_description,
                                                                self.outest.aditional_data,
                                                                float(self.outest.gross_value), 2)
            return value

    class CSLL:
        def __init__(self, outest):
            self.outest = outest

            self.value = self.extract_value()

        def extract_value(self):
            value = self.outest.extract_tax_value(self.outest.aditional_data,
                                                  self.outest.aditional_data, 3)
            if value < 0:
                value = self.outest.extract_tax_from_percentage(self.outest.service_description,
                                                                self.outest.aditional_data,
                                                                float(self.outest.gross_value), 3)
            return value