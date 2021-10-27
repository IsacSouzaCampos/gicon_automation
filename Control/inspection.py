from View.inspection import *
from View.inspection import Loading

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

    # invoices_amount_type = 0
    # # testa se o número de notas está dentro do limite de conferências por vez
    # if len(xml_files) > const.MAX_INVOICES:
    #     from View.short_inspection import PopUp
    #     pop_up = PopUp
    #     option = pop_up.max_invoices()
    #     if option == 0:  # se opcao == 0
    #         separate_xml_files(folder, xml_files)
    #         return False, InvoicesList([])
    #     elif option == 1:
    #         # invoices_amount_type = 1
    #         mii.temp_msg('Funcionalidade a ser atualizada!')
    #         return False, InvoicesList([])
    #     else:
    #         return False, InvoicesList([])

    # inicia janela da barra de progresso da conferência
    load_insp = Loading()
    load_insp.total_size = len(xml_files)
    load_insp.inspection()

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

        load_insp.update(invoice.serial_number, i)

    load_insp.close()

    res_tb = ResultTable(invoices, companies_names, invoices.number_of_errors())
    # is_finished = bool()
    # invoices = InvoicesList([])
    # if invoices_amount_type:  # se invoices_amount_type diferente de 0 / muito grande
    #     # results = mii.show_results_table(invoices, n_errors)
    #     pass
    # else:
    is_finished, invoices = res_tb.show()

    return is_finished, invoices
