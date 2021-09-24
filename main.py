# -*- coding: utf-8 -*-
import Control.inspection as control_inspection
import View.inspection as gui_inspection


def main():
    folder, xml_files, service_type = gui_inspection.main_gui()

    # print(folder)
    # print(xml_files)
    # print(service_type)

    invoice_inspected = control_inspection.inspect(folder, xml_files, service_type)

    while not invoice_inspected:
        folder, xml_files, service_type = gui_inspection.main_gui()
        invoice_inspected = control_inspection.inspect(folder, xml_files, service_type)

    # import os
    # os.system(r'py -2 Model\sql.py "select SEQ,CHAVELCTOFISENT,CODIGOPRODUTO from LCTOFISENTPRODUTO where '
    #           r'codigoempresa = 116 and CODIGOCFOP in (1403,2403) and datalctofis between \'01.10.2019\' '
    #           r'and \'31.10.2019\';"')

    # import subprocess
    # python3_command = "GUI_examples\\bd_connection.py \"select SEQ,CHAVELCTOFISENT,CODIGOPRODUTO from " \
    #                   "LCTOFISENTPRODUTO where codigoempresa = 116 and CODIGOCFOP in (1403,2403) and datalctofis " \
    #                   "between '01.10.2019' and '31.10.2019';\""  # launch your python2 script using bash
    # process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
    # output, error = process.communicate()  # receive output from the python2 script
    # print(output, error)


if __name__ == '__main__':
    main()
