from Model.sql import *
from Model.launch import LCTOFISData
from Model.ipi import IPI
from Model.funrural import FunRural
from Model.invoices_list import InvoicesList

from View.loading import Loading


class SQLControl:
    def __init__(self, invoices: InvoicesList, service_type):
        self.invoices = invoices
        self.service_type = service_type
        self.sql_commands = SQLCommands(self.service_type)
        self.sql_run = SQLRun()
        self.to_launch = InvoicesList([])
        self.commands = list()
        self.failed_invoices = InvoicesList([])

    def run(self):
        for invoice in self.to_launch:
            self.set_company_code(invoice)

        self.gen_insertion_commands()

    def get_launch_key_cmd(self):
        fed_id = self.invoices.index(0).client.fed_id
        client_code_cmd = self.sql_commands.get_company_code(fed_id, self.service_type)
        return self.sql_commands.lctofis_key(client_code_cmd)

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
        return invoice.taker.code != 'NULL' and invoice.provider.code != 'NULL'

    def gen_insertion_commands(self):
        load_insertion_commands = Loading('Gerando código de inserção... ', total_size=len(self.to_launch))
        load_insertion_commands.start()

        for index, invoice in zip(range(len(self.to_launch)), self.to_launch):
            load_insertion_commands.update(invoice.serial_number, index)
            comp_codes_ok = self.companies_codes_ok(invoice)
            if comp_codes_ok:
                self.commands.append(self.insert(invoice))
            else:
                self.failed_invoices.add(invoice)

        load_insertion_commands.close()

    def insert(self, invoice: Invoice) -> list:
        commands = SQLCommands(self.service_type)

        commands_list = list()
        launch = LCTOFISData(invoice, invoice.service_type, IPI(), FunRural())

        fed_id = self.invoices.index(0).client.fed_id
        client_code_cmd = self.sql_commands.get_company_code(fed_id, self.service_type)
        key = self.sql_commands.lctofis_key(client_code_cmd)
        commands_list.append(self.clear_command(commands.lctofis(launch, key)))

        key = self.sql_commands.lctofis_key(client_code_cmd, 0)
        commands_list.append(self.clear_command(commands.lctofiscfop(launch, key)))
        commands_list.append(self.clear_command(commands.lctofisvaloriss(launch, key)))
        commands_list.append(self.clear_command(commands.lctofisretido(launch, key)))
        return commands_list

    @staticmethod
    def clear_command(command: str) -> str:
        while '  ' in command:
            command = command.replace('  ', ' ')
        return command
