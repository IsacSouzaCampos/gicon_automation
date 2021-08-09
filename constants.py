import sys


ROOT_DIR = sys.path[0]
XML_DIR = f'{ROOT_DIR}\\notas_para_analise'

COLUMN_TITLES = ['Nº Nota', 'Data', 'Valor Bruto', 'Retenção de ISS',
                 'Retenção IR', 'Retenção CSRF']

POSSIBLE_IR_NOTES = ['ir1,50%', 'irrf1,50%', 'ir1,5%', 'irrf1,5%', 'ir1.50%',
                     'irrf1.50%', 'ir1.5%', 'irrf1.5%', 'irr$', 'irrfr$',
                     
                     'irr1,50%', 'irr1,5%', 'irr1.50%', 'irr1.5%', 'irrr$',
                     
                     'retencaodeir']

POSSIBLE_CSRF_NOTES = ['pis0,65%', 'pis0.65%', 'pisr$',

                       'cofins3%', 'cofins3.0%', 'cofins3.00%',
                       'cofins3,0%', 'cofins3,00%', 'cofinsr$',
                       
                       'csll1%', 'csll1.0%', 'csll1.00%',
                       'csll1,0%', 'csll1,00%', 'csllr$',
                       
                       'csrf4,65%', 'csrf4.65%', 'csrfr$',
                       'crf4,65%', 'crf4.65%', 'crfr$',
                       
                       'piscofinscsll', 'piscofins', 'cofinscsll',
                       
                       'retencaodecsrf', 'retencaodepis', 'retencaodecofins',
                       'retencaodecrf']
