import PySimpleGUI as sg
import os


def main_gui() -> tuple:
    """Gera interface onde será informado o tipo do serviço (tomado, prestado) e a
       localização da pasta que contém os arquivos XML a serem conferidos."""

    # sg.theme('GrayGrayGray')

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
            break

        if event == 'Conferir':
            if not values['Selecionar Pasta']:
                sg.popup('Selecione uma pasta para a conferência!')
                continue
            if values[0]:
                print('Conferência ainda não desenvolvida')
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

    window = sg.Window('Conferindo Notas', layout).Finalize()

    return window


def update_loading_window(window: sg.Window, invoice_number: str, progress: int, total_size: int) -> None:
    """Atualiza a barra de progresso da conferência"""

    window.Element('text').Update(f'Nota: {invoice_number}')
    window.Element('progress').UpdateBar(progress, total_size)


def provided_service_editing_screen(header: list, table: list) -> list or None:
    """Mostra tela com os resultados da conferência de notas de serviço prestado automatizada,
       possibilitando edição dos resultados antes de lançá-los no banco de dados."""

    new_table = list()

    layout = [
        [sg.Table(values=table, headings=header[:-1], key='table')],

        [sg.Button('Editar', size=(12, 1)), sg.Button('Atualizar', size=(12, 1))],

        [sg.Input(key='invoice_n', size=(12, 20)), sg.Input(key='date', size=(12, 20)),
         sg.Input(key='gross_value', size=(12, 20)), sg.Input(key='iss', size=(12, 20)),
         sg.Input(key='ir', size=(12, 20)), sg.Input(key='csrf', size=(12, 20)),
         sg.Input(key='net_value', size=(12, 20))],

        [sg.Text()],
        [sg.Button('Inserir Natureza(s)')]
    ]

    window = sg.Window('Resultados da Conferência', layout)

    selected_row = -1
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            window.close()
            return

        if event == 'Editar':
            try:
                selected_row = values['table'][0]
                edit_row(window, table[selected_row], 0)  # 0: serviço prestado
            except Exception as e:
                print(e)

        if event == 'Atualizar':
            # transforma os valores obtidos dos Inputs em lista
            row = [values[key] for key in values]
            # adiciona o resto da linha da tabela à linha que será adicionada para atualização
            row = row[1:] + table[selected_row][len(row) - 1:]
            if new_table:
                new_table = update_table(window, new_table, selected_row, row, 0)  # 0: serviço prestado
            else:
                new_table = update_table(window, table, selected_row, row, 0)  # 0: serviço prestado

        if event == 'Inserir Natureza(s)':
            new_table = insert_service_nature(new_table) if new_table else insert_service_nature(table)
            window.close()
            return provided_service_editing_final_screen(header, new_table)


