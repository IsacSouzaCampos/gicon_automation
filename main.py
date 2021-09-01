import Control.invoice_inspection as control_invoice_inspection
import View.invoices_inspection as gui_invoice_inspection


def main():
    folder, xml_files, service_type = gui_invoice_inspection.main_gui()

    # print(folder)
    # print(xml_files)
    # print(service_type)

    control_invoice_inspection.inspect_invoices(folder, xml_files, service_type)


if __name__ == '__main__':
    main()
