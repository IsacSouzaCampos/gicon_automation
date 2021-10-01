from Model.invoice import Invoice
from Model.sql import SQL
from Model.launch import LCTOFISENTData
from Model.ipi import IPI
from Model.funrural import FunRural


def bd_insert(invoice: Invoice, service_type: int, launch_key: int or None) -> tuple:
    bd = SQL()

    launch_command = str()
    if service_type:  # = 1 / serviço tomado
        invoice.taker.code = bd.get_company_code(invoice.taker.cnpj, 0)  # cliente
        invoice.provider.code = bd.get_company_code(invoice.provider.cnpj, 1)  # outra empresa

        # print(invoice.taker.name, ':', invoice.taker.code)
        # print(invoice.provider.name, ':', invoice.provider.code)

        if bd.invoice_in_bd(invoice.taker.code, invoice.provider.code, invoice.serial_number):
            print(f'Nota {invoice.serial_number} já lançada')
        else:
            print(f'Nota {invoice.serial_number} não lançada')
            if not launch_key:
                launch_key = bd.launch_key(invoice.taker.code)
            else:
                launch_key += 1
            launch = LCTOFISENTData(invoice, launch_key, IPI(), FunRural())
            launch_command = bd.lctofisent(launch)
    return launch_command, launch_key
