from openpyxl import Workbook
from Model.constants import *
from Model.invoice import Invoice
from Model.excel_functions import upload_sheet_content
from View.invoice_inspection import *


def inspect_invoices(folder: str, xml_files: list, service_type: int) -> None:
    """Cria um arquivo Excel contendo uma planilha com os dados referentes ao servico contido na nota"""

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
    import time
    for i in range(len(xml_files)):
        invoice_file = xml_files[i]
        invoice = Invoice(folder, invoice_file, service_type)
        update_loading_window(loading_window, invoice.d['numeroserie'], i, len(xml_files))
        row = invoice.data_list()
        results.append(row)
        time.sleep(.2)

    loading_window.close()

    results = taken_service_edition_screen(header, results) if service_type else \
        provided_service_editing_screen(header, results)

    # inserir na planilha os dados obtidos após confirmação de lançamento do usuário
    for row in results:
        sheet1.append(row)
    
    upload_sheet_content(sheet1, xml_files)

    # salva o arquivo Excel
    excel_file.save(f'{folder.split("/")[-1]}.xlsx')

    # abre o arquivo Excel gerado
    # os.system(f'start excel.exe {folder.split("/")[-1]}.xlsx')
