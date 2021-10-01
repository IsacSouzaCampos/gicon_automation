import PySimpleGUI as sg


def insertion_commands(commands: list) -> None:
    text = ';\n\n'.join([command for command in commands]) + ';'
    layout = [[sg.Multiline(text, size=(100, 30))]]

    window = sg.Window('Comandos Para o Lançamento', layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event is None:
            break

    window.close()