def provided_service_editing_final_screen(header: list, table: list) -> list or None:
    """Tela final de confirmação dos dados antes do lançamento para conferência de notas de serviço tomado"""
    layout = [
        [sg.Table(headings=header, values=table, key='table')],
        [sg.Text()],
        [sg.Button('Lançar', size=(12, 1)),  sg.Button('Editar', size=(12, 1))],
        [sg.Button('Cancelar', size=(12, 1))]
    ]

    window = sg.Window('Lançar notas', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancelar':
            return

        if event == 'Editar':
            window.close()
            return provided_service_reediting_screen(header, table)

        if event == 'Lançar':
            if sg.popup_yes_no('Deseja realmente lançar os dados no sistema?') == 'Yes':
                break

    window.close()
    return table


def provided_service_reediting_screen(header: list, table: list) -> list:
    """Tela de reedição das notas de serviço prestado. Igual à tela de edição dos serviços tomados."""
    return taken_service_edition_screen(header, table)


def insert_service_nature(table: list) -> list or None:
    """Mostra cada um dos serviços para que o usuário informe a natureza destes."""
    import time
    new_table = list()

    for row in table:
        layout = [
            [sg.Text(f'Prestador: {row[8]}')],
            [sg.Text(f'Tomador: {row[9]}')],
            [sg.Text()],

            [sg.Text('Descrição do Serviço:')],
            [sg.Text(row[10])],
            [sg.Text()],

            [sg.Text('Nº Nota', size=(12, 1)), sg.Text('Data Emissão', size=(12, 1)),
             sg.Text('Valor Bruto', size=(12, 1)), sg.Text('Valor ISS', size=(12, 1)),
             sg.Text('Valor IR', size=(12, 1)), sg.Text('Valor CSRF', size=(12, 1)),
             sg.Text('Valor Líquido', size=(12, 1)), sg.Text('Natureza', size=(12, 1))],

            [sg.Text(row[0], key='invoice_n', size=(12, 1)), sg.Text(row[1], key='date', size=(12, 1)),
             sg.Text(row[2], key='gross_value', size=(12, 1)), sg.Text(row[3], key='iss', size=(12, 1)),
             sg.Text(row[4], key='ir', size=(12, 1)), sg.Text(row[5], key='csrf', size=(12, 1)),
             sg.Text(row[6], key='net_value', size=(12, 1)), sg.Input(row[7], key='nature', size=(12, 1))],
            [sg.Text()],

            [sg.OK(key='ok_button', size=(12, 1))]
        ]

        window = sg.Window(f'Natureza da Nota: {row[0]}', layout)
        event, values = window.read()

        window.Element('invoice_n').Update(row[0])
        window.Element('date').Update(row[1])
        window.Element('gross_value').Update(row[2])
        window.Element('iss').Update(row[3])
        window.Element('ir').Update(row[4])
        window.Element('csrf').Update(row[5])
        window.Element('net_value').Update(row[6])
        window.Element('nature').Update(row[7])
        window.Element('nature').Update(move_cursor_to='end')  # não está tendo efeito

        if event == sg.WINDOW_CLOSED:
            return

        if event == 'ok_button':
            nature = values['nature']

            # se mantém em loop enquanto o número de dígitos da natureza não for 7
            while len(nature) != 7:
                sg.popup('A natureza digitada não está de acordo com o padrão (7 dígitos)')
                event, values = window.read()

                if event == sg.WINDOW_CLOSED:
                    return

                if event == 'ok_button':
                    nature = values['nature']

            # natureza está na posição 7
            new_table.append(row[:7] + [int(nature)])
            window.close()

        time.sleep(.1)

    return new_table


def taken_service_edition_screen(header: list, table: list) -> list or None:
    """Mostra tela com os resultados da conferência de ntoas de serviço tomado automatizada,
       possibilitando edição dos resultados antes de lançá-los no banco de dados."""
    new_table = list()

    layout = [
        [sg.Table(values=table, headings=header, key='table')],

        [sg.Button('Editar', size=(12, 1)), sg.Button('Atualizar', size=(12, 1))],

        [sg.Input(key='invoice_n', size=(12, 20)), sg.Input(key='date', size=(12, 20)),
         sg.Input(key='gross_value', size=(12, 20)), sg.Input(key='iss', size=(12, 20)),
         sg.Input(key='ir', size=(12, 20)), sg.Input(key='csrf', size=(12, 20)),
         sg.Input(key='net_value', size=(12, 20)), sg.Input(key='nature', size=(12, 20))],

        [sg.Text()],
        [sg.Button('Lançar', size=(12, 1))]
    ]

    window = sg.Window('Resultados da Conferência', layout)

    selected_row = -1
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            window.close()
            return

        if event == 'Editar':
            try:
                selected_row = values['table'][0]
                edit_row(window, table[selected_row], 1)  # 1: serviço tomado
            except Exception as e:
                print(e)

        if event == 'Atualizar':
            row = [values['invoice_n'], values['date'],
                   values['gross_value'], values['iss'],
                   values['ir'], values['csrf'],
                   values['net_value'], values['nature']]

            if new_table:
                new_table = update_table(window, new_table, selected_row, row, 1)  # 1: serviço tomado
            else:
                new_table = update_table(window, table, selected_row, row, 1)  # 1: serviço tomado

        if event == 'Lançar':
            if sg.popup_yes_no('Deseja realmente lançar os dados no sistema?') == 'Yes':
                window.close()
                return new_table if new_table else table


def edit_row(window: sg.Window, row: list, service_type: int) -> None:
    """Atualiza os valores das caixas de texto que permitirão a modificação dos dados da tabela."""
    window.Element('invoice_n').Update(row[0])
    window.Element('date').Update(row[1])
    window.Element('gross_value').Update(row[2])
    window.Element('iss').Update(row[3])
    window.Element('ir').Update(row[4])
    window.Element('csrf').Update(row[5])
    window.Element('net_value').Update(row[6])

    if service_type:
        window.Element('nature').Update(row[7])


def update_table(window: sg.Window, table: list, selected_row: int, row: list, service_type: int) -> list:
    """Atualiza a tabela da GUI e a tabela final a ser usada para lançamento no banco de dados."""
    # atualizar linha com os formatos corretos dos valores
    float_values = [float(row[i]) if row[i] else '' for i in range(2, 7)]  # gross_value, iss, ir, csrf, net_value

    if service_type:
        row = [int(row[0]), row[1]] + float_values + [int(row[7])]
    else:
        row = [int(row[0]), row[1]] + float_values + [int(row[7])] + row[8:]

    table = [table[i] if i != selected_row else row for i in range(len(table))]
    window.Element('table').Update(values=table)
    return table
