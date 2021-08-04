import xml.etree.ElementTree as ET
from constants import *


class Invoice():

    def __init__(self, file: str):
        self.file = file
        self.file_path = f'{XML_DIR}\\{file}'
        
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        self.d = dict()
        for child in root.iter():
            self.d[child.tag] = child.text


    def iss_withheld(self) -> bool:
        """Verifica se ha retencao de ISS com base no CFPS e CST"""

        iss_withheld = False
        try:
            if self.d['nomeMunicipioPrestador'] == 'FLORIANOPOLIS':
                if self.d['cst'] in ['4', '6', '10']:
                    iss_withheld = True

            elif self.d['cfps'] in ['9205', '9206'] and self.d['cst'] in ['0', '1']:
                    iss_withheld = True

        except Exception as e:
            print(f'Erro: {e} - Arquivo: {self.file_path}')


        return iss_withheld
    

    def is_ir_withheld(self) -> bool:        
        if 'descricaoServico' in self.d and self.d['descricaoServico'] is not None:
            descricao_servico = self.d['descricaoServico']

            # procurar indicios de retencao de impostos federais na descricao de servico
            descricao_servico_without_whitespaces = descricao_servico.replace(' ', '')
            for ir_note in POSSIBLE_IR_NOTES:
                if ir_note in descricao_servico_without_whitespaces:
                    return True
        
        if 'dadosAdicionais' in self.d and self.d['dadosAdicionais'] is not None:
            dados_adicionais = self.d['dadosAdicionais']

            # procurar indicios de retencao de impostos federais nos dados adicionais
            dados_adicionais_without_whitespaces = dados_adicionais.replace(' ', '')
            for ir_note in POSSIBLE_IR_NOTES:
                if ir_note in dados_adicionais_without_whitespaces:
                    return True
        
        return False
