from invoice import Invoice
from constants import *
import os

def offline_excel_results(invoice_file) -> list:
    """Gera a linha com os dados de retencao referentes a nota contida no arquivo invoice_file."""

    invoice_number = int(invoice_file.split('-')[-1].replace('.xml', ''))
    row = [invoice_number]

    invoice = Invoice(invoice_file)

    row.append('X' if invoice.iss_withheld() else '-')
    row.append('X' if invoice.is_ir_withheld() else '-')

    return row
