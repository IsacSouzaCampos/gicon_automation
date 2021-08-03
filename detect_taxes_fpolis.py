import xml.etree.ElementTree as ET
import constants as const


file = f'{const.ROOT_DIR}\\notas_xml\\nota_0164219-31.xml'

tree = ET.parse(file)
root = tree.getroot()

d = dict()
for child in root.iter():
    d[child.tag] = child.text

iss_retido = False
try:
    if d['nomeMunicipioPrestador'] == 'FLORIANOPOLIS':
        if d['cst'] in ['4', '6', '10']:
            iss_retido = True

    elif d['cfps'] in ['9205', '9206'] and d['cst'] in ['0', '1']:
            iss_retido = True

    print(d['dadosAdicionais'])

except Exception as e:
    print(f'Erro: {e} - Arquivo: {file}')


if iss_retido:
    print('ISS retido')
else:
    print('Sem retenção de ISS')
