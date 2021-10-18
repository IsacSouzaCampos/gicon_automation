class LCTOFISENTData:
    def __init__(self, _type, invoice, ipi, funrural, payment_method=99, freight_category=9):
        self.type = _type
        self.invoice = invoice
        # self.lctofisent_key = lctofisent_key
        # self.lctofisentretido_key = lctofisentretido_key
        self.ipi = ipi
        self.funrural = funrural
        self.payment_method = payment_method
        self.freight_category = freight_category
