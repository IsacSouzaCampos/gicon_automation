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
            commands.append(self.sql_commands.is_launched(invoice))
        self.sql_run.run(commands)
        results = self.sql_run.result()

        to_launch = InvoicesList([])
        for invoice in self.invoices:
            taker_cnpj = invoice.taker.cnpj

            s = f'{taker_cnpj};{invoice.provider.cnpj};{invoice.serial_number}'
            if s not in results and (invoice.iss_value != '' or invoice.csrf_value != '' or invoice.ir_value != ''):
                to_launch.add_invoice(invoice)

        launch_keys = self.get_launch_keys(to_launch)
        commands = list()
        for invoice, launch_key in zip(to_launch, launch_keys):
            # print('invoice:', invoice.serial_number)
            commands.append(self.insert(invoice, launch_key))

        return commands

    def get_launch_keys(self, to_launch: InvoicesList) -> list:
        launch_keys_commands = list()
        for i in range(len(to_launch)):
            inv = to_launch.index(i)
            launch_keys_commands.append(self.sql_commands.lctofisent_key(inv.taker.cnpj, inv.service_type))

        # for lkc in launch_keys_commands:
        #     print(lkc)

        self.sql_run.run(launch_keys_commands)
        launch_keys = list(map(int, self.sql_run.result()))

        # corrige as chaves nos casos em que o serviço entre duas empresas se repete na lista
        launch_keys_dict = dict()
        for i in range(len(to_launch)):
            inv = to_launch.index(i)
            inv_id = f'{inv.taker.cnpj}{inv.provider.cnpj}'
            if inv_id not in launch_keys_dict:
                launch_keys_dict[inv_id] = 0
            else:
                launch_keys_dict[inv_id] += 1
            launch_keys[i] += launch_keys_dict[inv_id]

        # for lk in launch_keys:
        #     print(type(lk), lk)

        return launch_keys

    def insert(self, invoice: Invoice, launch_key) -> list:
        commands = SQLCommands()

        commands_list = list()
        if invoice.service_type:  # = 1 / serviço tomado
            launch = LCTOFISENTData(invoice, launch_key, invoice.service_type, IPI(), FunRural())

            # commands_list.append(f'\n\n/* Tomador: {invoice.taker.name} - Prestador: {invoice.provider.name}'
            #                      f' - Nota: {invoice.serial_number} */')
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
