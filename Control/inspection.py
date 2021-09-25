# -*- coding: utf-8 -*-
from openpyxl import Workbook
import Model.constants as constants
from Model.invoice import Invoice
from Model.excel import upload_sheet_content
from View.inspection import *
import View.super_inspection as mii
from Model.inspection_lib import *


def inspect(folder: str, xml_files: list, service_type: int) -> bool:
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
            return False
        elif option == 1:
            invoices_amount_type = 1
        else:
            return False

    # lista que será passada como parâmetro para ser mostrada na tela pela GUI
    results = list()

    # inicia janela da barra de progresso da conferência
    loading_window = start_inspection_loading_window()

    # insere os dados de cada um dos arquivos xml a serem analisados em results
    companies_cnpjs = list()
    companies_names = list()
    invoices = list()
    for i in range(len(xml_files)):
        xml_file = xml_files[i]
        invoice = Invoice(f'{folder}\\{xml_file}', service_type)
        invoices.append(invoice)  # implementar esta lista no código ao invés da lista de dados anterior

        # dados da empresa que está trocando serviço com o nosso cliente
        company_cnpj = invoice.provider.cnpj if service_type else invoice.taker.cnpj
        company_name = invoice.provider.name if service_type else invoice.taker.name
        if company_cnpj not in companies_cnpjs:
            companies_names.append(company_name)
            companies_cnpjs.append(company_cnpj)

        update_loading_window(loading_window, invoice.serial_number, i, len(xml_files))

    loading_window.close()

    n_errors = number_of_errors(invoices)

    if invoices_amount_type:  # se invoices_amount_type diferente de 0 / muito grande
        results = mii.show_results_table(invoices, n_errors)
    else:
        results = editable_table(invoices, companies_names, n_errors)

    # retorna false caso a conferência tenha sido fechada sem lançamento
    if results is None:
        return False

    # volta à tela principal enquanto a tela de conferência for fechada sem lançamento
    # while results is None:
    #     main_gui()

    xlsx_file_name = folder.split('/')[-1] + '.xlsx'
    create_xlsx(constants.HEADER1, results, xlsx_file_name, xml_files)

    for invoice in invoices:
        bd_insert(invoice)

    return True


def create_xlsx(header: list, results: list, file_name: str, xml_files: list) -> None:
    """
    Cria o arquivo XLSX com os dados extraídos da conferência.

    :param header:    Cabeçalho da tabela de dados.
    :type header:     (list)
    :param results:   Dados extraídos da conferência.
    :type results:    (list)
    :param file_name: Nome do arquivo XLSX a ser criado.
    :type file_name:  (str)
    :param xml_files: Nomes dos arquivos XML que foram conferidos.
    :type xml_files:  (list)
    """
    # cria o arquivo Excel a ser editado
    excel_file = Workbook()

    # gera uma planilha (sheet1)
    sheet1 = excel_file.active

    sheet1.append(header)

    # inserir na planilha os dados obtidos após confirmação de lançamento do usuário
    for row in results:
        # adiciona a célula 'CANCELADA' caso essa esteja na linha e limpa os valores dela para que
        # não sejam somados ao valor total, senão copia só até a natureza
        if 'CANCELADA' in row:
            row = row[:header.index('Natureza') + 1]
            row.append('CANCELADA')
        else:
            row = row[:header.index('Natureza') + 1]
        sheet1.append(row)

    upload_sheet_content(sheet1, xml_files)

    # salva o arquivo Excel
    # excel_file.save(f'{folder.split("/")[-1]}.xlsx')
    excel_file.save(file_name)

    # abre o arquivo Excel gerado
    # os.system(f'start excel.exe {folder.split("/")[-1]}.xlsx')


def bd_insert(invoice: Invoice) -> None:
    # import Model.sql
    pass
