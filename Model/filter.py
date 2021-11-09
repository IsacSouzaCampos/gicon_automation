from Model.invoices_list import InvoicesList


class Filter:
    def __init__(self, invoices: InvoicesList, fed_id: str, selected_fed_id: int, sel_iss: bool, sel_irrf: bool,
                 sel_csrf: bool, cnae_description: str, withheld_type: int):
        self.invoices = invoices
        self.service_type = self.invoices.index(0).service_type
        self._fed_id = fed_id
        self._selected_fed_id = selected_fed_id
        self.sel_iss = sel_iss
        self.sel_irrf = sel_irrf
        self.sel_csrf = sel_csrf
        self.cnae_descr = cnae_description
        self.wh_type = withheld_type
        # print('CNAE description:', cnae_description)

    def run(self) -> tuple:
        invoices = self.invoices
        indexes = [i for i in range(len(self.invoices))]
        indexes, invoices = self.cnae_description(indexes, invoices)
        indexes, invoices = self.fed_id(indexes, invoices)
        indexes, invoices = self.selected_fed_id(indexes, invoices)
        indexes, invoices = self.withheld_type(indexes, invoices)

        if self.sel_iss:
            indexes, invoices = self.selected_tax(indexes, invoices, 0)  # filtrar pos iss
        if self.sel_irrf:
            indexes, invoices = self.selected_tax(indexes, invoices, 1)  # filtrar pos irrf
        if self.sel_csrf:
            indexes, invoices = self.selected_tax(indexes, invoices, 2)  # filtrar pos csrf

        # if len(self.invoices) == len(invoices):
        #     return [], None
        return indexes, invoices

    def cnae_description(self, indexes: list, invoices: InvoicesList) -> tuple:
        if self.cnae_descr is None or self.cnae_descr == '':
            return indexes, invoices

        idxs = list()
        invs = InvoicesList([])
        for i, inv in zip(indexes, invoices):
            if inv.cnae.description.title() == self.cnae_descr:
                idxs.append(i)
                invs.add(inv)

        return idxs, invs

    def fed_id(self, indexes: list, invoices: InvoicesList) -> tuple:
        fed_id = self._fed_id.replace('.', '').replace('/', '').replace('-', '')

        if not fed_id or not fed_id.replace(' ', ''):  # se campo CNPJ/CPF está vazio
            return indexes, invoices

        if self.service_type:  # se tomado
            for index, invoice in enumerate(self.invoices):
                if fed_id in invoice.provider.fed_id:
                    indexes.append(index)
                    invoices.add(invoice)
        else:
            for index, invoice in enumerate(self.invoices):
                if fed_id in invoice.taker.fed_id:
                    indexes.append(index)
                    invoices.add(invoice)

        return indexes, invoices

    def selected_fed_id(self, indexes: list, invoices: InvoicesList) -> tuple:
        if self._selected_fed_id is None:
            return indexes, invoices

        idxs = list()
        invs = InvoicesList([])

        if self.service_type:  # tomado
            if self._selected_fed_id == 0:  # CNPJ
                for i, inv in zip(indexes, invoices):
                    if len(inv.provider.fed_id) == 14:
                        idxs.append(i)
                        invs.add(inv)
            elif self._selected_fed_id == 1:  # CPF
                for i, inv in zip(indexes, invoices):
                    if len(inv.provider.fed_id) == 11:
                        idxs.append(i)
                        invs.add(inv)
        else:  # prestador
            if self._selected_fed_id == 0:  # CNPJ
                for i, inv in zip(indexes, invoices):
                    if len(inv.taker.fed_id) == 14:
                        idxs.append(i)
                        invs.add(inv)
            elif self._selected_fed_id == 1:  # CPF
                for i, inv in zip(indexes, invoices):
                    if len(inv.taker.fed_id) == 11:
                        idxs.append(i)
                        invs.add(inv)

        return idxs, invs

    def selected_tax(self, indexes: list, invoices: InvoicesList, tax: int) -> tuple:
        idxs = list()
        invs = InvoicesList([])

        if tax == 0:  # iss
            if self.sel_iss:
                for i, inv in zip(indexes, invoices):
                    if inv.taxes.iss.value != '' and float(inv.taxes.iss.value) > 0:
                        idxs.append(i)
                        invs.add(inv)
        elif tax == 1:  # irrf
            if self.sel_irrf:
                for i, inv in zip(indexes, invoices):
                    if inv.taxes.irrf.value != '' and float(inv.taxes.irrf.value) > 0:
                        idxs.append(i)
                        invs.add(inv)
        elif tax == 2:  # csrf
            if self.sel_csrf:
                for i, inv in zip(indexes, invoices):
                    if inv.taxes.csrf.value != '' and float(inv.taxes.csrf.value) > 0:
                        idxs.append(i)
                        invs.add(inv)
        else:
            return indexes, invoices

        return idxs, invs

    def withheld_type(self, indexes: list, invoices: InvoicesList):
        if not self.wh_type:
            return indexes, invoices

        idxs = list()
        invs = InvoicesList([])

        # print('wh type:', self.wh_type)
        for index, invoice in zip(indexes, invoices):
            if invoice.withheld_type == str(self.wh_type):
                idxs.append(index)
                invs.add(invoice)

        return idxs, invs
