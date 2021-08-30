import PySimpleGUI as sg
import os


def main_gui() -> tuple:
    """Gera interface onde será informado o tipo do serviço (tomado, prestado) e a
       localização da pasta que contém os arquivos XML a serem conferidos."""

    sg.theme('default1')

    folder_name = str()
    xml_file_names = list()
    service_type = int()

    layout = [
        [sg.Text('Tipo de serviço:')],
        [sg.Radio('Prestado', 'radio1', default=False)],
        [sg.Radio('Tomado', 'radio1', default=False)],
        [sg.Text('Selecione a pasta que contém as notas a serem conferidas:')],
        [sg.Input(), sg.FolderBrowse('Selecionar Pasta')],
        [sg.Submit('Conferir'), sg.Cancel('Cancelar')],
    ]

    window = sg.Window('Conferência Automatizada', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancelar':
            exit()

        if event == 'Conferir':
            if not values['Selecionar Pasta']:
                sg.popup('Selecione uma pasta para a conferência!')
                continue
            if values[0]:
                service_type = 0
                folder_name = values['Selecionar Pasta'] or '.'
                xml_file_names = [file for file in os.listdir(folder_name) if '.xml' in file]
                break
            elif values[1]:
                # se a pasta não foi selecionada use a pasta atual `.`
                service_type = 1
                folder_name = values['Selecionar Pasta'] or '.'
                xml_file_names = [file for file in os.listdir(folder_name) if '.xml' in file]
                break
            else:
                sg.popup('Selecione o tipo de conferência a ser feita!')

    window.close()
    return folder_name, xml_file_names, service_type


def start_inspection_loading_window() -> sg.Window:
    """Inicializa a janela que mostrará o progresso da conferência"""

    layout = [
        [sg.Text(key='text')],
        [sg.ProgressBar(1, orientation='horizontal', size=(40, 20), key='progress')]
    ]

    window = sg.Window('Conferindo Notas', layout, disable_close=True, finalize=True)

    return window


def update_loading_window(window: sg.Window, invoice_number: str, progress: int, total_size: int) -> None:
    """Atualiza a barra de progresso da conferência"""

    window.Element('text').Update(f'Nota: {invoice_number}')
    window.Element('progress').UpdateBar(progress, total_size)


def editable_table(table: list) -> list or None:
    """Cria tabela de resultados editável."""
    header = ['Nº nota', 'Emissão', 'Valor Bruto', 'ISS', 'IR', 'CSRF', 'Valor Líquido', 'Natureza']
    table_header = [sg.Text(header[0], pad=(35, 0)), sg.Text(header[1], pad=(25, 0)),
                    sg.Text(header[2], pad=(25, 0)), sg.Text(header[3], pad=(35, 0)),
                    sg.Text(header[4], pad=(52, 0)), sg.Text(header[5], pad=(30, 0)),
                    sg.Text(header[6], pad=(20, 0)), sg.Text(header[7], pad=(20, 0))]

    input_rows = [[sg.Input(v, size=(15, 1), pad=(0, 0), justification='center') for i, v in enumerate(row[:8])] +
                  [sg.Button('...', pad=(0, 0), key=f'detail_{i}')] for i, row in enumerate(table)]

    frame = [
        table_header,
        [sg.Column(input_rows, size=(900, 200), scrollable=True, key='-COL-')]
    ]

    layout = [
        [sg.Frame('Tabela de Resultados', frame, key='-FRAME-')],
        [sg.Text()],
        [sg.Button('Lançar', size=(10, 1))]
    ]

    window = sg.Window('Tabela de Edição', layout, finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if 'detail_' in event:
            table_n_columns = len(header)
            index = int(event.split('_')[1])
            start = index * table_n_columns
            end = start + table_n_columns

            row = [values[i] for i in range(start, end)]
            row = row + table[index][(end - start):]

            new_table = service_details(table, header, row, index)
            if new_table:
                table = new_table
                window = update_table(window, header, table)

        if event == 'Lançar':
            if sg.popup_yes_no('Deseja realmente lançar os dados no sistema?') == 'Yes':
                # *** atuaizar a tabela com os valores contidos atualmente na tela ***
                break

    window.close()
    return [row[:8] for row in table]


def service_details(table: list, header: list, row: list, row_index: int) -> list or None:
    """Mostra ao usuário detalhes referentes ao serviço que não aparecem em outras janelas."""

    input_size = (10, 1)
    input_padding = ((5, 20), (0, 0))
    header_size = (11, 1)
    text_width = 107

    bg_color = '#bbbbbb'
    txt_color = 'black'

    # gera a lista de inputs para edição dos dados conferidos
    keys = ['invoice_n', 'date', 'gross_value', 'iss', 'ir', 'csrf', 'net_value', 'nature']
    inputs = [sg.Input(row[i], key=k, size=input_size, pad=input_padding) for i, k in enumerate(keys)]

    table_header = [sg.Text(h, size=header_size) for h in header]

    layout = [
        [sg.Text('Prestador:')],
        [sg.Text(f'{row[8]}', size=(text_width, 1), background_color=bg_color, text_color=txt_color)],
        [sg.Text('Tomador:')],
        [sg.Text(f'{row[9]}', size=(text_width, 1), background_color=bg_color, text_color=txt_color)],
        [sg.Text()],

        [sg.Text('Descrição do Serviço:')],
        [sg.Text(row[10], size=(text_width, 10), background_color=bg_color, text_color=txt_color)],
        [sg.Text()],

        table_header,
        inputs,
        [sg.Text()],

        [sg.OK(key='ok_button', size=(12, 1))]
    ]

    window = sg.Window(f'Natureza da Nota: {row[0]}', layout)
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        return

    if event == 'ok_button':
        # se mantém em loop enquanto o número de dígitos da natureza não for 7
        while len(values['nature']) != 7:
            sg.popup('A natureza digitada não está de acordo com o padrão (7 dígitos)')
            event, values = window.read()

            if event == sg.WINDOW_CLOSED:
                return

            if event == 'ok_button':
                break

        new_row = [values[key] for key in values] + row[len(values):]

        # atualizar linha com os formatos corretos dos valores
        # gross_value, iss, ir, csrf, net_value
        float_values = [float(new_row[i]) if new_row[i] else '' for i in range(2, 7)]

        new_row = [int(new_row[0]), new_row[1]] + float_values + [int(new_row[7])] + new_row[8:]

        # natureza está na posição 7
        table = [row if i != row_index else new_row for i, row in enumerate(table)]
        window.close()

    return table


def update_table(window: sg.Window, header: list, table: list) -> sg.Window:
    """Atualiza a tabela da GUI e a tabela final a ser usada para lançamento no banco de dados."""

    # Por enquanto a tela de edição está sendo recriada ao invés de apenas atualizados os valores
    # modificados. O ideal é corrigir isso assim que a solução for encontrada.

    table_header = [sg.Text(header[0], pad=(35, 0)), sg.Text(header[1], pad=(25, 0)),
                    sg.Text(header[2], pad=(25, 0)), sg.Text(header[3], pad=(35, 0)),
                    sg.Text(header[4], pad=(52, 0)), sg.Text(header[5], pad=(30, 0)),
                    sg.Text(header[6], pad=(20, 0)), sg.Text(header[7], pad=(20, 0))]

    input_rows = [[sg.Input(v, size=(15, 1), pad=(0, 0), justification='center') for i, v in enumerate(row[:8])] +
                  [sg.Button('...', pad=(0, 0), key=f'detail_{i}')] for i, row in enumerate(table)]

    frame = [
        table_header,
        [sg.Column(input_rows, size=(900, 200), scrollable=True, key='-COL-')]
    ]

    layout = [
        [sg.Frame('Tabela de Resultados', frame, key='-FRAME-')],
        [sg.Text()],
        [sg.Button('Lançar', size=(10, 1))]
    ]

    # window.Element('-FRAME-').Update('Tabela de Resultados *', frame)
    window.close()

    window = sg.Window('Tabela de Edição', layout)
    return window
