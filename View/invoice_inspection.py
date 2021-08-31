import PySimpleGUI as sg
from Model.constants import MAX_INVOICES
import os


def main_gui() -> tuple:
    """Gera interface onde será informado o tipo do serviço (tomado, prestado) e a
       localização da pasta que contém os arquivos XML a serem conferidos."""

    sg.theme('default1')

    folder_name = str()
    xml_file_names = list()
    service_type = int()

    service_type_layout = [[sg.Radio('Prestado', 'radio1', default=False)],
                            [sg.Radio('Tomado', 'radio1', default=False)]]

    service_type_col = [[sg.Column(service_type_layout, size=(425, 70))]]

    layout = [
        [sg.Frame('Tipo de Serviço', service_type_col)],
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


def max_invoices_popup():
    sg.popup(f'Número limite de notas excedido. Separe os arquivos em subgupos de no máximo '
             f'{MAX_INVOICES} notas e tente novamente.')


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
            # complementa com os dados que estão na tabela e não são mostrados na tabela editável
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
    final_table = get_table_values(values, len(table), len(header))
    final_table = [set_row_types(header, row) for row in final_table]
    final_table = [final_table[i] + row[(len(header) + 1):] for i, row in enumerate(table)]
    return final_table


def service_details(table: list, header: list, row: list, row_index: int) -> list or None:
    """Mostra ao usuário detalhes referentes ao serviço que não aparecem em outras janelas."""

    input_size = (12, 1)
    input_padding = (2, 0)
    header_size = (10, 1)
    text_width = 101

    bg_color = '#bbbbbb'
    txt_color = 'black'

    # gera a lista de inputs para edição dos dados conferidos
    keys = ['invoice_n', 'date', 'gross_value', 'iss', 'ir', 'csrf', 'net_value', 'nature']
    inputs = [sg.Input(row[i], key=k, size=input_size, pad=input_padding, justification='center')
              for i, k in enumerate(keys)]

    table_header = [sg.Text(h, size=header_size, justification='center') for h in header]

    provider_name_layout = [[sg.Text(f'{row[8]}', size=(text_width, 1), text_color=txt_color)]]
    taker_name_layout = [[sg.Text(f'{row[9]}', size=(text_width, 1), text_color=txt_color)]]
    description_layout = [[sg.Text(row[10], size=(text_width, 7), text_color=txt_color)]]
    additional_data_layout = [[sg.Text(row[11], size=(text_width, 7), text_color=txt_color)]]

    provider_name_col = [[sg.Column(provider_name_layout)]]
    taker_name_col = [[sg.Column(taker_name_layout)]]
    description_col = [[sg.Column(description_layout)]]
    additional_data_col = [[sg.Column(additional_data_layout)]]

    inspection_data_layouts = [[[table_header[i]], [inputs[i]]] for i in range(len(inputs))]
    inspection_data_cols = [[sg.Column(inspection_data_layouts[i]) for i in range(len(inputs))]]

    layout = [
        [sg.Frame('Prestador', provider_name_col)],
        [sg.Frame('Tomador', taker_name_col)],
        [sg.Text()],

        [sg.Frame('Descrição do Serviço', description_col)],
        [sg.Frame('Dados Adicionais', additional_data_col)],
        [sg.Text()],

        [sg.Frame('Dados da Conferência', inspection_data_cols)],
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
        new_row = set_row_types(header, new_row)

        table = [row if i != row_index else new_row for i, row in enumerate(table)]
        window.close()

    return table


def update_table(window: sg.Window, header: list, table: list) -> sg.Window:
    """Cria nova tabela da GUI com os valores atualizados."""

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


def set_row_types(header: list, row: list) -> list:
    """Corrige o tipo dos valores da linha."""
    # natureza está na posição 7
    nature_pos = header.index('Natureza')
    float_values = list()

    for i in range(2, nature_pos):
        r = row[i]
        if r in ['-', '******']:
            float_values.append(r)
        elif not r:
            float_values.append('')
        else:
            float_values.append(float(r))

    if row[nature_pos].isnumeric():
        row = [int(row[0]), row[1]] + float_values + [int(row[nature_pos])] + row[(nature_pos + 1):]
    else:
        row = [int(row[0]), row[1]] + float_values + [row[nature_pos]] + row[(nature_pos + 1):]

    return row


def get_table_values(values: dict, n_rows: int, n_columns: int) -> list:
    """Retorna o uma lista com os valores contidos atualmente na tabela editável."""

    table = [[values[(j * n_columns) + i] for i in range(n_columns)] for j in range(n_rows)]
    return table
