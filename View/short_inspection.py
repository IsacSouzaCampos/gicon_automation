import PySimpleGUI as sg
from Model.constants import MAX_INVOICES, ERROR_LINK_TEXT, TAX_EXTRACTION_ERROR
from Model.invoices_list import InvoicesList
import os


class MainGUI:
    @staticmethod
    def show() -> tuple:
        """
        Gera interface onde será informado o tipo do serviço (tomado, prestado) e a
        localização da pasta que contém os arquivos XML a serem conferidos.

        :return: Tupla contendo o nome da pasta escolhida, arquivos xml nela contidos e o tipo de serviço selecionado.
        :rtype:  (tuple)
        """

        sg.theme('default1')

        folder_name = str()
        xml_file_names = list()
        service_type = int()

        service_type_layout = [[sg.Radio('Prestado', 'radio1', default=False)],
                               [sg.Radio('Tomado', 'radio1', default=False)]]

        service_type_col = [[sg.Column(service_type_layout, size=(425, 70))]]

        layout = [
            [sg.Frame('Tipo de Serviço', service_type_col)],
            [sg.Text('Selecione a pasta que contém as notas a serem conferidas:')],
            [sg.Input(), sg.FolderBrowse('Selecionar Pasta')],
            [sg.Submit('Conferir'), sg.Cancel('Cancelar')],
        ]

        window = sg.Window('Conferência Automatizada', layout)

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                window.close()
                from sys import exit  # para não gerar erro no executável
                exit()

            if event == 'Conferir':
                if not values['Selecionar Pasta']:
                    sg.popup('Selecione uma pasta para a conferência!')
                    continue
                if values[0]:  # prestado
                    # service_type = 0
                    # folder_name = values['Selecionar Pasta'] or '.'
                    # xml_file_names = [f for f in os.listdir(folder_name) if '.xml' in f]
                    sg.popup('A conferência deste tipo de serviço ainda está em desenvolvimento.')
                    continue
                    # break
                elif values[1]:  # tomado
                    # se a pasta não foi selecionada use a pasta atual `.`
                    service_type = 1
                    folder_name = values['Selecionar Pasta'] or '.'
                    xml_file_names = [f for f in os.listdir(folder_name) if '.xml' in f]
                    break
                else:
                    sg.popup('Selecione o tipo de conferência a ser feita!')

        window.close()
        return folder_name, xml_file_names, service_type


class Loading:
    def __init__(self, window: sg.Window = None, total_size: int = None):
        """
                Atualiza a barra de progresso da conferência.

                :param window:         Janela de carregamento a ser atualizada.
                :type window:          (sg.Window)
                :param total_size:     Número total de notas a serem conferidas.
                :type total_size:      (int)
                """
        self.window = window
        self.total_size = total_size

    def inspection(self):
        """
        Inicializa a janela que mostrará o progresso da conferência

        :return: Janela de carregamento das conferências.
        :rtype:  (sg.Window)
        """

        layout = [
            [sg.Text(key='text')],
            [sg.ProgressBar(1, orientation='horizontal', size=(40, 20), key='progress')]
        ]

        self.window = sg.Window('Conferindo Notas', layout, disable_close=True, finalize=True)

    def update(self, invoice_number: int, progress: int):
        self.window.Element('text').Update('Nota: ' + str(invoice_number))
        self.window.Element('progress').UpdateBar(progress, self.total_size)

    def close(self):
        self.window.close()


class PopUp:
    @staticmethod
    def max_invoices() -> int:
        """
        Popup de aviso de limite de notas excedido.

        :return: Valor referente à opçõa escolhida pelo usuário no tratamento do caso.
        :rtype:  (int)
        """
        layout = [
            [sg.Text(f'Número limite de notas excedido ({MAX_INVOICES}). Com um número assim, a edição das'
                     ' notas com possíveis erros não é tão prática quanto com a tela padrão do sistema. '
                     f'Gostaria que as notas fossem separadas em subgrupos de {MAX_INVOICES} ou conferir '
                     'com uma interface gráfica mais simplificada?', size=(50, 5))],

            [sg.Button('Conferir com interface simplificada'), sg.Button(f'Criar subgrupos de {MAX_INVOICES} notas')]
        ]

        window = sg.Window('Limite de Notas Excedido', layout)
        event, values = window.read()
        window.close()

        if event == f'Criar subgrupos de {MAX_INVOICES} notas':
            return 0
        elif event == 'Conferir com interface simplificada':
            return 1
        else:
            return 2


