import Control.inspection as inspection
from Control.sql import SQLControl

from View.inspection import MainGUI

import Model.initiate as initiate
import Model.excel as excel
import Model.constants as constants
from View.inspection_lib import insertion_commands


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

    sql_control = SQLControl(invoices, main_gui.service_type)
    commands = sql_control.run()

    insertion_commands(commands)


if __name__ == '__main__':
    main()
