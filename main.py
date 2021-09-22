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


if __name__ == '__main__':
    main()
