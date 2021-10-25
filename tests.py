from Control.inspection import inspect
from Control.sql import SQLControl

import Model.excel as excel
import Model.constants as constants

from View.inspection_lib import insertion_commands
import os


def test():
    # TIPOS DE SERVICO (PRESTADO, TOMADO):
    # service_type = 0
    service_type = 1

    # PASTAS E XMLS PRA CONFERÊNCIA
    # ***Apenas uma nota***
    # folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/auto_posto_sao_pedro_junho'
    # folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/08'
    # folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/0524239_janeiro_xmls (20)'
    # folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/ibagy_agosto'
    folder = r'C:\Users\Fiscal_20\Documents\gicon_automation\xml(s)\teste_bd'

    # ***Possui notas canceladas e uma quantidade um pouco maior***
    # folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/0524239_janeiro_xmls (20)'

    xml_files = [file for file in os.listdir(folder) if '.xml' in file]

    is_finished, invoices = inspect(folder, xml_files, service_type)

    xlsx_file_name = folder.split('/')[-1] + '.xlsx'
    excel.create_xlsx(constants.HEADER1, invoices, xlsx_file_name, xml_files)

    sql_control = SQLControl(invoices)
    commands = sql_control.run()

    insertion_commands(commands)


if __name__ == '__main__':
    test()
