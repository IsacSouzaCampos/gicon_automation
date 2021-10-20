from View.short_inspection import *
import View.long_inspection as mii

from Model.inspection_lib import *
from Model.invoices_list import InvoicesList
from Model.invoice import Invoice


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

    invoices_amount_type = 0
    # testa se o número de notas está dentro do limite de conferências por vez
    if len(xml_files) > MAX_INVOICES:
        option = max_invoices_popup()
        if option == 0:  # se opcao == 0
            separate_xml_files(folder, xml_files)
            return False, InvoicesList([])
        elif option == 1:
            # invoices_amount_type = 1
            mii.temp_msg('Funcionalidade a ser atualizada!')
            return False, InvoicesList([])
        else:
            return False, InvoicesList([])

    # inicia janela da barra de progresso da conferência
    loading_window = start_inspection_loading_window()

    # insere os dados de cada um dos arquivos xml a serem analisados em results
    companies_cnpjs = list()
    companies_names = list()
    invoices = InvoicesList([])  # precisa receber lista vazia '[]' para não acumular notas conferidas antes
    for i in range(len(xml_files)):
        xml_file = xml_files[i]
        invoice = Invoice(f'{folder}\\{xml_file}', service_type)
        invoices.add_invoice(invoice)  # implementar esta lista no código ao invés da lista de dados anterior

        # dados da empresa que está trocando serviço com o nosso cliente
        company_cnpj = invoice.provider.cnpj if service_type else invoice.taker.cnpj
        company_name = invoice.provider.name if service_type else invoice.taker.name
        if company_cnpj not in companies_cnpjs:
            companies_names.append(company_name)
            companies_cnpjs.append(company_cnpj)

        update_loading_window(loading_window, invoice.serial_number, i, len(xml_files))

    loading_window.close()

    n_errors = invoices.number_of_errors()

    if invoices_amount_type:  # se invoices_amount_type diferente de 0 / muito grande
        # results = mii.show_results_table(invoices, n_errors)
        pass
    else:
        invoices = editable_table(invoices, companies_names, n_errors)

    return (True, invoices) if not invoices.empty() else (False, invoices)
