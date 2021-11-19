import PySimpleGUI as sg


class InsertionCommandsView:
    def __init__(self, text: str):
        self.text = text

    def show(self):
        layout = [[sg.Multiline(self.text, size=(100, 30))]]
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
