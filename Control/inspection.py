from View.inspection import *
from View.inspection import Loading

from Model.invoices_list import InvoicesList
from Model.invoice import Invoice

from View.inspection import PopUp


def inspect(folder: str, xml_files: list, service_type: int) -> tuple:
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

    # inicia janela da barra de progresso da conferência
    load_insp = Loading()
    load_insp.total_size = len(xml_files)
    load_insp.inspection()

    # insere os dados de cada um dos arquivos xml a serem analisados em results
    # companies_cnpjs = list()
    # companies_names = list()
    cnae_descriptions = ['']
    invoices = InvoicesList([])  # precisa receber lista vazia '[]' para não acumular notas conferidas antes
    for i in range(len(xml_files)):
        xml_file = xml_files[i]
        invoice = Invoice(f'{folder}\\{xml_file}', service_type)
        invoices.add(invoice)  # implementar esta lista no código ao invés da lista de dados anterior

        if invoice.cnae.description.title() not in cnae_descriptions:
            cnae_descriptions.append(invoice.cnae.description.title())

        load_insp.update(invoice.serial_number, i)
    load_insp.close()

    if invoices.empty():
        PopUp().msg('A pasta selecionada não contém XML\'s.')
        return False, InvoicesList([])

    res_tb = ResultTable(invoices, cnae_descriptions, invoices.number_of_errors())
    is_finished, invoices = res_tb.show()

    return is_finished, invoices
