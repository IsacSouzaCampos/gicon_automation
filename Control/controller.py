import sys

import Model.excel as excel
import Model.constants as constants
from Model.invoices_list import InvoicesList
from Model.insertion_commands import InsertionCommands

from Control.sql import SQLControl
from Control.inspection import InspectControl

from View.inspection import MainGUI
from View.inspection import ResultTable
from View.loading import Loading
from View.warnings import Warnings
from View.insertion_commands import InsertionCommandsView


class Controller:
    def run(self):
        main_gui = MainGUI()
        while True:
            main_gui.show()

            service_type = main_gui.service_type

            inspection_control = InspectControl(main_gui.folder, main_gui.xml_files, main_gui.service_type)
            invoices = inspection_control.inspect()

            repeated_invoices = self.get_repeated_invoices(invoices)
            if repeated_invoices:
                to_remove_indexes, unfixable_invoices = self.fix_repeated_invoices(invoices, repeated_invoices)
                if unfixable_invoices:
                    # print(f'{unfixable_invoices = }')
                    Warnings().repeated_invoices(unfixable_invoices)
                    sys.exit()
                else:
                    for index in reversed(sorted(to_remove_indexes)):
                        invoices.remove(index)

            # for invoice in invoices:
            #     print(f'is_canceled: {invoice.is_canceled = }')

            if invoices.repeated_fed_ids():
                s = 'tomadora' if service_type else 'prestadora'
                Warnings().msg(f'Há mais de uma empresa {s} nas notas. Certifique-se de manter notas da  mesma '
                               f'empresa na pasta.')
                continue

            res_tb = ResultTable(invoices, inspection_control.cnae_code, invoices.number_of_errors())
            is_finished, invoices = res_tb.show()

            if is_finished:
                break

        xlsx_file_name = main_gui.folder.split('/')[-1] + '.xlsx'
        excel.create_xlsx(constants.HEADER1, invoices, xlsx_file_name, main_gui.xml_files)

        sql_control = SQLControl(invoices, main_gui.service_type)
        if invoices.index(0).client.code is None:
            for invoice in invoices:
                invoice.client.set_code(sql_control.get_company_code_cmd(invoice.client, service_type))
        for invoice in invoices:
            person_serv_type = 0 if service_type else 1
            invoice.person.set_code(sql_control.get_company_code_cmd(invoice.person, person_serv_type))

        sql_control.run()

        insertion_commands = InsertionCommands(sql_control.commands, self.get_client_fed_id(invoices),
                                               invoices.index(0).client.code, service_type)
        text = insertion_commands.to_string()
        text += '\n\n' + insertion_commands.updates_commands()

        InsertionCommandsView(text).show()

    @staticmethod
    def update_companies_codes(n_invoices, sql_control):
        load_insp = Loading('Obtendo código das empresas... ', total_size=n_invoices)
        load_insp.start()
        for index, invoice in enumerate(sql_control.invoices):
            if len(invoice.person.fed_id) == 14:
                load_insp.update(invoice.serial_number, index)
                sql_control.set_companies_codes(invoice)
        load_insp.close()

        return sql_control.invoices

    @staticmethod
    def get_client_fed_id(invoices: InvoicesList) -> int:
        client_fed_id = int()
        for invoice in invoices:
            if invoice.client.fed_id is not None:
                client_fed_id = invoice.client.fed_id
                break
        return client_fed_id

    def get_repeated_invoices(self, invoices: InvoicesList) -> InvoicesList:
        aux = list()
        repeated_aux = list()
        repeated = InvoicesList()
        for invoice in invoices:
            identifier = [invoice.serial_number, self.format_fed_id(invoice.client.fed_id)]
            if identifier in aux:
                if identifier in repeated_aux:
                    continue
                repeated_aux.append(identifier)
                repeated.add(invoice)
            else:
                aux.append(identifier)

        return repeated

    @staticmethod
    def fix_repeated_invoices(invoices: InvoicesList, repeated_invoices: InvoicesList) -> tuple:
        to_remove_indexes = list()
        unfixable = list()
        for repeated in repeated_invoices:
            elements = list()
            repeated_identifier = [repeated.serial_number, repeated.client.fed_id]
            for invoice in invoices:
                if repeated_identifier == [invoice.serial_number, invoice.client.fed_id]:
                    elements.append(invoice)
            for index, element in enumerate(elements):
                if element.is_canceled:
                    for i, e in enumerate(elements):  # se nota não for a cancelada, adiciona em to_remove
                        if i != index:
                            # print(f'to_remove: {invoices.get_index(elements[i]) = }')
                            to_remove_indexes.append(invoices.get_index(elements[i]))
                    break
            else:
                unfixable.append([repeated.serial_number, repeated.client.fed_id, repeated.file_path.split('\\')[-1]])
        return to_remove_indexes, unfixable

    @staticmethod
    def format_fed_id(fed_id):
        if len(fed_id) == 14:
            fed_id = f'{fed_id[:2]}.{fed_id[2:5]}.{fed_id[5:8]}/{fed_id[8:12]}-{fed_id[12:]}'
        elif len(fed_id) == 11:
            fed_id = f'{fed_id[:3]}.{fed_id[3:6]}.{fed_id[6:9]}-{fed_id[9:]}'
        return fed_id
