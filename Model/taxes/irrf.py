from Model.constants import *
from Model.inspection_lib import clear_string


class IRRF:
    def __init__(self, outer):
        # 0 = IR / 1 = CSRF
        self.outer = outer
        self.is_withheld = outer.is_fed_tax_withheld(0)
        self.value = self.extract_value() if self.is_withheld else 0
        gross_value = self.outer.gross_value
        self.aliquot = outer.tax_percentage(self.value, gross_value) if type(self.value) == float else 0
        self.calc_basis = self.outer.gross_value if self.is_withheld else 0
        self.code = 1708 if self.is_withheld else 'NULL'
        self.variation = 6 if self.is_withheld else 'NULL'

    def extract_value(self):
        keywords = ['porcentagemir', 'porcentagemdeir', 'percentualir', 'percentualdeir']
        service_description = self.outer.service_description
        aditional_data = self.outer.aditional_data

        calc_from_percentage = False
        for kw in keywords:
            if kw in clear_string(service_description) or kw in clear_string(aditional_data):
                calc_from_percentage = True
                break

        try:
            value = -1
            if not calc_from_percentage:
                value = self.outer.extract_tax_value(service_description, aditional_data, 0)

            if value > -1:
                ir_value = value
            else:
                ir_value = self.outer.extract_tax_from_percentage(service_description, aditional_data,
                                                                  float(self.outer.gross_value), 0)

            if ir_value != '' and ir_value < 0:
                ir_value = TAX_EXTRACTION_ERROR
        except Exception as e:
            print(self.outer.data['numeroserie'], 'Erro na extração do IR', e)
            ir_value = TAX_EXTRACTION_ERROR

        return ir_value
