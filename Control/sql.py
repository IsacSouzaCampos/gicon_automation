from Model.invoice import Invoice
from Model.sql import SQL
from Model.launch import LCTOFISENTData
from Model.ipi import IPI
from Model.funrural import FunRural


def bd_insert(invoice: Invoice, service_type: int) -> list:
    bd = SQL()

    commands = list()
    if service_type:  # = 1 / serviço tomado
        invoice.taker.code = bd.get_company_code(invoice.taker.cnpj, 0)  # cliente
        invoice.provider.code = bd.get_company_code(invoice.provider.cnpj, 1)  # outra empresa

        if bd.invoice_in_bd(invoice):
            print(f'Nota {invoice.serial_number} - tomador: {invoice.taker.code} - prestador: {invoice.provider.code}'
                  f' já lançada')
        else:
            print(f'Nota {invoice.serial_number} não lançada')
            launch = LCTOFISENTData(invoice, IPI(), FunRural())

            commands.append(clear_command(bd.lctofisent(launch)))
            commands.append(clear_command(bd.lctofisentcfop(launch)))
            commands.append(clear_command(bd.lctofisentvaloriss(launch)))
            commands.append(clear_command(bd.lctofisentretido(launch)))
    return commands


def clear_command(command: str) -> str:
    while '  ' in command:
        command = command.replace('  ', ' ')
    return command
