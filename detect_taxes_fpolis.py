import xml.etree.ElementTree as ET
from constants import XML_DIR


class DetectTaxes():

    def __init__(self, file: str):
        self.file_path = f'{XML_DIR}\\{file}'


    def iss_withheld(self) -> bool:
        """Verifica se ha retencao de ISS com base no CFPS e CST"""

        tree = ET.parse(self.file_path)
        root = tree.getroot()

        d = dict()
        for child in root.iter():
            d[child.tag] = child.text

        iss_withheld = False
        try:
            if d['nomeMunicipioPrestador'] == 'FLORIANOPOLIS':
                if d['cst'] in ['4', '6', '10']:
                    iss_withheld = True

            elif d['cfps'] in ['9205', '9206'] and d['cst'] in ['0', '1']:
                    iss_withheld = True

            # print(d['dadosAdicionais'])

        except Exception as e:
            print(f'Erro: {e} - Arquivo: {self.file_path}')


        return iss_withheld
