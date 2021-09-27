from Model.invoice import Invoice


class InvoicesList:
    def __init__(self, invoices: list = list()):
        self.invoices = invoices

    def invoice(self, index):
        return self.invoices[index]

    def add_invoice(self, invoice: Invoice):
        self.invoices.append(invoice)

    def empty(self):
        return len(self.invoices) == 0

    def print_list(self):
        for invoice in self.invoices:
            print(invoice.serial_number, end='\t')
            print(invoice.issuance_date, end='\t')
            print(invoice.gross_value, end='\t')
            print(invoice.iss_value, end='\t')
            print(invoice.ir_value, end='\t')
            print(invoice.csrf_value, end='\t')
            print(invoice.net_value, end='\t')
            print(invoice.service_nature)

    def get_gui_table(self) -> list:
        table = list()
        for invoice in self.invoices:
            table.append([invoice.serial_number, invoice.issuance_date, invoice.gross_value, invoice.iss_value,
                          invoice.ir_value, invoice.csrf_value, invoice.net_value, invoice.service_nature])
        return table

    def update_invoice(self, index: int, invoice_data: list) -> None:
        self.invoices[index].serial_number = invoice_data[0]
        self.invoices[index].issuance_date = invoice_data[1]
        self.invoices[index].gross_value = invoice_data[2]
        self.invoices[index].iss_value = invoice_data[3]
        self.invoices[index].ir_value = invoice_data[4]
        self.invoices[index].csrf_value = invoice_data[5]
        self.invoices[index].net_value = invoice_data[6]
        self.invoices[index].service_nature = invoice_data[7]

    def number_of_errors(self) -> int:
        """
        Retorna o número de conferências com erros.

        :return:         Número de erros detectados.
        :rtype:          (int)
        """

        n_errors = 0
        for invoice in self.invoices:
            values = [invoice.gross_value, invoice.iss_value, invoice.ir_value, invoice.csrf_value, invoice.net_value]
            for value in values:
                try:
                    if value not in ['-', '']:
                        float(value)
                except Exception as e:
                    print(e)
                    n_errors += 1
        return n_errors

    def __iter__(self):
        return InvoicesListIterator(self)

    def __len__(self):
        return len(self.invoices)


class InvoicesListIterator:
    def __init__(self, invoices):
        self._invoices = invoices
        self._index = 0

    def __next__(self):
        if self._index < len(self._invoices):
            result = self._invoices.invoices[self._index]
            self._index += 1
            return result
        raise StopIteration
