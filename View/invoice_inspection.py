import PySimpleGUI as sg
import os


def main_gui() -> tuple:
    """Gera interface onde será informado o tipo do serviço (tomado, prestado) e a
       localização da pasta que contém os arquivos XML a serem conferidos."""

    folder_name = str()
    xml_file_names = list()

    layout = [
        [sg.Text('Tipo de serviço:')],
        [sg.Radio('Prestado', 'radio1', default=False)],
        [sg.Radio('Tomado', 'radio1', default=False)],
        [sg.Text('Selecione a pasta que contém as notas a serem conferidas:')],
        [sg.Input(), sg.FolderBrowse('Selecionar Pasta')],
        [sg.Submit('Conferir'), sg.Cancel('Cancelar')],
    ]

    window = sg.Window('Test', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancelar':
            break

        if event == 'Conferir':
            print(values)
            if values[0]:
                print('Conferência ainda não desenvolvida')
                break
            elif values[1]:
                # if folder was not selected then use current folder `.`
                folder_name = values['Selecionar Pasta'] or '.'
                xml_file_names = [file for file in os.listdir(folder_name) if '.xml' in file]
                break

    window.close()
    return folder_name, xml_file_names


def start_loading_inspection_window() -> sg.Window:
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


def show_results_table(header: list, table: list) -> None:
    layout = [
        [sg.Table(values=table, headings=header)]
    ]

    window = sg.Window('Resultados da Conferência', layout)
    window.read()
    window.close()
