# from Model.invoice import Invoice
from Model.sql import *
from Model.launch import LCTOFISData
from Model.ipi import IPI
from Model.funrural import FunRural

from Model.invoices_list import InvoicesList


class SQLControl:
    def __init__(self, invoices: InvoicesList, service_type):
        self.invoices = invoices
        self.service_type = service_type
        self.sql_commands = SQLCommands(self.service_type)
        self.sql_run = SQLRun()

    def run(self):
        commands = list()
        print('GERANDO CÓDIGO DE VERIFICAÇÃO DE NOTAS LANÇADAS...')
        for invoice in self.invoices:
            commands.append(self.sql_commands.is_launched(invoice))
        print('RODANDO CÓDIGO DE VERIFICAÇÃO DE NOTAS LANÇADAS...')
        self.sql_run.run(commands)
        results = self.sql_run.result()

        print('SELECIONANDO NOTAS COM RETENÇÃO...')
        to_launch = InvoicesList([])
        for invoice in self.invoices:
            taker_id = invoice.taker.fed_id

            s = f'{taker_id};{invoice.provider.fed_id};{invoice.serial_number}'
            iss_value = invoice.taxes.iss.value
            csrf_value = invoice.taxes.csrf.value
            irrf_value = invoice.taxes.irrf.value
            try:
                if s not in results and ((iss_value != '' and float(iss_value) > 0) or
                                         (csrf_value != '' and float(csrf_value) > 0) or
                                         (irrf_value != '' and float(irrf_value) > 0)):
                    # print(invoice.taxes.iss.value, invoice.taxes.csrf.value, invoice.taxes.irrf.value)
                    to_launch.add_invoice(invoice)
            except Exception as e:
                print(e, 'Erro ao detectar notas a serem lançadas no banco')

        launch_keys = self.get_launch_keys(to_launch)
        withheld_keys = self.get_launch_withheld_key(to_launch)
        print('GERANDO CÓDIGOS SQL DE INSERÇÃO...')
        commands = list()
        for invoice, launch_key, withheld_key in zip(to_launch, launch_keys, withheld_keys):
            # print('invoice:', invoice.serial_number)
            commands.append(self.insert(invoice, launch_key, withheld_key))

        return commands

    def get_launch_keys(self, to_launch: InvoicesList) -> list:
        print('GERANDO CÓDIGO DE OBTENÇÃO DAS CHAVES DE LANÇAMENTO...')
        launch_keys_commands = list()
        for i in range(len(to_launch)):
            inv = to_launch.index(i)
            fed_id = inv.taker.fed_id if self.service_type else inv.provider.fed_id
            launch_keys_commands.append(self.sql_commands.lctofis_key(fed_id))

        # for lkc in launch_keys_commands:
        #     print(lkc)

        # print('keys commands:', launch_keys_commands)
        print('RODANDO CÓDIGO DE OBTENÇÃO DAS CHAVES DE LANÇAMENTO...')
        self.sql_run.run(launch_keys_commands)

        try:
            launch_keys = list(map(int, self.sql_run.result()))
        except Exception as e:
            print(f'Error: {e}')
            return []  # retorna uma lista vazia caso todas as notas já estejam lançadas

        # corrige as chaves nos casos em que o serviço entre duas empresas se repete na lista
        # launch_keys_dict = dict()
        # for i in range(len(to_launch)):
        #     inv = to_launch.index(i)
        #     inv_id = f'{inv.taker.fed_id}{inv.provider.fed_id}'
        #     print('inv id:', inv_id)
        #     if inv_id not in launch_keys_dict:
        #         launch_keys_dict[inv_id] = 0
        #     else:
        #         launch_keys_dict[inv_id] += 1
        #     launch_keys[i] += launch_keys_dict[inv_id]

        launch_keys = [lk + i for i, lk in enumerate(launch_keys)]

        # for lk in launch_keys:
        #     print(type(lk), lk)

        return launch_keys

    def get_launch_withheld_key(self, to_launch: InvoicesList) -> list:
        print('GERANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS...')
        withheld_keys_commands = list()
        for i in range(len(to_launch)):
            inv = to_launch.index(i)
            fed_id = inv.taker.fed_id if self.service_type else inv.provider.fed_id
            withheld_keys_commands.append(self.sql_commands.lctofisretido_key(fed_id))

        # print('withheld keys commands:', withheld_keys_commands)
        print('RODANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS...')
        self.sql_run.run(withheld_keys_commands)

        try:
            withheld_keys = list(map(int, self.sql_run.result()))
        except Exception as e:
            print(f'Error: {e}')
            return []  # retorna uma lista vazia caso todas as notas já estejam lançadas

        # corrige as chaves nos casos em que o serviço entre duas empresas se repete na lista
        # withheld_keys_dict = dict()
        # for i in range(len(to_launch)):
        #     inv = to_launch.index(i)
        #     inv_id = f'{inv.taker.fed_id}{inv.provider.fed_id}'
        #     if inv_id not in withheld_keys_dict:
        #         withheld_keys_dict[inv_id] = 0
        #     else:
        #         withheld_keys_dict[inv_id] += 1
        #     withheld_keys[i] += withheld_keys_dict[inv_id]

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
