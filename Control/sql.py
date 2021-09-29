from Model.invoice import Invoice


def bd_insert(invoice: Invoice, service_type: int) -> None:
    from Model.sql import SQL

    bd = SQL()

    # if invoice.serial_number != 379428:
    #     return

    if service_type == 1:  # serviço tomado
        taker_code = bd.get_company_code(invoice.taker.cnpj)
        provider_code = bd.get_company_code(invoice.provider.cnpj)

        print(invoice.taker.name, ':', taker_code)
        print(invoice.provider.name, ':', provider_code)
        print()

        # bd.invoice_in_bd(taker_code, provider_code, invoice.serial_number)
