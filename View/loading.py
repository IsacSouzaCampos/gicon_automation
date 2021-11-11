import PySimpleGUI as sg


class Loading:
    def __init__(self, text='', window: sg.Window = None, total_size: int = None):
        """
                Atualiza a barra de progresso da conferência.

                :param text:           Texto informativo sobre o que está carregando.
                :type text:            (str)
                :param window:         Janela de carregamento a ser atualizada.
                :type window:          (sg.Window)
                :param total_size:     Número total de notas a serem conferidas.
                :type total_size:      (int)
                """
        self.text = text
        self.window = window
        self.total_size = total_size

    def start(self):
        """
        Inicializa a janela que mostrará o progresso da conferência

        :return: Janela de carregamento das conferências.
        :rtype:  (sg.Window)
        """

        layout = [
            [sg.Text(self.text, key='-TEXT-')],
            [sg.ProgressBar(1, orientation='horizontal', size=(40, 20), key='progress')]
        ]

        self.window = sg.Window('Conferindo Notas', layout, disable_close=True, finalize=True)

    def update(self, invoice_number: int, progress: int):
        self.window.Element('-TEXT-').Update(self.text + 'Nota: ' + str(invoice_number))
        self.window.Element('progress').UpdateBar(progress, self.total_size)

    def close(self):
        self.window.close()
