from Control.inspection import InspectControl

from View.inspection import MainGUI

import Model.initiate as initiate
import Model.excel as excel
import Model.constants as constants
from Model.constants import SYS_PATH
from Model.invoices_list import InvoicesList

from Control.sql import SQLControl

from View.inspection_lib import insertion_commands, create_delete_commands
from View.inspection import ResultTable
from View.inspection import Loading


class Main:
    def main(self):
        initiate.init()

        main_gui = MainGUI()
        main_gui.show()

        inspection_control = InspectControl(main_gui.folder, main_gui.xml_files, main_gui.service_type)
        invoices = inspection_control.inspect()

        sql_control = SQLControl(invoices, main_gui.service_type)

        invoices = self.update_companies_codes(main_gui.xml_files, sql_control, invoices)
        invoices = self.update_invoices_infos(invoices, len(invoices))

        res_tb = ResultTable(invoices, inspection_control.cnae_descriptions, invoices.number_of_errors())
        is_finished, invoices = res_tb.show()

        while not is_finished:
            main_gui.show()
            is_finished, invoices = inspection_control.inspect()

        xlsx_file_name = main_gui.folder.split('/')[-1] + '.xlsx'
        excel.create_xlsx(constants.HEADER1, invoices, xlsx_file_name, main_gui.xml_files)

        # seleciona apenas notas com retenção
        to_launch = InvoicesList([])
        for invoice in invoices:
            if invoice.to_launch:
                to_launch.add(invoice)

        sql_control.run()
        to_launch = sql_control.to_launch
        self.update_infos_table(to_launch)

        insertion_commands(sql_control.commands)
        if sql_control.launch_keys and sql_control.withheld_keys:
            create_delete_commands(sql_control.launch_keys[0], sql_control.withheld_keys[0])

    @staticmethod
    def update_companies_codes(xml_files, sql_control, invoices):
        load_insp = Loading()
        load_insp.total_size = len(xml_files)
        load_insp.inspection()
        for index, invoice in enumerate(sql_control.invoices):
            if len(invoice.person.fed_id) == 14:
                load_insp.update(invoice.serial_number, index)
                sql_control.set_company_code(index)
                # print('taker:', sql_control.invoices.index(index).taker.code)
                # print('provider:', sql_control.invoices.index(index).provider.code)
        load_insp.close()

        return sql_control.invoices

    @staticmethod
    def update_invoices_infos(invoices: InvoicesList, n_invoices):
        with open(SYS_PATH + r'\query.csv', 'r') as fin:
            services_infos = fin.readlines()

            load_insp = Loading()
            load_insp.total_size = n_invoices
            load_insp.inspection()
            for index, invoice in enumerate(invoices):
                if len(invoice.person.fed_id) != 14:  # se não for cnpj
                    continue

                load_insp.update(invoice.serial_number, index)
                infos = [invoice.taker.code, invoice.provider.code, invoice.cnae.description,
                         invoice.taxes.iss.is_withheld, invoice.taxes.irrf.is_withheld,
                         invoice.taxes.csrf.is_withheld]
                infos = list(map(str, infos))

                for ser_infos in services_infos:
                    splitted_ser_infos = ser_infos.split(';')
                    print('splitted infos:', splitted_ser_infos[:-2])
                    print('infos:', infos)
                    if infos == splitted_ser_infos[:-2]:
                        invoice.withheld_type = splitted_ser_infos[-2]
                        invoice.nature = splitted_ser_infos[-1]
        load_insp.close()

        return invoices

    @staticmethod
    def update_infos_table(to_launch):
        with open(SYS_PATH + r'\query.csv', 'r') as fin:
            services_infos = fin.readlines()

        with open(SYS_PATH + r'\query.csv', 'a') as fout:
            for invoice in to_launch:
                infos = [invoice.taker.code, invoice.provider.code, invoice.cnae.description,
                         invoice.taxes.iss.is_withheld, invoice.taxes.irrf.is_withheld,
                         invoice.taxes.csrf.is_withheld]

                for ser_infos in services_infos:
                    if infos == ser_infos.split(';')[:-2]:
                        break
                else:
                    if invoice.taker.code == 'NULL' or invoice.provider.code == 'NULL':
                        break
                    s = f'{invoice.withheld_type};{invoice.nature}'
                    # print('s:', s)
                    print(';'.join([str(info) for info in infos]) + ';' + s, file=fout)


if __name__ == '__main__':
    Main().main()
