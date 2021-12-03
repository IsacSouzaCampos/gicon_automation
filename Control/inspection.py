from View.loading import Loading

from Model.invoices_list import InvoicesList
from Model.invoice import Invoice

from View.warnings import Warnings


class InspectControl:
    def __init__(self, folder: str, xml_files: list, service_type: int):
        """
        Cria um arquivo Excel contendo uma planilha com os dados referentes ao servico contido na nota

        :param folder:       Caminho da pasta que contém as notas a serem conferidas.
        :type folder:        (str)
        :param xml_files:    Nomes dos arquivos XML a serem conferidos.
        :type xml_files:     (list)
        :param service_type: Tipo de serviço das notas conferidas (tomado, prestado).
        :type service_type:  (int)
        :return:             Verdadeiro se houver êxito na conferência, caso contrário, False.
        :rtype:              (bool)
        """
        self.folder = folder
        self.xml_files = xml_files
        self.service_type = service_type
        self.min_date = [99, 99, 9999]
        self.max_date = [0, 0, 0]

    def inspect(self) -> InvoicesList:
        # inicia janela da barra de progresso da conferência
        load_insp = Loading('Conferindo... ', total_size=len(self.xml_files))
        load_insp.start()

        # self.cnae_code = ['']
        invoices = InvoicesList([])  # precisa receber lista vazia '[]' para não acumular notas conferidas antes
        for i in range(len(self.xml_files)):
            xml_file = self.xml_files[i]
            invoice = Invoice(f'{self.folder}\\{xml_file}', self.service_type)
            self.update_dates_range(invoice.issuance_date)
            invoices.add(invoice)  # implementar esta lista no código ao invés da lista de dados anterior

            load_insp.update(invoice.serial_number, i)
        load_insp.close()

        if invoices.empty():
            Warnings().msg('A pasta selecionada não contém XML\'s.')
            return InvoicesList([])

        return invoices

    def update_dates_range(self, date: str):
        date = [int(d) for d in date.split('/')]
        self.update_min_date(date)
        self.update_max_date(date)

    def update_min_date(self, date: list):
        if date[2] < self.min_date[2]:
            self.min_date = date
            return
        if date[1] < self.min_date[1]:
            self.min_date = date
            return
        if date[0] < self.min_date[0]:
            self.min_date = date

    def update_max_date(self, date: list):
        if date[2] > self.max_date[2]:
            self.max_date = date
            return
        if date[1] > self.max_date[1]:
            self.max_date = date
            return
        if date[0] > self.max_date[0]:
            self.max_date = date
