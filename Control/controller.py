import Model.excel as excel
import Model.constants as constants
from Model.invoices_list import InvoicesList
from Model.insertion_commands import InsertionCommands

from Control.sql import SQLControl
from Control.inspection import InspectControl

from View.inspection import MainGUI
from View.inspection import ResultTable
from View.loading import Loading
from View.popup import PopUp
from View.insertion_commands import InsertionCommandsView


class Controller:
    def run(self):
        sql_control = SQLControl
        main_gui = MainGUI()
        while True:
            main_gui.show()

            service_type = main_gui.service_type

            inspection_control = InspectControl(main_gui.folder, main_gui.xml_files, main_gui.service_type)
            invoices = inspection_control.inspect()

            if invoices.repeated_fed_ids():
                s = 'tomadora' if service_type else 'prestadora'
                PopUp().msg(f'Há mais de uma empresa {s} nas notas. Certifique-se de manter notas da  mesma '
                            f'empresa na pasta.')
                continue

            # size = len(invoices)
            # invoices = self.update_companies_codes(size, sql_control)

            res_tb = ResultTable(invoices, inspection_control.cnae_code, invoices.number_of_errors())
            is_finished, invoices = res_tb.show()

            if is_finished:
                break

        xlsx_file_name = main_gui.folder.split('/')[-1] + '.xlsx'
        excel.create_xlsx(constants.HEADER1, invoices, xlsx_file_name, main_gui.xml_files)

        # seleciona apenas notas com retenção
        # for invoice in invoices:
        #     if invoice.to_launch:
        #         sql_control.to_launch.add(invoice)

        sql_control = SQLControl(invoices, main_gui.service_type)
        if invoices.index(0).client.code is None:
            for invoice in invoices:
                invoice.client.set_code(sql_control.get_company_code_cmd(invoice.client, service_type))
        for invoice in invoices:
            person_serv_type = 0 if service_type else 1
            invoice.person.set_code(sql_control.get_company_code_cmd(invoice.person, person_serv_type))
        sql_control.run()

        insertion_commands = InsertionCommands(sql_control.commands, self.get_client_fed_id(invoices), service_type)
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
