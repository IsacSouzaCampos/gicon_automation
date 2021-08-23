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
            print(values)
            if values[0]:
                print('Conferência ainda não desenvolvida')
                service_type = 0
                break
            elif values[1]:
                # if folder was not selected then use current folder `.`
                service_type = 1
                folder_name = values['Selecionar Pasta'] or '.'
                xml_file_names = [file for file in os.listdir(folder_name) if '.xml' in file]
                break

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


def show_results_table(header: list, table: list) -> list or None:
    """Mostra tela com os resultados da conferência automatizada, possibilitando edição dos resultados
       antes de lançá-los no banco de dados."""
    new_table = list()

    layout = [
        [sg.Table(values=table, headings=header, key='table')],

        [sg.Button('Editar'), sg.Button('Atualizar')],

        # [sg.Text('Nº Nota', size=(10, 1)), sg.Text('Data', size=(11, 1)),
        #  sg.Text('Valor Bruto', size=(11, 1)), sg.Text('Retenção ISS', size=(11, 1)),
        #  sg.Text('Retenção IR', size=(11, 1)), sg.Text('Retenção CSRF', size=(11, 1)),
        #  sg.Text('Valor Líquido', size=(11, 1)), sg.Text('Natureza', size=(11, 1))],

        [sg.Input(key='invoice_n', size=(12, 20)), sg.Input(key='date', size=(12, 20)),
         sg.Input(key='gross_value', size=(12, 20)), sg.Input(key='iss', size=(12, 20)),
         sg.Input(key='ir', size=(12, 20)), sg.Input(key='csrf', size=(12, 20)),
         sg.Input(key='net_value', size=(12, 20)), sg.Input(key='nature', size=(12, 20))],

        [sg.Text()],
        [sg.Button('Lançar')]
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
                edit_row(window, table[selected_row])
            except Exception as e:
                print(e)

        if event == 'Lançar':
            if sg.popup_yes_no('Deseja realmente lançar os dados no sistema?') == 'Yes':
                window.close()
                return new_table if new_table else table

        if event == 'Atualizar':
            row = [values['invoice_n'], values['date'],
                   values['gross_value'], values['iss'],
                   values['ir'], values['csrf'],
                   values['net_value'], values['nature']]

            new_table = update_table(window, table, selected_row, row)


def edit_row(window: sg.Window, row: list) -> None:
    """Atualiza os valores das caixas de texto que permitirão a modificação dos dados da tabela."""
    window.Element('invoice_n').Update(row[0])
    window.Element('date').Update(row[1])
    window.Element('gross_value').Update(row[2])
    window.Element('iss').Update(row[3])
    window.Element('ir').Update(row[4])
    window.Element('csrf').Update(row[5])
    window.Element('net_value').Update(row[6])
    window.Element('nature').Update(row[7])


def update_table(window: sg.Window, table: list, selected_row: int, row: list) -> list:
    """Atualiza a tabela da GUI e a tabela final a ser usada para lançamento no banco de dados."""
    # atualizar linha com os formatos corretos dos valores
    float_values = [float(row[i]) if row[i] else '' for i in range(2, 7)]  # gross_value, iss, ir, csrf, net_value

    row = [int(row[0]), row[1]] + float_values + [int(row[7])]

    table = [table[i] if i != selected_row else row for i in range(len(table))]
    window.Element('table').Update(values=table)
    return table
