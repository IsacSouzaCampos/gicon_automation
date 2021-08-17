import PySimpleGUI as sg
import os

# help(sg.FolderBrowse)
# help(sg.FileBrowse)


def main_gui() -> tuple:
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
