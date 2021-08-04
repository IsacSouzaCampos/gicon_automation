import data_management as dm
from openpyxl import Workbook
from constants import *
import os


def main():
    # cria o arquivo Excel a ser editado
    excel_file = Workbook()

    # gera uma planilha (sheet1)
    sheet1 = excel_file.active

    # insere o cabecalho da planilha
    sheet1.append([COLUMN1_TEXT, COLUMN2_TEXT, COLUMN3_TEXT])

    # insere os dados de cada um dos arquivos xml a serem analisados
    for invoice_file in os.listdir(XML_DIR):
        if '.xml' not in invoice_file:
            continue
        row = dm.offline_excel_results(invoice_file)
        sheet1.append(row)
    
    # centraliza o conteudo das celulas das colunas 2 e 3
    from openpyxl.styles import Alignment
    for cell_row in range(len( os.listdir(XML_DIR) )):
        cell = sheet1.cell(row=(cell_row + 2), column=2)
        cell.alignment = Alignment(horizontal='center')

        cell = sheet1.cell(row=(cell_row + 2), column=3)
        cell.alignment = Alignment(horizontal='center')
    
    # centraliza celula[1, 1] (value='Notas')
    cell = sheet1.cell(row=1, column=1)
    cell.alignment = Alignment(horizontal='center')
    
    # arruma a largura das colunas 2 e 3
    from openpyxl.utils import get_column_letter
    sheet1.column_dimensions[get_column_letter(2)].width = len(COLUMN2_TEXT)
    sheet1.column_dimensions[get_column_letter(3)].width = len(COLUMN3_TEXT)
    
    # salva o arquivo Excel
    excel_file.save('output_data.xlsx')


if __name__ == '__main__':
    main()
