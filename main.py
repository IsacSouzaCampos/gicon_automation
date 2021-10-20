import Control.inspection as inspection
from Control.sql import SQLControl

import View.short_inspection as gui_inspection

import Model.initiate as initiate
import Model.excel as excel
import Model.constants as constants
from View.inspection_lib import insertion_commands


def main():
    initiate.init()

    folder, xml_files, service_type = gui_inspection.main_gui()

    is_finished, invoices = inspection.inspect(folder, xml_files, service_type)
    while not is_finished:
        folder, xml_files, service_type = gui_inspection.main_gui()
        is_finished, invoices = inspection.inspect(folder, xml_files, service_type)

    xlsx_file_name = folder.split('/')[-1] + '.xlsx'
    excel.create_xlsx(constants.HEADER1, invoices, xlsx_file_name, xml_files)

    sql_control = SQLControl(invoices)
    commands = sql_control.run()

    insertion_commands(commands)


if __name__ == '__main__':
    main()
