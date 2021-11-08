import Control.inspection as inspection

from View.inspection import MainGUI

import Model.initiate as initiate
import Model.excel as excel
import Model.constants as constants
from Model.constants import SYS_PATH
from Model.invoices_list import InvoicesList

from Control.sql import SQLControl
from View.inspection_lib import insertion_commands, create_delete_commands


def main():
    initiate.init()

    main_gui = MainGUI()
    # folder, xml_files, service_type = main_gui.show()
    main_gui.show()

    is_finished, invoices = inspection.inspect(main_gui.folder, main_gui.xml_files, main_gui.service_type)
    while not is_finished:
        main_gui.show()
        is_finished, invoices = inspection.inspect(main_gui.folder, main_gui.xml_files, main_gui.service_type)

    xlsx_file_name = main_gui.folder.split('/')[-1] + '.xlsx'
    excel.create_xlsx(constants.HEADER1, invoices, xlsx_file_name, main_gui.xml_files)

    # seleciona apenas notas com retenção
    to_launch = InvoicesList([])
    for invoice in invoices:
        if invoice.to_launch:
            to_launch.add(invoice)

    sql_control = SQLControl(to_launch, main_gui.service_type)
    sql_control.run()

    with open(SYS_PATH + r'\query.csv', 'r') as fin:
        services_infos = fin.readlines()

    to_launch = sql_control.to_launch
    with open(SYS_PATH + r'\query.csv', 'w+') as fout:
        for invoice in to_launch:
            infos = f'{invoice.taker.code};{invoice.provider.code};{invoice.cnae.description};' \
                    f'{invoice.taxes.iss.is_withheld};{invoice.taxes.irrf.is_withheld};' \
                    f'{invoice.taxes.csrf.is_withheld};{invoice.withheld_type};{invoice.nature};'

            if infos not in services_infos:
                print(infos, file=fout)

    insertion_commands(sql_control.commands)
    create_delete_commands(sql_control.launch_keys[0], sql_control.withheld_keys[0])


if __name__ == '__main__':
    main()
