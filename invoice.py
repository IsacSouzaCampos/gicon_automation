import xml.etree.ElementTree as ET
from constants import *


class Invoice():

    def __init__(self, file: str):
        self.file = file
        self.file_path = f'{XML_DIR}\\{file}'

        self.number = int(self.file.split('-')[-1].replace('.xml', ''))
        self.d = self.get_xml_tags_dict()
    

    def excel_data_list(self) -> list:
        """Gera a linha com os dados de retencao referentes a nota contida no arquivo 
        invoice_file."""

        row = [self.number]
        row.append(self.get_taker_business_name())
        row.append(self.get_provider_business_name())
        row.append('X' if self.iss_withheld() else '-')

        # 0 = IR / 1 = CSRF
        row.append('X' if self.is_fed_tax_withheld(0) else '-')
        row.append('X' if self.is_fed_tax_withheld(1) else '-')

        return row


    def iss_withheld(self) -> bool:
        """Verifica se ha retencao de ISS com base no CFPS e CST"""

        iss_withheld = False
        try:
            if self.d['nomeMunicipioPrestador'] == 'FLORIANOPOLIS':
                if self.d['cst'] in ['2', '4', '6', '10']:
                    iss_withheld = True

            elif self.d['cfps'] in ['9205', '9206'] and self.d['cst'] in ['0', '1']:
                    iss_withheld = True

        except Exception as e:
            print(f'Erro: {e} - Arquivo: {self.file_path}')


        return iss_withheld
    

    def is_fed_tax_withheld(self, tax_type: int) -> bool:
        """Verifica se ha retencao de imposto federal com base em palavras chave"""

        if tax_type not in [0, 1]:  # 0 = IR / 1 = CSRF
            raise Exception('Imposto não reconhecido')

        KEYWORDS = POSSIBLE_IR_NOTES if tax_type == 0 else POSSIBLE_CSRF_NOTES

        if 'descricaoServico' in self.d and self.d['descricaoServico'] is not None:
            descricao_servico = self.d['descricaoServico']

            # procurar indicios de retencao do tax_type na descricao de servico
            clean_descricao_servico = self.clear_string(descricao_servico)
            # if tax_type == 1 and self.number in [44319, 9014, 419]:
            #     print(str(self.number) + '\n' + clean_descricao_servico + '\n\n')
            for ir_note in KEYWORDS:
                if ir_note.lower() in clean_descricao_servico or ('retencao' + ir_note) in clean_descricao_servico:
                    return True
        
        if 'dadosAdicionais' in self.d and self.d['dadosAdicionais'] is not None:
            dados_adicionais = self.d['dadosAdicionais']

            # procurar indicios de retencao do tax_type nos dados adicionais
            clean_dados_adicionais = self.clear_string(dados_adicionais)
            # if tax_type == 1 and self.number in [44319, 9014, 419]:
            #     print(str(self.number) + '\n' + clean_dados_adicionais + '\n\n')
            for ir_note in KEYWORDS:
                if ir_note.lower() in clean_dados_adicionais or ('retencao' + ir_note) in clean_dados_adicionais:
                    return True
        
        return False
    

    def clear_string(self, s: str) -> str:
        """Altera a string a ser analisada de maneira conveniente para a deteccao de 
        possiveis retencoes"""
        s = s.lower()

        s = s.replace(' ', '')
        s = s.replace('(', '')
        s = s.replace('=', '')
        s = s.replace('-', '')
        s = s.replace(':', '')
        s = s.replace('/', '')
        s = s.replace('\\', '')
        
        s = s.replace('ç', 'c')
        
        s = s.replace('ã', 'a')
        s = s.replace('õ', 'o')
        
        s = s.replace('á', 'a')
        s = s.replace('é', 'e')
        s = s.replace('í', 'i')
        s = s.replace('ó', 'o')
        s = s.replace('ú', 'u')

        s = s.replace('â', 'a')
        s = s.replace('ê', 'e')
        s = s.replace('ó', 'o')

        if s.count('leidatransparencia') > 1:
            before = s[0 : s.find('leidatransparencia')]
            after = s[s.find('leidatransparencia') + len('leidatransparencia') : len(s)]
            after = after[after.find('leidatransparencia') + len('leidatransparencia') : len(after)]
            s = before + after

        return s
    

    def get_xml_tags_dict(self) -> dict:
        """Retorna o dicionario referente as tags do xml e seus valores associados"""
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        d = dict()
        for child in root.iter():
            d[child.tag] = child.text
        
        return d
    

    def get_taker_business_name(self) -> str:
        """Retorna a razao social do tomador do servico"""
        return self.d['razaoSocialTomador']
    

    def get_provider_business_name(self) -> str:
        """Retorna a razao social do prestador do servico"""
        return self.d['razaoSocialPrestador']
