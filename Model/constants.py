import sys


ROOT_DIR = sys.path[0]
# XML_DIR = f'{ROOT_DIR}\\notas_para_analise'

COLUMN_TITLES = ['Nº Nota', 'Data', 'Valor Bruto', 'Retenção ISS',
                 'Retenção IR', 'Retenção CSRF', 'Valor Líquido', 'Natureza']

IR_KEYWORDS = ['ir1,50%', 'irrf1,50%', 'ir1,5%', 'irrf1,5%', 'ir1.50%',
               'irrf1.50%', 'ir1.5%', 'irrf1.5%', 'irr$', 'irrfr$',
                     
               'irr1,50%', 'irr1,5%', 'irr1.50%', 'irr1.5%', 'irrr$',
                     
               'retencaodeir', 'recolherir', 'irrf']

PIS_KEYWORDS = ['pis0,65%', 'pis0.65%', 'pis,65%', 'pis.65%', 'pisr$', 'retencaodepis']

COFINS_KEYWORDS = ['cofins3%', 'cofins3.0%', 'cofins3.00%',
                   'cofins3,0%', 'cofins3,00%', 'cofinsr$',
                   'retencaodecofins']

CSLL_KEYWORDS = ['csll1%', 'csll1.0%', 'csll1.00%',
                 'csll1,0%', 'csll1,00%', 'csllr$', 'retencaodecsll']

CSRF_KEYWORDS = ['csrf4,65%', 'csrf4.65%', 'csrfr$',
                 'crf4,65%', 'crf4.65%', 'crfr$',
                       
                 'piscofinscsll', 'piscofins', 'cofinscsll',
                       
                 'retencaodecsrf', 'recolhercsrf'
                 'retencaodecrf', 'recolhercrf']

ALL_KEYWORDS = [IR_KEYWORDS, PIS_KEYWORDS, COFINS_KEYWORDS, CSLL_KEYWORDS, CSRF_KEYWORDS]
