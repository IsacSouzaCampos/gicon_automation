from openpyxl import Workbook
from Model.constants import *
from Model.invoice import Invoice
from Model.excel_functions import upload_sheet_content
from View.invoices_inspection import *
import View.many_invoices_inspection as mii
from Model.invoice_inspection_lib import *


def inspect_invoices(folder: str, xml_files: list, service_type: int) -> bool:
    """Cria um arquivo Excel contendo uma planilha com os dados referentes ao servico contido na nota"""

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

    # cria o arquivo Excel a ser editado
    excel_file = Workbook()

    # gera uma planilha (sheet1)
    sheet1 = excel_file.active

    # insere o cabeçalho da planilha
    # 'Nº Nota', 'Data', 'Valor Bruto', 'Retenção ISS',
    # 'Retenção IR', 'Retenção CSRF', 'Valor Líquido', 'Natureza'
    header = [COLUMN_TITLES[0], COLUMN_TITLES[1], COLUMN_TITLES[2], COLUMN_TITLES[3], COLUMN_TITLES[4],
              COLUMN_TITLES[5], COLUMN_TITLES[6], COLUMN_TITLES[7]]

    sheet1.append(header)

    # lista que será passada como parâmetro para ser mostrada na tela pela GUI
    results = list()

    # inicia janela da barra de progresso da conferência
    loading_window = start_inspection_loading_window()

    # insere os dados de cada um dos arquivos xml a serem analisados
    # import time
    for i in range(len(xml_files)):
        invoice_file = xml_files[i]
        invoice = Invoice(folder, invoice_file, service_type)
        update_loading_window(loading_window, invoice.d['numeroserie'], i, len(xml_files))
        row = invoice.data_list()
        results.append(row)
        # time.sleep(.05)

    loading_window.close()

    n_errors = number_of_errors(results)

    if invoices_amount_type:  # se invoices_amount_type diferente de 0 / muito grande
        results = mii.show_results_table(header, results, n_errors)
    else:
        results = editable_table(results, n_errors)

    # retorna false caso a conferência tenha sido fechada sem lançamento
    if results is None:
        return False

    # volta à tela principal enquanto a tela de conferência for fechada sem lançamento
    while results is None:
        main_gui()

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
    excel_file.save(f'{folder.split("/")[-1]}.xlsx')

    # abre o arquivo Excel gerado
    # os.system(f'start excel.exe {folder.split("/")[-1]}.xlsx')

    return True
