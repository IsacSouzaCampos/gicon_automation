import PySimpleGUI as sg
import pyperclip


def insertion_commands(commands: list) -> None:
    text = ';\n\n'.join([command for command in commands]) + ';'
    # layout = [[sg.Multiline(text, size=(100, 30))]]
    layout = [
        [sg.Text('Comandos SQL copiados para a Área de Transferência.')],
        [sg.Button('Finalizar'), sg.Button('Copiar Novamente')]
    ]

    pyperclip.copy(text)

    window = sg.Window('Comandos Para o Lançamento', layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event is None or event == 'Finalizar':
            break

        if event == 'Copiar Novamente':
            pyperclip.copy(text)

    window.close()
