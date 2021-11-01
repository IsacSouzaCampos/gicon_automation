# from Model.invoice import Invoice
from Model.sql import *
from Model.launch import LCTOFISData
from Model.ipi import IPI
from Model.funrural import FunRural

from Model.invoices_list import InvoicesList
from Model.constants import RESULTS_PATH


class SQLControl:
    def __init__(self, invoices: InvoicesList, service_type):
        self.invoices = invoices
        self.service_type = service_type
        self.sql_commands = SQLCommands(self.service_type)
        self.sql_run = SQLRun()

    def run(self):
        # print('SELECIONANDO NOTAS COM RETENÇÃO...')
        # to_launch = InvoicesList([])
        # for invoice in self.invoices:
        #     taker_id = invoice.taker.fed_id
        #
        #     s = f'{taker_id};{invoice.provider.fed_id};{invoice.serial_number}'
        #     iss_value = invoice.taxes.iss.value
        #     csrf_value = invoice.taxes.csrf.value
        #     irrf_value = invoice.taxes.irrf.value
        #     try:
        #         if ((iss_value != '' and float(iss_value) > 0) or (csrf_value != '' and float(csrf_value) > 0) or
        #                 (irrf_value != '' and float(irrf_value) > 0)):
        #             # print(invoice.taxes.iss.value, invoice.taxes.csrf.value, invoice.taxes.irrf.value)
        #             to_launch.add_invoice(invoice)
        #     except Exception as e:
        #         print(e, 'Erro ao detectar notas a serem lançadas no banco')

        self.clear_results_file()
        commands = list()
        for invoice in self.invoices:
            print(f'GERANDO CÓDIGO DE VERIFICAÇÃO DE NOTAS LANÇADAS... Nota: {invoice.serial_number}')
            commands.append(self.sql_commands.is_launched(invoice))
        print('RODANDO CÓDIGO DE VERIFICAÇÃO DE NOTAS LANÇADAS...')
        self.sql_run.run(commands)
        results = self.sql_run.result()

        to_launch = InvoicesList([])
        for i in range(len(self.invoices)):
            invoice = self.invoices.index(i)
            if f'{invoice.taker.fed_id};{invoice.provider.fed_id};{invoice.serial_number}' not in results:
                to_launch.add_invoice(invoice)

        launch_keys = self.get_launch_keys(to_launch)
        withheld_keys = self.get_launch_withheld_key(to_launch)
        commands = list()
        for invoice, launch_key, withheld_key in zip(to_launch, launch_keys, withheld_keys):
            print(f'GERANDO CÓDIGOS SQL DE INSERÇÃO... Nota: {invoice.serial_number}')

            commands.append(self.insert(invoice, launch_key, withheld_key))

        # print('RODANDO CÓDIGOS SQL DE INSERÇÃO...')
        # self.sql_run.run(commands)
        return commands

    def get_launch_keys(self, to_launch: InvoicesList) -> list:
        launch_keys_commands = list()
        for i in range(len(to_launch)):
            inv = to_launch.index(i)
            print(f'GERANDO CÓDIGO DE OBTENÇÃO DAS CHAVES DE LANÇAMENTO... Nota: {inv.serial_number}')
            fed_id = inv.taker.fed_id if self.service_type else inv.provider.fed_id
            launch_keys_commands.append(self.sql_commands.lctofis_key(fed_id))

        # for lkc in launch_keys_commands:
        #     print(lkc)

        print('RODANDO CÓDIGO DE OBTENÇÃO DAS CHAVES DE LANÇAMENTO...')
        self.sql_run.run(launch_keys_commands)

        try:
            launch_keys = list(map(int, self.sql_run.result()))
        except Exception as e:
            print(f'Error: {e}')
            return []  # retorna uma lista vazia caso todas as notas já estejam lançadas

        launch_keys = [lk + i for i, lk in enumerate(launch_keys)]

        # for lk in launch_keys:
        #     print(type(lk), lk)

        return launch_keys

    def get_launch_withheld_key(self, to_launch: InvoicesList) -> list:
        withheld_keys_commands = list()
        for i in range(len(to_launch)):
            inv = to_launch.index(i)
            print(f'GERANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS... Nota: {inv.serial_number}')
            fed_id = inv.taker.fed_id if self.service_type else inv.provider.fed_id
            withheld_keys_commands.append(self.sql_commands.lctofisretido_key(fed_id))

        print('RODANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS...')
        self.sql_run.run(withheld_keys_commands)

        try:
            withheld_keys = list(map(int, self.sql_run.result()))
        except Exception as e:
            print(f'Error: {e}')
            return []  # retorna uma lista vazia caso todas as notas já estejam lançadas

        withheld_keys = [wk + i for i, wk in enumerate(withheld_keys)]

        # for lk in launch_keys:
        #     print(type(lk), lk)

        return withheld_keys

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

    @staticmethod
    def clear_results_file():
        open(RESULTS_PATH, 'w').close()
