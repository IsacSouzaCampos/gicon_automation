from Model.invoice import Invoice
from Model.sql import SQL
from Model.launch import LCTOFISENTData
from Model.ipi import IPI
from Model.funrural import FunRural


def bd_insert(invoice: Invoice, service_type: int, lctofisent_key: int or None,
              lctofisentretido_key: int or None) -> tuple:
    bd = SQL()

    commands = list()
    if service_type:  # = 1 / serviço tomado
        invoice.taker.code = bd.get_company_code(invoice.taker.cnpj, 0)  # cliente
        invoice.provider.code = bd.get_company_code(invoice.provider.cnpj, 1)  # outra empresa

        # print(invoice.taker.name, ':', invoice.taker.code)
        # print(invoice.provider.name, ':', invoice.provider.code)

        if bd.invoice_in_bd(invoice.taker.code, invoice.provider.code, invoice.serial_number):
            print(f'Nota {invoice.serial_number} já lançada')
        else:
            print(f'Nota {invoice.serial_number} não lançada')
            if not lctofisent_key:
                lctofisent_key = bd.lctofisent_key(invoice.taker.code)
            else:
                lctofisent_key += 1

            if not lctofisentretido_key:
                lctofisent_key = bd.lctofisentretido_key(invoice.taker.code)
            else:
                lctofisentretido_key += 1
            launch = LCTOFISENTData(invoice, lctofisent_key, lctofisentretido_key, lctofisentretido_key, IPI(),
                                    FunRural())

            commands.append(bd.lctofisent(launch))
            commands.append(bd.lctofisentcfop(launch))
    return commands, lctofisent_key
