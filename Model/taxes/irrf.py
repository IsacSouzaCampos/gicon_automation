from Model.constants import *


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
            print(self.outer.data['numeroserie'], 'Erro na extração do IR', e)
            ir_value = TAX_EXTRACTION_ERROR

        return ir_value
