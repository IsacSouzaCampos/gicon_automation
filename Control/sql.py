from Model.invoice import Invoice
from Model.sql import SQLCommands
from Model.launch import LCTOFISENTData
from Model.ipi import IPI
from Model.funrural import FunRural


def bd_insert(invoice: Invoice, service_type: int) -> list:
    commands = SQLCommands()

    commands_list = list()
    if service_type:  # = 1 / serviço tomado
        print(f'Nota {invoice.serial_number}')
        launch = LCTOFISENTData(service_type, invoice, IPI(), FunRural())

        commands_list.append(clear_command(commands.lctofisent(launch)))
        commands_list.append(clear_command(commands.lctofisentcfop(launch)))
        commands_list.append(clear_command(commands.lctofisentvaloriss(launch)))
        commands_list.append(clear_command(commands.lctofisentretido(launch)))
    return commands_list


def clear_command(command: str) -> str:
    while '  ' in command:
        command = command.replace('  ', ' ')
    return command
