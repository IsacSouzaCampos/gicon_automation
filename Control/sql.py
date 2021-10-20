# from Model.invoice import Invoice
from Model.sql import *
from Model.launch import LCTOFISENTData
from Model.ipi import IPI
from Model.funrural import FunRural

from Model.invoices_list import InvoicesList


class SQLControl:
    def __init__(self, invoices: InvoicesList):
        self.invoices = invoices
        self.sql_commands = SQLCommands()
        self.sql_run = SQLRun()

    def run(self):
        commands = list()
        for invoice in self.invoices:
            commands.append(self.sql_commands.launched(invoice))
        self.sql_run.run(commands)
        results = self.sql_run.result()

        to_launch = InvoicesList([])
        for invoice in self.invoices:
            taker_cnpj = invoice.taker.cnpj

            s = f'{taker_cnpj};{invoice.provider.cnpj};{invoice.serial_number}'
            if s not in results and (invoice.iss_value != '' or invoice.csrf_value != '' or invoice.ir_value != ''):
                to_launch.add_invoice(invoice)
                print('invoice:', invoice.serial_number)

        launch_keys = list()
        commands = list()
        for invoice, launch_key in zip(to_launch, launch_keys):
            print('invoice:', invoice.serial_number)
            commands.append(self.insert(invoice, launch_key))

        return commands

    def insert(self, invoice: Invoice, launch_key) -> list:
        commands = SQLCommands()

        commands_list = list()
        if invoice.service_type:  # = 1 / serviço tomado
            print(f'Nota {invoice.serial_number}')
            launch = LCTOFISENTData(invoice, launch_key, invoice.service_type, IPI(), FunRural())

            commands_list.append(self.clear_command(commands.lctofisent(launch)))
            # commands_list.append(self.clear_command(commands.lctofisentcfop(launch)))
            # commands_list.append(self.clear_command(commands.lctofisentvaloriss(launch)))
            # commands_list.append(self.clear_command(commands.lctofisentretido(launch)))
        return commands_list

    @staticmethod
    def clear_command(command: str) -> str:
        while '  ' in command:
            command = command.replace('  ', ' ')
        return command
