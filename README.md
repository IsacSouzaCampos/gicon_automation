# gicon_automation

links para pesquisas relacionadas:

1. https://www.ti-enxame.com/pt/python/como-extrair-tabela-como-texto-do-pdf-usando-python/835326779/?fbclid=IwAR16EuGKsxhSKGoExGjYDAuDoIMtGdkAXH2ZZa8d7ysHf2cdKrd8vIoRLAw
2. https://focusnfe.com.br/exemplo-de-codigo-python/?fbclid=IwAR0x9nbOUrYKa4i_6WSFadZU8iDBoBeZZaHqWb5QVPkC8Y7thEbV1wzX3ow
3. https://github.com/webmaniabr/NFe-Python?fbclid=IwAR3MM45us6BK8va4ALPzBaUyMYvPMFhiZAWClf2d-4cJ6Xpzi31_Y57-v9Y
4. https://pt.stackoverflow.com/questions/363079/iterar-por-v%c3%a1rios-arquivos-xmls-com-python?fbclid=IwAR2ZNbhThhDdJ8R7JE09saFZCo7Gfy2duplsi5euXRUttJgb9_OyPclsLLI
5. https://www.techtudo.com.br/dicas-e-tutoriais/noticia/2015/09/como-converter-uma-nota-em-xml-para-pdf.html?fbclid=IwAR0x9nbOUrYKa4i_6WSFadZU8iDBoBeZZaHqWb5QVPkC8Y7thEbV1wzX3ow
6. http://sped.rfb.gov.br/pasta/show/1888?fbclid=IwAR16EuGKsxhSKGoExGjYDAuDoIMtGdkAXH2ZZa8d7ysHf2cdKrd8vIoRLAw
7. http://sped.rfb.gov.br/pasta/show/1846?fbclid=IwAR0x9nbOUrYKa4i_6WSFadZU8iDBoBeZZaHqWb5QVPkC8Y7thEbV1wzX3ow
8. https://raccoon.ninja/pt/dev-pt/manipulando-xml-com-python/?fbclid=IwAR12gLMWZGGwdlA6O_ZZ8NzFfuAdQ5RRTkC058OEIOkdyIdSzAs9rHHF3tk
9. http://www.pmf.sc.gov.br/sistemas/suporte/nfpssuporte/codigos.php
10. https://docs.questor.com.br/docs/fiscal/importar-nfse
11. https://pt.stackoverflow.com/questions/478761/attributeerror-nonetype-object-has-no-attribute-text
12. https://www.letscode.com.br/blog/aprenda-a-integrar-python-e-excel

*******************************************************************************************************

Para baixar módulos:

https://pt.stackoverflow.com/questions/239047/como-instalar-o-pip-no-windows-10

*******************************************************************************************************

ML para padrões de texto (em último caso):

https://serokell.io/blog/machine-learning-text-analysis

*******************************************************************************************************

Para criar um .txt com os módulos necessários para a execução do código:

instalar pipreqs na máquina:
	Windows: "python -m pip install pipreqs"
	Linux: "pip(3) install pipreqs"
rodar pipreqs dentro da pasta do projeto:
	"pipreqs ./"

*******************************************************************************************************

Conectar código com servidor SQL:

https://datatofish.com/how-to-connect-python-to-sql-server-using-pyodbc/
https://www.w3schools.com/python/python_mysql_getstarted.asp
https://stackoverflow.com/questions/16088151/how-to-find-server-name-of-sql-server-management-studio
https://docs.microsoft.com/pt-br/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver15

*******************************************************************************************************

Comando de pesquisa no Banco de Dados (X:\QUESTOR\Relatórios Personalizados\Layouts\F100 EFD Contribuições Lucro Presumido\Competencia):

select CODIGOEMPRESA, CODIGOESTAB, DATASALDO, VALORCRED, CONTACTB  
from  SALDOCTB where CODIGOEMPRESA in (73) and DATASALDO between '01.06.2021' and '30.06.2021' and CONTACTB in ('2859', '2858', '2860', '2862', '2893', '4999', '5248', '4872', '4904')

*******************************************************************************************************

Criar arquivo executável:

https://pypi.org/project/pyinstaller/
https://pyinstaller.readthedocs.io/en/v4.5.1/
