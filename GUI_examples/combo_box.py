import PySimpleGUI as sg


if __name__ == '__main__':
    options_list = [f'Empresa {i + 1}' for i in range(5)]
    layout = [
        [sg.Combo(options_list, default_value='Empresa 2', size=(25, 1), key='-COMBO-')],
        [sg.B('Imprimir')],
        [sg.T(key='-TEXT-')],
        [sg.T()],
        [sg.B('Sair')]
    ]

    window = sg.Window('Combo Box Example', layout)

    while True:
        event, values = window.read()
        print(event, values)

        if event == 'Sair' or event == sg.WINDOW_CLOSED:
            break

        if event == 'Imprimir':
            window.Element('-TEXT-').Update(values['-COMBO-'])

    window.close()
