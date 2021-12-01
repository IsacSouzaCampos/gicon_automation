import PySimpleGUI as sg

import Model.constants as const


class PopUp:
    @staticmethod
    def max_invoices() -> int:
        """
        Popup de aviso de limite de notas excedido.

        :return: Valor referente à opçõa escolhida pelo usuário no tratamento do caso.
        :rtype:  (int)
        """
        layout = [
            [sg.Text(f'Número limite de notas excedido ({const.MAX_INVOICES}). Com um número assim, a edição das'
                     ' notas com possíveis erros não é tão prática quanto com a tela padrão do sistema. '
                     f'Gostaria que as notas fossem separadas em subgrupos de {const.MAX_INVOICES} ou conferir '
                     'com uma interface gráfica mais simplificada?', size=(50, 5))],

            [sg.Button('Conferir com interface simplificada'), sg.Button(f'Criar subgrupos de '
                                                                         f'{const.MAX_INVOICES} notas')]
        ]

        window = sg.Window('Limite de Notas Excedido', layout)
        event, values = window.read()
        window.close()

        if event == f'Criar subgrupos de {const.MAX_INVOICES} notas':
            return 0
        elif event == 'Conferir com interface simplificada':
            return 1
        else:
            return 2

    @staticmethod
    def msg(msg):
        sg.popup(msg)
