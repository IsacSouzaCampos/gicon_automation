# from Model.invoice import Invoice
from Model.sql import *
from Model.launch import LCTOFISData
from Model.ipi import IPI
from Model.funrural import FunRural
from Model.invoices_list import InvoicesList
# from Model.constants import RESULTS_PATH

from View.loading import Loading
# from View.popup import PopUp


class SQLControl:
    def __init__(self, invoices: InvoicesList, service_type):
        self.invoices = invoices
        self.service_type = service_type
        self.sql_commands = SQLCommands(self.service_type)
        self.sql_run = SQLRun()
        self.to_launch = InvoicesList([])
        self.launch_key_cmd = str()
        self.withheld_key_cmd = str()
        self.commands = list()
        self.failed_invoices = InvoicesList([])

    def run(self):

        # self.clear_results_file()

        for invoice in self.to_launch:
            self.set_company_code(invoice)

        self.launch_key_cmd = self.get_launch_key_cmd()
        self.launch_key_cmd = self.get_withheld_keys_cmds()

        self.gen_insertion_commands()

    def get_launch_key_cmd(self):
        fed_id = self.invoices.index(0).client.fed_id
        client_code_cmd = self.sql_commands.get_company_code(fed_id, self.service_type)
        return self.sql_commands.lctofisretido_key(client_code_cmd)

    # def update_launch_keys(self, launch_keys):
    #     launch_keys = [lk + i for i, lk in enumerate(launch_keys)]
    #     self.launch_keys = launch_keys

    def get_withheld_keys_cmds(self):
        fed_id = self.invoices.index(0).client.fed_id
        client_code_cmd = self.sql_commands.get_company_code(fed_id, self.service_type)
        return self.sql_commands.lctofisretido_key(client_code_cmd)

    def set_company_code(self, invoice):
        if self.service_type:
            invoice.client.code = self.sql_commands.get_company_code(invoice.taker.fed_id, 1)
            invoice.person.code = self.sql_commands.get_company_code(invoice.provider.fed_id, 0)
        else:
            invoice.client.code = self.sql_commands.get_company_code(invoice.provider.fed_id, 0)
            invoice.person.code = self.sql_commands.get_company_code(invoice.taker.fed_id, 1)

        invoice.taker.code = invoice.client.code if self.service_type else invoice.person.code
        invoice.provider.code = invoice.person.code if self.service_type else invoice.client.code

    @staticmethod
    def companies_codes_ok(invoice: Invoice):
        # if str(invoice.serial_number) == '90108':
        #     print('taker:', invoice.taker.code, 'provider:', invoice.provider.code)
        return invoice.taker.code != 'NULL' and invoice.provider.code != 'NULL'

    def gen_insertion_commands(self):
        load_insertion_commands = Loading('Gerando código de inserção... ', total_size=len(self.to_launch))
        load_insertion_commands.start()

        for index, invoice in zip(range(len(self.to_launch)), self.to_launch):
            load_insertion_commands.update(invoice.serial_number, index)
            comp_codes_ok = self.companies_codes_ok(invoice)
            if comp_codes_ok:
                self.commands.append(self.insert(invoice, self.launch_key_cmd, self.withheld_key_cmd))
            else:
                self.failed_invoices.add(invoice)

        load_insertion_commands.close()

    def insert(self, invoice: Invoice, launch_key, withheld_key) -> list:
        commands = SQLCommands(self.service_type)

        commands_list = list()
        # if invoice.service_type:  # = 1 / serviço tomado
        launch = LCTOFISData(invoice, launch_key, invoice.service_type, IPI(), FunRural())

        commands_list.append(self.clear_command(commands.lctofis(launch)))
        commands_list.append(self.clear_command(commands.lctofiscfop(launch)))
        commands_list.append(self.clear_command(commands.lctofisvaloriss(launch)))
        commands_list.append(self.clear_command(commands.lctofisretido(launch, withheld_key)))
        return commands_list

    @staticmethod
    def clear_command(command: str) -> str:
        while '  ' in command:
            command = command.replace('  ', ' ')
        return command

    # @staticmethod
    # def clear_results_file():
    #     open(RESULTS_PATH, 'w').close()
