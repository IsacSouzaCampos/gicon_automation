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
            # remover os zeros iniciais pois a consulta SQL os remove
            while taker_cnpj[0] == '0':
                taker_cnpj = taker_cnpj[1:]

            s = f'{taker_cnpj};{invoice.provider.cnpj};{invoice.serial_number}'
            if s not in results:
                to_launch.add_invoice(invoice)

        for invoice in to_launch:
            print(f'{invoice.taker.cnpj};{invoice.provider.cnpj};{invoice.serial_number}')
        # insertion_commands(launch_commands)

    def bd_insert(self, invoice: Invoice, service_type: int) -> list:
        commands = SQLCommands()

        commands_list = list()
        if service_type:  # = 1 / serviço tomado
            print(f'Nota {invoice.serial_number}')
            launch = LCTOFISENTData(service_type, invoice, IPI(), FunRural())

            commands_list.append(self.clear_command(commands.lctofisent(launch)))
            commands_list.append(self.clear_command(commands.lctofisentcfop(launch)))
            commands_list.append(self.clear_command(commands.lctofisentvaloriss(launch)))
            commands_list.append(self.clear_command(commands.lctofisentretido(launch)))
        return commands_list

    @staticmethod
    def clear_command(command: str) -> str:
        while '  ' in command:
            command = command.replace('  ', ' ')
        return command
