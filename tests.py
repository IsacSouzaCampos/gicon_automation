from Control.inspection import inspect


# TIPOS DE SERVICO (PRESTADO, TOMADO):
# service_type = 0
service_type = 1

# PASTAS E XMLS PRA CONFERÊNCIA
# ***Apenas uma nota***
# folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/auto_posto_sao_pedro_junho'
# xml_files = ['nota_527612-9598.xml']

# folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/08'
# xml_files = ['nota_169818-184.xml', 'nota_169818-185.xml', 'nota_169818-186.xml']

folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/ibagy_agosto'
xml_files = ['nota_725017-314669.xml', 'nota_725017-314979.xml', 'nota_725017-315276.xml', 'nota_725017-318708.xml',
             'nota_725017-319213.xml', 'nota_725017-319215.xml', 'nota_725017-319218.xml']

# ***Possui notas canceladas e uma quantidade um pouco maior***
# folder = 'C:/Users/Fiscal_20/Documents/gicon_automation/xml(s)/0524239_janeiro_xmls (20)'
# xml_files = ['nota_681316-814.xml', 'nota_681316-815.xml', 'nota_681316-816.xml', 'nota_681316-817.xml',
#              'nota_681316-818.xml', 'nota_681316-819.xml', 'nota_681316-820.xml', 'nota_681316-821.xml',
#              'nota_681316-824.xml', 'nota_681316-825.xml', 'nota_681316-826.xml', 'nota_681316-827.xml',
#              'nota_681316-828.xml', 'nota_681316-829.xml']

inspect(folder, xml_files, service_type)