class ResultTable:
    def __init__(self, invoices: InvoicesList, companies: list = None, n_errors: int = None):
        """
        Cria tabela de resultados editável.

        :param invoices:     Lista de notas.
        :type invoices:      (InvoiceList)
        :param companies:    Empresa tomadora e prestadora do serviço.
        :type companies:     (list)
        :param n_errors:     Número de erros detectados pelo algoritmo.
        :type n_errors:      (int)
        :return:             Lista com o resultado da edição ou None se o botão de fechar janela for acionado.
        :rtype:              (list or None)
        """
        self.invoices = invoices
        self.companies = companies
        self.n_errors = n_errors

    def show(self):
        header = ['Nº nota', 'Emissão', 'Valor Bruto', 'ISS', 'IR', 'CSRF', 'Valor Líquido', 'Natureza']
        n_columns = len(header)

        table_header = [sg.Text(header[0], pad=(35, 0)), sg.Text(header[1], pad=(25, 0)),
                        sg.Text(header[2], pad=(25, 0)), sg.Text(header[3], pad=(35, 0)),
                        sg.Text(header[4], pad=(52, 0)), sg.Text(header[5], pad=(30, 0)),
                        sg.Text(header[6], pad=(20, 0)), sg.Text(header[7], pad=(20, 0))]

        # print('invoices type:', type(invoices.invoices[0]))
        # input()
        table = self.invoices.get_gui_table()
        # print('invoices type:', type(invoices))
        # input()

        input_rows = [[sg.Input(v if v != 0 else '', size=(15, 1), pad=(0, 0), justification='center')
                       for j, v in enumerate(row[:8])] +
                      [sg.Button('...', pad=(0, 0), key='detail_' + str(i))] for i, row in enumerate(table)]

        frame = [
            table_header,
            [sg.Column(input_rows, size=(900, 200), scrollable=True, vertical_scroll_only=True, key='-COL-')]
        ]

        errors_link = []
        if self.n_errors is not None:
            errors_link = [sg.Text(str(self.n_errors) + ' ' + ERROR_LINK_TEXT, text_color='blue', enable_events=True,
                                   key='-ERRORS-')
                           if self.n_errors > 0 else sg.Text(str(self.n_errors) + ' ' + ERROR_LINK_TEXT,
                                                             text_color='blue', key='-ERRORS-')]

        # o botão que aparece ao final da tela será escolhido de acordo com o valor de n_errors
        # Atualizar caso seja tela com erros apenas e lançar caso seja tela com todos os resultados
        button = [sg.Button('Atualizar', size=(10, 1))] if self.n_errors is None else [sg.Button('Lançar',
                                                                                                 size=(10, 1))]

        # combo_text = 'Filtro por empresa: '
        # combo_layout = [[sg.Text(combo_text), sg.Combo(companies, size=(45, 1), key='-COMBO-'), sg.Button('Filtrar')]]
        # combo_column = [[sg.Column(combo_layout, size=(910, 40))]]

        layout = [
            # implementar futuramente
            # [sg.Text(combo_text), sg.Combo(companies, size=(45, 1), key='-COMBO-'), sg.Button('Filtrar')],
            # [sg.Frame('Filtro', combo_column)],
            [sg.Frame('Tabela de Resultados', frame, key='-FRAME-')],
            errors_link,
            [sg.Text()],
            button
        ]

        window = sg.Window('Resultados da Conferênca', layout, finalize=True)

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event is None:
                # exit()  # REMOVER APÓS TERMINAR TESTES
                # return InvoicesList([])
                self.invoices = InvoicesList([])
                break

            if 'detail_' in event:
                # prepara para informações necessárias para obtenção de lista com os
                # valores contidos na linha selecionada
                index = int(event.split('_')[1])
                start = index * n_columns
                end = start + n_columns

                selected_row = [values[i] for i in range(start, end)]

                # # complementa com os dados que estão na tabela e não são mostrados na tabela editável
                # row = row + table[index][(end - start):]

                # atualiza tabela com os valores contidos na GUI
                new_table = self.get_table_values(values, len(self.invoices), len(header))
                for i, row in enumerate(new_table):
                    new_table[i] = self.set_row_types(header, row)
                    self.invoices.update_invoice(i, row)
                # new_table = [set_row_types(header, row) for row in new_table]

                invoices, changed = self.service_details(self.invoices, header, selected_row, index)
                if changed:
                    table = invoices.get_gui_table()
                    # print('row:', table[index])
                    self.update(window, table[index], range(start, end))
                self.n_errors = self.update_errors(invoices, window) if self.n_errors is not None else None

            if event == '-ERRORS-':
                if not self.n_errors:
                    continue

                errors_indexes = [i for i, row in enumerate(table) if TAX_EXTRACTION_ERROR in row]
                errors_list = [self.invoices.index(i) for i in errors_indexes]

                errors_inv_list = InvoicesList(errors_list)
                resulting_table = errors_inv_list.get_gui_table()

                if not resulting_table:
                    continue

                new_table = list()
                i = 0
                for index, row in enumerate(table):
                    if index in errors_indexes:
                        row = resulting_table[i]

                        start = index * n_columns
                        end = start + n_columns
                        r = range(start, end)

                        self.update(window, row, r)
                        new_table.append(row)
                        self.invoices.update_invoice(i, row)
                        i += 1
                    else:
                        new_table.append(row)
                table = new_table

                self.n_errors = self.update_errors(self.invoices, window) if self.n_errors is not None else None

            if event == 'Atualizar':
                break

            if event == 'Lançar':
                if sg.popup('Deseja realmente lançar os dados no sistema?', custom_text=('Sim', 'Não')) == 'Sim':
                    break

        window.close()

        # atualiza tabela com os valores contidos atualmente na tabela de edição
        final_table = self.get_table_values(values, len(table), len(header))
        final_table = [self.set_row_types(header, row) for row in final_table]
        [self.invoices.update_invoice(i, row) for i, row in enumerate(final_table)]
        # invoices.print_list()
        # return self.invoices if not self.invoices.empty() else InvoicesList([])

    def service_details(self, invoices: InvoicesList, header: list, row: list, row_index: int) -> tuple:
        """
        Mostra ao usuário detalhes referentes ao serviço que não aparecem em outras janelas.

        :param invoices:     Lista de notas.
        :type invoices:      (InvoicesList)
        :param header:       Cabeçalho dos dados a serem possivelmente editados.
        :type header:        (list)
        :param row:          Linha selecionada a ser mostrada na janela.
        :type row:           (list)
        :param row_index:    Índice da linha selecionada (row).
        :type row_index:     (int)
        :return:             Linha selecionada com os valores atualizados.
        :rtype:              (list or None)
        """

        keys = ['invoice_n', 'date', 'gross_value', 'iss', 'ir', 'csrf', 'net_value', 'nature']
        input_size = (12, 1)
        header_size = (10, 1)
        # tamanho dos boxes de texto informativos
        text_width = ((input_size[0]) * len(keys)) + (len(keys) + 1)

        txt_color = 'black'

        # gera a lista de inputs para edição dos dados conferidos
        inputs = [sg.Input(row[i], key=k, size=input_size, justification='center')
                  for i, k in enumerate(keys)]

        table_header = [sg.Text(h, size=header_size, justification='center') for h in header]

        invoice = invoices.index(row_index)

        provider_name_layout = [[sg.Text(invoice.provider.name, size=(text_width, 1), text_color=txt_color)]]
        taker_name_layout = [[sg.Text(invoice.taker.name, size=(text_width, 1), text_color=txt_color)]]
        description_layout = [[sg.Text(invoice.service_description, size=(text_width, 7), text_color=txt_color)]]
        additional_data_layout = [[sg.Text(invoice.aditional_data, size=(text_width, 7), text_color=txt_color)]]

        provider_name_col = [[sg.Column(provider_name_layout)]]
        taker_name_col = [[sg.Column(taker_name_layout)]]
        description_col = [[sg.Column(description_layout)]]
        additional_data_col = [[sg.Column(additional_data_layout)]]

        inspection_data_layouts = [[[table_header[i]], [inputs[i]]] for i in range(len(inputs))]
        inspection_data_cols = [[sg.Column(inspection_data_layouts[i]) for i in range(len(inputs))]]

        layout = [
            [sg.Frame('Prestador', provider_name_col)],
            [sg.Frame('Tomador', taker_name_col)],
            [sg.Text()],

            [sg.Frame('Descrição do Serviço', description_col)],
            [sg.Frame('Dados Adicionais', additional_data_col)],
            [sg.Text()],

            [sg.Frame('Dados da Conferência', inspection_data_cols)],
            [sg.Text()],

            [sg.OK(key='ok_button', size=(12, 1))]
        ]

        window = sg.Window('Nota: ' + row[0], layout)
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            return invoices, False

        if event == 'ok_button':
            # se mantém em loop enquanto o número de dígitos da natureza não for 7
            while len(values['nature']) != 7:
                sg.popup('A natureza digitada não está de acordo com o padrão (7 dígitos)')
                event, values = window.read()

                if event == sg.WINDOW_CLOSED:
                    return invoices, False

                if event == 'ok_button':
                    break

            new_row = [values[key] for key in values]
            # print('new row:', new_row)

            # atualizar linha com os formatos corretos dos valores
            # gross_value, iss, ir, csrf, net_value
            new_row = self.set_row_types(header, new_row)

            invoices.update_invoice(row_index, new_row)
            # inv = invoices.index(row_index)
            # print('invoice:', inv.serial_number, 'ir:', inv.taxes.irrf.value, 'csrf:', inv.taxes.csrf.value)
            window.close()

        return invoices, True

    @staticmethod
    def update(window: sg.Window, row: list, r: range) -> None:
        """
        Atualiza uma determinada linha na tabela da GUI.

        :param window: Janela a ser atualizada.
        :type window:  (sg.Window)
        :param row:    Valores da linha a ser atualizada.
        :type row:     (list)
        :param r:      Faixa de posições a serem atualizadas.
        :type r:       (range)
        """

        [window.Element(n).Update(row[i]) for i, n in enumerate(r)]

    @staticmethod
    def update_errors(invoices, window):
        n_errors = invoices.number_of_errors()
        window.Element('-ERRORS-').Update(str(n_errors) + ' ' + ERROR_LINK_TEXT)
        return n_errors

    @staticmethod
    def set_row_types(header: list, row: list) -> list:
        """
        Corrige o tipo dos valores da linha.

        :param header: Lista de títulos do cabeçalho da tabela mostrada ao usuário.
        :type header:  (list)
        :param row:    Linha contendo os valores a terem seus tipos settados.
        :type row:     (list)
        :return:       Linha dada como entrada com seus valores settados para o formato correto.
        :rtype:        (list)
        """

        # natureza está na posição 7
        nature_pos = header.index('Natureza')
        float_values = list()

        for i in range(2, nature_pos):
            r = row[i].replace(',', '.')
            if r in ['-', '******']:
                float_values.append(r)
            elif not r:
                float_values.append('')
            else:
                float_values.append(float(r))

        if row[nature_pos].isnumeric():
            row = [int(row[0]), row[1]] + float_values + [int(row[nature_pos])] + row[(nature_pos + 1):]
        else:
            row = [int(row[0]), row[1]] + float_values + [row[nature_pos]] + row[(nature_pos + 1):]

        return row

    @staticmethod
    def get_table_values(values: dict, n_rows: int, n_columns: int) -> list:
        """
        Retorna o uma lista com os valores contidos atualmente na tabela editável.

        :param values:    Números dos inputs da tabela editável e seus respectivos valores.
        :type values:     (dict)
        :param n_rows:    Número de linhas da tabela editável.
        :type n_rows:     (int)
        :param n_columns: Número de colunas da tabela editável.
        :type n_columns:  (int)
        :return:          Tabela com os valores extraídos da GUI da tabela editável.
        :rtype:           (list)
        """

        return [[values[(j * n_columns) + i] for i in range(n_columns)] for j in range(n_rows)] if values else []
