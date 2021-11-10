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

        size = len(main_gui.xml_files)
        service_type = main_gui.service_type

        inspection_control = InspectControl(main_gui.folder, main_gui.xml_files, main_gui.service_type)
        invoices = inspection_control.inspect()

        sql_control = SQLControl(invoices, main_gui.service_type)

        invoices = self.update_companies_codes(size, sql_control)
        client_code = self.get_client_code(invoices)
        invoices = self.update_invoices_infos(invoices, len(invoices), client_code, service_type)

        res_tb = ResultTable(invoices, inspection_control.cnae_code, invoices.number_of_errors())
        is_finished, invoices = res_tb.show()

        while not is_finished:
            main_gui.show()
            is_finished, invoices = inspection_control.inspect()

        xlsx_file_name = main_gui.folder.split('/')[-1] + '.xlsx'
        excel.create_xlsx(constants.HEADER1, invoices, xlsx_file_name, main_gui.xml_files)

        # seleciona apenas notas com retenção
        for invoice in invoices:
            if invoice.to_launch:
                sql_control.to_launch.add(invoice)

        sql_control.run()
        to_launch = sql_control.to_launch
        self.update_infos_table(to_launch, client_code, service_type)

        insertion_commands(sql_control.commands)
        if sql_control.launch_keys and sql_control.withheld_keys:
            create_delete_commands(sql_control.launch_keys[0], sql_control.withheld_keys[0])

        # print('failed invoices:')
        # for invoice in sql_control.failed_invoices:
        #     print(f'{invoice.serial_number} - provider:', invoice.provider.code, ' - taker:', invoice.taker.code)

    @staticmethod
    def update_companies_codes(size, sql_control):
        load_insp = Loading()
        load_insp.total_size = size
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
    def update_invoices_infos(invoices: InvoicesList, n_invoices, client_code, service_type):
        service_str = 'tomado' if service_type else 'prestado'
        path = fr'{SYS_PATH}\{service_str}\{client_code}.csv'

        import os.path
        if not os.path.exists(path):
            open(path, 'a').close()

        with open(path, 'r') as fin:
            services_infos = fin.readlines()

            load_insp = Loading()
            load_insp.total_size = n_invoices
            load_insp.inspection()
            for index, invoice in enumerate(invoices):
                if len(invoice.person.fed_id) != 14:  # se não for cnpj
                    continue

                load_insp.update(invoice.serial_number, index)
                infos = [invoice.person.code, invoice.cnae.code, invoice.taxes.iss.is_withheld,
                         invoice.taxes.irrf.is_withheld, invoice.taxes.csrf.is_withheld]
                infos = list(map(str, infos))

                for ser_infos in services_infos:
                    splitted_ser_infos = ser_infos.split(';')
                    # print('splitted infos:', splitted_ser_infos[:-2])
                    # print('infos:', infos)
                    if infos == splitted_ser_infos[:-2]:
                        invoice.withheld_type = splitted_ser_infos[-2]
                        invoice.nature = splitted_ser_infos[-1]
        load_insp.close()

        return invoices

    @staticmethod
    def update_infos_table(to_launch, client_code, service_type):
        service_str = 'tomado' if service_type else 'prestado'
        path = fr'{SYS_PATH}\{service_str}\{client_code}.csv'
        with open(path, 'r') as fin:
            services_infos = fin.readlines()

        with open(path, 'a') as fout:
            new_infos = list()
            for invoice in to_launch:
                # print('person code:', invoice.person.code)
                infos = [invoice.person.code, invoice.cnae.code, invoice.taxes.iss.is_withheld,
                         invoice.taxes.irrf.is_withheld, invoice.taxes.csrf.is_withheld]
                infos = list(map(str, infos))

                if ';'.join(infos) in new_infos:
                    continue

                # print('infos:', infos, type(infos))
                # print('new_infos[0]:', new_infos[0] if len(new_infos) else '',
                #       type(new_infos[0]) if len(new_infos) else '')

                for ser_infos in services_infos:
                    # print('infos:', infos)
                    # print('serv_infos:', ser_infos.split(';')[:-2])
                    if infos == ser_infos.split(';')[:-2]:
                        break
                else:
                    if invoice.person.code != 'NULL':
                        # print('else serial number:', invoice.serial_number)
                        s = f'{invoice.withheld_type};{invoice.nature}'
                        # print('s:', s)
                        print((';'.join([str(info) for info in infos]) + ';' + s).strip(), file=fout)
                        new_infos.append(';'.join(infos))
            print(new_infos)

    @staticmethod
    def get_client_code(invoices: InvoicesList) -> int:
        for invoice in invoices:
            if invoice.client.code is not None:
                client_code = invoice.client.code
                break
        else:
            raise Exception('Cliente não encontrado no BD.')
        return client_code


if __name__ == '__main__':
    Main().main()
