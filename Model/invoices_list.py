from Model.invoice import Invoice


class InvoicesList:
    def __init__(self, invoices: list = list()):
        self.invoices = invoices

    def index(self, index):
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
            print(invoice.nature)

    def get_gui_table(self) -> list:
        table = list()
        for invoice in self.invoices:
            irrf_value = '' if not invoice.taxes.irrf.value else invoice.taxes.irrf.value
            csrf_value = '' if not invoice.taxes.csrf.value else invoice.taxes.csrf.value

            table.append([invoice.serial_number, invoice.issuance_date, invoice.gross_value, invoice.taxes.iss.value,
                          irrf_value, csrf_value, invoice.net_value,
                          invoice.nature])
        return table

    def update(self, indexes: list, invoice_data_lst: list):
        for i, idx in enumerate(indexes):
            self.update_invoice(idx, invoice_data_lst[i])

    def update_invoice(self, index: int, invoice_data: list) -> None:
        # print('new row*:', invoice_data)
        self.invoices[index].serial_number = invoice_data[0]
        self.invoices[index].issuance_date = invoice_data[1]
        self.invoices[index].gross_value = invoice_data[2]
        self.invoices[index].taxes.iss.value = invoice_data[3]
        self.invoices[index].taxes.irrf.value = invoice_data[4]
        self.invoices[index].taxes.csrf.value = invoice_data[5]
        self.invoices[index].set_net_value()
        self.invoices[index].nature = invoice_data[7]

        # print(self.invoices[index].taxes.irrf.value)

    def number_of_errors(self) -> int:
        """
        Retorna o número de conferências com erros.

        :return:         Número de erros detectados.
        :rtype:          (int)
        """

        n_errors = 0
        for invoice in self.invoices:
            values = [invoice.gross_value, invoice.taxes.iss.value, invoice.taxes.irrf.value, invoice.taxes.csrf.value,
                      invoice.net_value]
            for value in values:
                try:
                    if value not in ['-', '']:
                        float(value)
                except Exception as e:
                    print(e)
                    n_errors += 1
        return n_errors

    def filter(self, fed_id, service_type):
        fed_id = fed_id.replace('.', '').replace('/', '').replace('-', '')

        res_invs = InvoicesList([])
        indexes = list()

        if service_type:  # se tomado
            for index, invoice in enumerate(self.invoices):
                if fed_id in invoice.provider.fed_id:
                    indexes.append(index)
                    res_invs.add_invoice(invoice)
        else:
            for index, invoice in enumerate(self.invoices):
                if fed_id in invoice.taker.fed_id:
                    indexes.append(index)
                    res_invs.add_invoice(invoice)

        return indexes, res_invs

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
