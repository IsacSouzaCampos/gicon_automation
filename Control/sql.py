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
        self.to_launch = InvoicesList([])
        self.launch_keys = list()
        self.withheld_keys = list()
        self.commands = list()
        self.failed_invoices = InvoicesList([])

    def run(self):

        self.clear_results_file()

        # self.set_companies_codes()

        commands = list()
        for invoice in self.invoices:
            print(f'GERANDO CÓDIGO DE VERIFICAÇÃO DE NOTAS LANÇADAS... Nota: {invoice.serial_number}')
            commands.append(self.sql_commands.is_launched(invoice))
        print('RODANDO CÓDIGO DE VERIFICAÇÃO DE NOTAS LANÇADAS...')
        self.sql_run.run(commands)
        results = self.sql_run.result()

        for i in range(len(self.invoices)):
            invoice = self.invoices.index(i)
            if f'{invoice.taker.fed_id};{invoice.provider.fed_id};{invoice.serial_number}' not in results:
                person_fed_id = invoice.provider.fed_id if self.service_type else invoice.taker.fed_id
                if len(person_fed_id) == 14:  # se é CNPJ
                    self.to_launch.add(invoice)

        self.set_launch_keys()
        self.set_withheld_keys()
        for invoice, launch_key, withheld_key in zip(self.to_launch, self.launch_keys, self.withheld_keys):
            print(f'GERANDO CÓDIGOS SQL DE INSERÇÃO... Nota: {invoice.serial_number}')
            comp_codes_ok = self.companies_codes_ok(invoice)
            if comp_codes_ok:
                self.commands.append(self.insert(invoice, launch_key, withheld_key))
            else:
                self.failed_invoices.add(invoice)

    def set_launch_keys(self) -> list:
        launch_keys_commands = list()
        controler = list()
        for invoice in self.to_launch:
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
        for invoice in self.to_launch:
            company_code = invoice.taker.code if self.service_type else invoice.provider.code
            if company_code in aux.keys():
                aux[company_code] += 1
                launch_keys.append(aux[company_code])
            else:
                aux[company_code] = results[count]
                launch_keys.append(aux[company_code])
                count += 1

        for lk in launch_keys:
            print(type(lk), lk)

        self.launch_keys = launch_keys

    def set_withheld_keys(self) -> list:
        withheld_keys_commands = list()
        for invoice in self.to_launch:
            print(f'GERANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS... Nota: {invoice.serial_number}')
            company_code = invoice.taker.code if self.service_type else invoice.provider.code
            withheld_keys_commands.append(self.sql_commands.lctofisretido_key(company_code))

        print('RODANDO CHAVES DE LANÇAMENTO DA TABELA RETIDOS...')
        # for i in range(len(withheld_keys_commands)):
        #     print('withheld key command:', withheld_keys_commands[i])
        self.sql_run.run(withheld_keys_commands)

        try:
            results = list(map(int, self.sql_run.result()))
        except Exception as e:
            print(f'Error: {e}')
            return []  # retorna uma lista vazia caso todas as notas já estejam lançadas

        # withheld_keys = [wk + i for i, wk in enumerate(withheld_keys)]
        withheld_keys = list()
        aux = dict()
        count = 0
        for invoice in self.to_launch:
            company_code = invoice.taker.code if self.service_type else invoice.provider.code
            if company_code in aux.keys():
                aux[company_code] += 1
                withheld_keys.append(aux[company_code])
            else:
                aux[company_code] = results[count]
                withheld_keys.append(aux[company_code])
                count += 1

        # for lk in launch_keys:
        #     print(type(lk), lk)

        self.withheld_keys = withheld_keys

    def set_company_code(self, index):
        invoice = self.invoices.index(index)

        client_command = list()
        person_command = list()

        if self.service_type:
            client_command.append(self.sql_commands.get_company_code(invoice.taker.fed_id, 1))
            person_command.append(self.sql_commands.get_company_code(invoice.provider.fed_id, 0))
        else:
            client_command.append(self.sql_commands.get_company_code(invoice.provider.fed_id, 0))
            person_command.append(self.sql_commands.get_company_code(invoice.taker.fed_id, 1))

        self.sql_run.run(client_command)
        client_code = self.sql_run.result()[0]

        self.sql_run.run(person_command)
        person_code = self.sql_run.result()[0]

        invoice.client.code = client_code
        invoice.person.code = person_code

        # print('client:', client_code)
        # print('person:', person_code)

        invoice.taker.code = invoice.client.code if self.service_type else invoice.person.code
        invoice.provider.code = invoice.person.code if self.service_type else invoice.client.code

        return client_code, person_code

    def set_companies_codes(self):
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

    @staticmethod
    def companies_codes_ok(invoice: Invoice):
        # if str(invoice.serial_number) == '90108':
        #     print('taker:', invoice.taker.code, 'provider:', invoice.provider.code)
        return invoice.taker.code != 'NULL' and invoice.provider.code != 'NULL'

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
