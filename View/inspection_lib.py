import PySimpleGUI as sg
from Model.constants import SYS_PATH
# import pyperclip


def insertion_commands(commands: list) -> None:
    # transforma a matriz commands em uma lista
    commands_list = list()
    for cmds in commands:
        for cmd in cmds:
            commands_list.append(cmd)

    text = ';\n\n'.join([command for command in commands_list]) + ';'
    layout = [[sg.Multiline(text, size=(100, 30))]]
    # layout = [
    #     [sg.Text('Comandos SQL copiados para a Área de Transferência.')],
    #     [sg.Button('Finalizar'), sg.Button('Copiar Novamente')]
    # ]
    #
    # pyperclip.copy(text)

    window = sg.Window('Comandos Para o Lançamento', layout, finalize=True)
    window.read()

    # while True:
    #     event, values = window.read()
    #     if event == sg.WINDOW_CLOSED or event is None or event == 'Finalizar':
    #         break
    #
    #     if event == 'Copiar Novamente':
    #         pyperclip.copy(text)

    window.close()


def create_delete_commands(min_launch_key, min_withheld_key):
    commands = f'DELETE FROM LCTOFISSAI WHERE CODIGOEMPRESA = 641 AND CHAVELCTOFISSAI >= {min_launch_key};\n' \
              f'DELETE FROM LCTOFISSAICFOP WHERE CODIGOEMPRESA = 641 AND CHAVELCTOFISSAI >= {min_launch_key};\n' \
              f'DELETE FROM LCTOFISSAIRETIDO WHERE CODIGOEMPRESA = 641 AND CHAVELCTOFISSAI >= {min_withheld_key};\n' \
              f'DELETE FROM LCTOFISSAIVALORISS WHERE CODIGOEMPRESA = 641 AND CHAVELCTOFISSAI >= {min_launch_key};'

    with open(SYS_PATH + r'\delete_commands.txt', 'w') as fout:
        print(commands, file=fout)
