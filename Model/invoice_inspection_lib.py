import os


def separate_xml_files(folder: str, xml_files: list) -> None:
    import math
    from Model.constants import MAX_INVOICES

    n_xmls = len(xml_files)
    n_folders = math.ceil(n_xmls / MAX_INVOICES)
    for i in range(n_folders):
        new_folder = f'{folder}/{folder.split("/")[-1]}({i + 1})'
        os.mkdir(new_folder)

        for j in range(MAX_INVOICES):
            # calcula posição atual do xml a ser movido na lista de xmls
            pos = (i * MAX_INVOICES) + j

            # se a posição calculada for igual ao tamanho da lista, finaliza varredura
            if pos == n_xmls:
                return
            xml_file = xml_files[pos]
            os.replace(f'{folder}/{xml_file}', f'{new_folder}/{xml_file}')
