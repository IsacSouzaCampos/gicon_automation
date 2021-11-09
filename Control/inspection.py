from View.inspection import *
from View.inspection import Loading

from Model.invoices_list import InvoicesList
from Model.invoice import Invoice
from Model.constants import SYS_PATH

from View.inspection import PopUp


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
        self.cnae_descriptions = list()

    def inspect(self) -> InvoicesList:
        # inicia janela da barra de progresso da conferência
        load_insp = Loading()
        load_insp.total_size = len(self.xml_files)
        load_insp.inspection()

        # insere os dados de cada um dos arquivos xml a serem analisados em results
        # companies_cnpjs = list()
        # companies_names = list()
        self.cnae_descriptions = ['']
        invoices = InvoicesList([])  # precisa receber lista vazia '[]' para não acumular notas conferidas antes
        for i in range(len(self.xml_files)):
            xml_file = self.xml_files[i]
            invoice = Invoice(f'{self.folder}\\{xml_file}', self.service_type)
            invoices.add(invoice)  # implementar esta lista no código ao invés da lista de dados anterior

            if invoice.cnae.description.title() not in self.cnae_descriptions:
                self.cnae_descriptions.append(invoice.cnae.description.title())

            load_insp.update(invoice.serial_number, i)
        load_insp.close()

        if invoices.empty():
            PopUp().msg('A pasta selecionada não contém XML\'s.')
            return InvoicesList([])

        return invoices
