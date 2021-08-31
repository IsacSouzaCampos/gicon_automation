import sys


ROOT_DIR = sys.path[0]
MAX_INVOICES = 100

COLUMN_TITLES = ['Nº Nota', 'Data', 'Valor Bruto', 'Retenção ISS',
                 'Retenção IR', 'Retenção CSRF', 'Valor Líquido', 'Natureza']

IR_KEYWORDS = ['ir1,50%', 'irrf1,50%', 'ir1,5%', 'irrf1,5%', 'ir1.50%',
               'irrf1.50%', 'ir1.5%', 'irrf1.5%', 'irr$', 'irrfr$',
                     
               'irr1,50%', 'irr1,5%', 'irr1.50%', 'irr1.5%', 'irrr$',
                     
               'retencaoir', 'retencaodeir', 'retencoesir', 'recolherir', 'irrf']

PIS_KEYWORDS = ['pis0,65%', 'pis0.65%', 'pis,65%', 'pis.65%', 'pisr$',
                'retencaopis', 'retencaodepis', 'retencoespis', 'recolherpis']

COFINS_KEYWORDS = ['cofins3%', 'cofins3.0%', 'cofins3.00%',
                   'cofins3,0%', 'cofins3,00%', 'cofinsr$',
                   'retencaocofins', 'retencaodecofins', 'retencoescofins', 'recolhercofins']

CSLL_KEYWORDS = ['csll1%', 'csll1.0%', 'csll1.00%',
                 'csll1,0%', 'csll1,00%', 'csllr$',
                 'retencaocsll', 'retencaodecsll', 'retencoescsll', 'recolhercsll']

CSRF_KEYWORDS = ['csrf4,65%', 'csrf4.65%', 'csrfr$',
                 'crf4,65%', 'crf4.65%', 'crfr$',

                 'pcc4,65%', 'pcc4.65%', 'pccr$'
                       
                 'piscofinscsll', 'piscofins', 'cofinscsll',
                       
                 'retencaocsrf', 'retencaodecsrf', 'retencoescsrf', 'recolhercsrf'
                 'retencaocrf', 'retencaodecrf', 'retencoescsr', 'recolhercrf',
                 'retencaopcc', 'retencaodepcc', 'retencoespcc']

ALL_KEYWORDS = [IR_KEYWORDS, PIS_KEYWORDS, COFINS_KEYWORDS, CSLL_KEYWORDS, CSRF_KEYWORDS]
