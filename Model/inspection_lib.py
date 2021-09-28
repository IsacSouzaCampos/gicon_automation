import os
from Model.constants import ALL_KEYWORDS


def separate_xml_files(folder, xml_files):
    import math
    from Model.constants import MAX_INVOICES

    n_xmls = len(xml_files)
    n_folders = int(math.ceil(n_xmls / MAX_INVOICES))
    for i in range(n_folders):
        new_folder = folder + '/' + folder.split("/")[-1] + '(' + str(i + 1) + ')'
        os.mkdir(new_folder)

        for j in range(MAX_INVOICES):
            # calcula posição atual do xml a ser movido na lista de xmls
            pos = (i * MAX_INVOICES) + j

            # se a posição calculada for igual ao tamanho da lista, finaliza varredura
            if pos == n_xmls:
                return
            xml_file = xml_files[pos]
            os.replace(folder + '/' + xml_file, new_folder + '/' + xml_file)


def clear_string(s: str) -> str:
    """
    Altera a string a ser analisada de maneira conveniente para a detecção de
    possíveis retenções

    :param s: String a ser filtrada.
    :type s:  (str)
    :return:  Resultado da string filtrada.
    :rtype:   (str)
    """
    s = s.lower()

    s = s.replace(' ', '')
    # s = s.replace('(', '')
    s = s.replace('=', '')
    s = s.replace('-', '')
    # s = s.replace(':', '')

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
        before = s[: s.find('leidatransparencia') + 1]
        after = s[s.find('leidatransparencia') + len('leidatransparencia'): len(s)]
        after = after[after.find('leidatransparencia') + len('leidatransparencia'): len(after)]
        s = before + after

    return s


def extract_tax_value(service_description, aditional_data, tax_type):
    """Encontra e extrai o valor do imposto federal solicitado"""

    # 0 = IR / 1 = PIS / 2 = COFINS / 3 = CSLL / 4 = CSRF
    keywords = ALL_KEYWORDS[tax_type]

    for text in [service_description, aditional_data]:
        clean_value = clear_string(text)
        for tax_kw in keywords:
            if tax_kw in clean_value:
                splitted_string = clean_value.split(tax_kw)

                for s in splitted_string[1:]:
                    # aux serve para que o algoritmo saiba quando o valor realmente começou a ser lido
                    aux = False
                    tax_value = str()

                    i = 0
                    while i < len(s):
                        c = s[i]
                        if (i + 1) >= len(s):
                            # não encontrou valor referente ao imposto em análise
                            if c.isnumeric():
                                tax_value += c
                            if not tax_value:
                                return -1
                            return convert_s_tax_value_to_float(tax_value)

                        next_c = s[i + 1]
                        if c.isnumeric() or c in [',', '.']:
                            tax_value += c

                            # reinicia a variável tax_value caso o valor extraído até aqui tenha
                            # sido o de porcentagem da cobrança
                            if next_c == '%':
                                tax_value = ''
                                aux = False
                                i += 1
                                continue

                            if not next_c.isnumeric() and next_c not in [',', '.'] and aux:
                                return convert_s_tax_value_to_float(tax_value)

                        if next_c.isnumeric() and not aux:
                            aux = True
                        i += 1
    return -1


def convert_s_tax_value_to_float(tax_value):
    """Converte a string tax_value extraída da nota para o formato float"""
    if not tax_value[-1].isnumeric():
        tax_value = tax_value[:-1]
    if not tax_value[0].isnumeric():
        tax_value = tax_value[1:]

    dot = tax_value.find('.')
    comma = tax_value.find(',')
    if dot > 0 and comma > 0:
        if dot < comma:
            return round(float(tax_value.replace('.', '').replace(',', '.')), 2)
    else:
        return round(float(tax_value.replace(',', '.')), 2)


def extract_tax_from_percentage(service_description, aditional_data, gross_value, tax_type):
    """Encontra e extrai o valor do imposto federal solicitado com base no seu percentual"""

    # 0 = IR / 1 = PIS / 2 = COFINS / 3 = CSLL / 4 = CSRF
    keywords = ALL_KEYWORDS[tax_type]

    for text in [service_description, aditional_data]:
        clean_value = clear_string(text)
        for tax_kw in keywords:
            if tax_kw in clean_value:
                splitted_string = clean_value.split(tax_kw)

                for s in splitted_string[1:]:
                    tax_value = str()

                    i = 0
                    s_len = len(s)
                    while i < s_len:
                        c = s[i]
                        if (i + 1) >= s_len and c != '%':
                            break

                        next_c = s[i + 1]
                        if c.isnumeric() or c in [',', '.']:
                            tax_value += c

                            # reinicia a variável tax_value caso o valor extraído até aqui tenha
                            # sido o de porcentagem da cobrança
                            if next_c == '%':
                                percentage = tax_value
                                percentage = convert_s_tax_value_to_float(percentage)
                                tax_value = round(float((percentage / 100) * gross_value), 2)

                                return tax_value

                        i += 1

    return -1
