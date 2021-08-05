import os


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
XML_DIR = f'{ROOT_DIR}\\notas_xml'

COLUMN_TITLES = ['Nota', 'Razão Social Tomador', 'Razão Social Prestador', 'Renteção de ISS',
                 'Retenção IR', 'Retenção CSRF']

POSSIBLE_IR_NOTES = ['IR1,50%', 'IRRF1,50%', 'IR1,5%', 'IRRF1,5%','IR1.50%',
                     'IRRF1.50%', 'IR1.5%', 'IRRF1.5%','IRR$', 'IRRFR$',
                     
                     'IRR1,50%', 'IRR1,5%', 'IRR1.50%','IRR1.5%','IRRR$',
                     
                     'RETENCAODEIR']

POSSIBLE_CSRF_NOTES = ['PIS0,65%', 'PIS0.65%', 'PISR$',

                       'COFINS3%', 'COFINS3.0%', 'COFINS3.00%',
                       'COFINS3,0%', 'COFINS3,00%', 'COFINSR$',
                       
                       'CSLL1%', 'CSLL1.0%', 'CSLL1.00%',
                       'CSLL1,0%', 'CSLL1,00%', 'CSLLR$',
                       
                       'CSRF4,65%', 'CSRF4.65%', 'CSRFR$',
                       'CRF4,65%', 'CRF4.65%', 'CRFR$',
                       
                       'PISCOFINSCSLL', 'PISCOFINS', 'COFINSCSLL',
                       
                       'RETENCAODECSRF', 'RETENCAODEPIS', 'RETENCAODECOFINS',
                       'RETENCAODECRF']
