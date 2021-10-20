class LCTOFISENTData:
    def __init__(self, invoice, key, _type, ipi, funrural, payment_method=99, freight_category=9):
        self.invoice = invoice
        self.type = _type
        self.key = key
        # self.lctofisentretido_key = lctofisentretido_key
        self.ipi = ipi
        self.funrural = funrural
        self.payment_method = payment_method
        self.freight_category = freight_category
