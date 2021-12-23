from Model.sql import *
from Model.launch import LCTOFISData
from Model.ipi import IPI
from Model.funrural import FunRural
from Model.invoices_list import InvoicesList
from Model.company import Company
from Model.invoice import Invoice

from View.loading import Loading


class SQLControl:
    def __init__(self, invoices: InvoicesList, service_type):
        self.invoices = invoices
        self.service_type = service_type
        self.sql_commands = SQLCommands(self.service_type)
        # self.sql_run = SQLRun()
        self.commands = list()

    def run(self):
        self.gen_insertion_commands()

    def set_companies_codes(self, invoice):
        if self.service_type:
            invoice.client.code = self.sql_commands.get_company_code(invoice.taker.fed_id, 1)
            invoice.person.code = self.sql_commands.get_company_code(invoice.provider.fed_id, 0)
        else:
            invoice.client.code = self.sql_commands.get_company_code(invoice.provider.fed_id, 0)
            invoice.person.code = self.sql_commands.get_company_code(invoice.taker.fed_id, 1)

        invoice.taker.code = invoice.client.code if self.service_type else invoice.person.code
        invoice.provider.code = invoice.person.code if self.service_type else invoice.client.code

    def gen_insertion_commands(self):
        load_insertion_commands = Loading('Gerando código de inserção... ', total_size=len(self.invoices))
        load_insertion_commands.start()

        for index, invoice in zip(range(len(self.invoices)), self.invoices):
            load_insertion_commands.update(invoice.serial_number, index)
            self.commands.append(self.insert_commands(invoice))

        load_insertion_commands.close()

    def insert_commands(self, invoice: Invoice) -> list:
        commands = SQLCommands(self.service_type)

        commands_list = list()
        launch = LCTOFISData(invoice, invoice.service_type, IPI(), FunRural())
        commands_list.append(self.clear_command(commands.lctofisretido(launch)))
        if invoice.is_canceled:
            commands_list.append(self.clear_command(commands.update_lctofiscfop(invoice)))
        return commands_list

    def get_company_code_cmd(self, company: Company, comp_type: int):
        return self.sql_commands.get_company_code(company.fed_id, comp_type)

    @staticmethod
    def clear_command(command: str) -> str:
        while '  ' in command:
            command = command.replace('  ', ' ')
        return command
