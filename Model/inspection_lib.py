import os
# from Model.constants import ALL_KEYWORDS


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

    law_terms = ['leidatransparencia', 'lei12.741/2012']
    for law_term in law_terms:
        if s.count(law_term) > 0:
            before = s[: s.find(law_term) + 1]
            after = s[s.find(law_term) + len(law_term): len(s)]
            after = after[after.find(law_term) + len(law_term): len(after)]
            s = before + after

    return s
