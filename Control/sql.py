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

        self.clear_results_file()

        self.get_companies_codes()
        self.remove_company_code_errors()

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
                to_launch.add(invoice)

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
        controler = list()
        for invoice in to_launch:
            print(f'GERANDO CÓDIGO DE OBTENÇÃO DAS CHAVES DE LANÇAMENTO... Nota: {invoice.serial_number}')
            company_code = invoice.taker.code if self.service_type else invoice.provider.code
            if company_code in controler:
                continue
            launch_keys_commands.append(self.sql_commands.lctofis_key(company_code))
            controler.append(company_code)

        # for lkc in launch_keys_commands:
        #     print(lkc)

        print('RODANDO CÓDIGO DE OBTENÇÃO DAS CHAVES DE LANÇAMENTO...')
        self.sql_run.run(launch_keys_commands)

        try:
            results = list(map(int, self.sql_run.result()))
        except Exception as e:
            print(f'Error: {e}')
            return []  # retorna uma lista vazia caso todas as notas já estejam lançadas

        # launch_keys = [lk + i for i, lk in enumerate(launch_keys)]
        launch_keys = list()
        aux = dict()
        count = 0
        for invoice in to_launch:
            company_code = invoice.taker.code if self.service_type else invoice.provider.code
            if company_code in aux.keys():
                launch_keys.append(aux[company_code] + 1)
                aux[company_code] += 1
            else:
                aux[company_code] = results[count]
                count += 1

        for lk in launch_keys:
            print(type(lk), lk)

        return launch_keys

    def get_launch_withheld_key(self, to_launch: InvoicesList) -> list:
        withheld_keys_commands = list()
        for i in range(len(to_launch)):
            inv = to_launch.index(i)
            print(f'GERANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS... Nota: {inv.serial_number}')
            company_code = inv.taker.code if self.service_type else inv.provider.code
            withheld_keys_commands.append(self.sql_commands.lctofisretido_key(company_code))

        print('RODANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS...')
        # for i in range(len(withheld_keys_commands)):
        #     print('withheld key command:', withheld_keys_commands[i])
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

    def get_companies_codes(self):
        clients_commands = list()
        persons_commands = list()
        if self.service_type:  # se tomado
            for i in range(len(self.invoices)):
                invoice = self.invoices.index(i)
                clients_commands.append(self.sql_commands.get_company_code(invoice.taker.fed_id, 1))
                persons_commands.append(self.sql_commands.get_company_code(invoice.provider.fed_id, 0))
        else:
            for i in range(len(self.invoices)):
                invoice = self.invoices.index(i)
                clients_commands.append(self.sql_commands.get_company_code(invoice.provider.fed_id, 0))
                persons_commands.append(self.sql_commands.get_company_code(invoice.taker.fed_id, 1))

        # print('clients commands:', clients_commands)
        # print('\n\npersons commands:', persons_commands)

        self.sql_run.run(clients_commands)
        clients_codes = self.sql_run.result()
        # print('clients result:', clients_codes)
        # print('clients result len:', len(clients_codes))
        self.sql_run.run(persons_commands)
        persons_codes = self.sql_run.result()
        # print('persons result:', persons_codes)
        # print('persons result len:', len(persons_codes))

        if self.service_type:  # se tomado
            for i, client_code, person_code in zip(range(len(self.invoices)), clients_codes, persons_codes):
                invoice = self.invoices.index(i)
                invoice.taker.code = client_code
                invoice.provider.code = person_code
        else:
            for i, client_code, person_code in zip(range(len(self.invoices)), clients_codes, persons_codes):
                invoice = self.invoices.index(i)
                invoice.taker.code = person_code
                invoice.provider.code = client_code

    def remove_company_code_errors(self):
        error_invoices_idxs = list()
        for i in range(len(self.invoices)):
            invoice = self.invoices.index(i)
            if invoice.taker.code == 'NULL' or invoice.provider.code == 'NULL':
                error_invoices_idxs.append(i)

        error_invoices = InvoicesList([])
        for idx in error_invoices_idxs:
            invoice = self.invoices.index(idx)
            error_invoices.add(invoice)
            self.invoices.remove(invoice)

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
