from Control.invoice_inspection import inspect_invoices


# folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/auto_posto_sao_pedro_junho'
# xml_files = ['nota_527612-9598.xml']

folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/ibagy_agosto'
xml_files = ['nota_725017-314669.xml', 'nota_725017-314979.xml', 'nota_725017-315276.xml', 'nota_725017-318708.xml',
             'nota_725017-319213.xml', 'nota_725017-319215.xml', 'nota_725017-319218.xml']

service_type = 0

inspect_invoices(folder, xml_files, service_type)
