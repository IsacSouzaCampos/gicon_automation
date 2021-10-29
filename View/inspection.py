import PySimpleGUI as sg
import os
import re

import Model.constants as const
from Model.invoices_list import InvoicesList


class MainGUI:
    def __init__(self, folder: str = '', xml_files: list = None, service_type: int = None):
        self.folder = folder
        self.xml_files = xml_files
        self.service_type = service_type

    def show(self):
        """
        Gera interface onde será informado o tipo do serviço (tomado, prestado) e a
        localização da pasta que contém os arquivos XML a serem conferidos.

        # :return: Tupla contendo o nome da pasta escolhida, arquivos xml nela contidos e o tipo de serviço selecionado.
        # :rtype:  (tuple)
        """

        sg.theme('default1')

        radio = [False, False]
        if self.service_type is not None:
            radio[self.service_type] = True
        service_type_layout = [[sg.Radio('Prestado', 'radio1', default=radio[0])],
                               [sg.Radio('Tomado', 'radio1', default=radio[1])]]

        service_type_col = [[sg.Column(service_type_layout, size=(425, 70))]]

        layout = [
            [sg.Frame('Tipo de Serviço', service_type_col)],
            [sg.Text('Selecione a pasta que contém as notas a serem conferidas:')],
            [sg.Input(self.folder), sg.FolderBrowse('Selecionar Pasta')],
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
                if not values['Selecionar Pasta'] and not self.folder:
                    sg.popup('Selecione uma pasta para a conferência!')
                    continue
                if values[0]:  # prestado
                    self.service_type = 0
                    self.folder = values['Selecionar Pasta'] or self.folder
                    self.xml_files = [f for f in os.listdir(self.folder) if '.xml' in f]
                    # sg.popup('A conferência deste tipo de serviço ainda está em desenvolvimento.')
                    # continue
                    break
                elif values[1]:  # tomado
                    # se a pasta não foi selecionada use a pasta atual `.`
                    self.service_type = 1
                    self.folder = values['Selecionar Pasta'] or '.'
                    self.xml_files = [f for f in os.listdir(self.folder) if '.xml' in f]
                    break
                else:
                    sg.popup('Selecione o tipo de conferência a ser feita!')

        window.close()
        # return folder_name, xml_file_names, service_type


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


class EditableResultTable:
    def __init__(self, invoices: InvoicesList, companies: list = None, n_errors: int = None, window: sg.Window = None):
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
        self.window = window

    def show(self) -> list:
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
            errors_link = [sg.Text(str(self.n_errors) + ' ' + const.ERROR_LINK_TEXT, text_color='blue',
                                   enable_events=True, key='-ERRORS-')
                           if self.n_errors > 0 else sg.Text(str(self.n_errors) + ' ' + const.ERROR_LINK_TEXT,
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

        self.window = sg.Window('Resultados da Conferênca', layout, finalize=True)

        while True:
            event, values = self.window.read()

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
                    self.update(table[index], range(start, end))
                self.n_errors = self.update_errors() if self.n_errors is not None else None

            if event == '-ERRORS-':
                if not self.n_errors:
                    continue

                errors_indexes = [i for i, row in enumerate(table) if const.TAX_EXTRACTION_ERROR in row]
                errors_list = [self.invoices.index(i) for i in errors_indexes]

                errors_inv_list = InvoicesList(errors_list)
                errors_gui = EditableResultTable(errors_inv_list)
                err_values = errors_gui.show()
                resulting_table = errors_gui.get_table_values(err_values, int(len(err_values)/len(header)), len(header))

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

                        self.update(row, r)
                        new_table.append(row)
                        self.invoices.update_invoice(i, row)
                        i += 1
                    else:
                        new_table.append(row)
                table = new_table

                self.n_errors = self.update_errors() if self.n_errors is not None else None

            if event == 'Atualizar':
                break

            if event == 'Lançar':
                if sg.popup('Deseja realmente lançar os dados no sistema?', custom_text=('Sim', 'Não')) == 'Sim':
                    break

        self.window.close()

        # atualiza tabela com os valores contidos atualmente na tabela de edição
        final_table = self.get_table_values(values, len(table), len(header))
        final_table = [self.set_row_types(header, row) for row in final_table]
        [self.invoices.update_invoice(i, row) for i, row in enumerate(final_table)]
        # invoices.print_list()
        return values

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

    def update(self, row: list, r: range) -> None:
        """
        Atualiza uma determinada linha na tabela da GUI.

        :param row:    Valores da linha a ser atualizada.
        :type row:     (list)
        :param r:      Faixa de posições a serem atualizadas.
        :type r:       (range)
        """

        [self.window.Element(n).Update(row[i]) for i, n in enumerate(r)]

    def update_errors(self):
        n_errors = self.invoices.number_of_errors()
        self.window.Element('-ERRORS-').Update(str(n_errors) + ' ' + const.ERROR_LINK_TEXT)

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
    def get_table_values(values: list, n_rows: int, n_columns: int) -> list:
        """
        Retorna o uma lista com os valores contidos atualmente na tabela editável.

        :param values:    Números dos inputs da tabela editável e seus respectivos valores.
        :type values:     (list)
        :param n_rows:    Número de linhas da tabela editável.
        :type n_rows:     (int)
        :param n_columns: Número de colunas da tabela editável.
        :type n_columns:  (int)
        :return:          Tabela com os valores extraídos da GUI da tabela editável.
        :rtype:           (list)
        """

        return [[values[(j * n_columns) + i] for i in range(n_columns)] for j in range(n_rows)] if values else []


class ResultTable:
    def __init__(self, invoices: InvoicesList, companies: list = None, n_errors: int = None):
        self.invoices = invoices
        self.companies = companies
        self.n_errors = n_errors
        self.window = None

    def show(self):
        """Mostra tabela de resultados simplificada por conta do número grande de notas conferidas."""

        inputs_header = [sg.Text(h, size=(10, 1), justification='center') for h in const.HEADER2]
        inputs = [sg.Input(key=k, size=(12, 1), justification='center') for k in const.HEADER2]

        inspection_data_layouts = [[[inputs_header[i]], [inputs[i]]] for i in range(len(inputs))]
        inspection_data_cols = [[sg.Column(inspection_data_layouts[i], pad=(0, 0)) for i in range(len(inputs))]]

        errors_link = [
            sg.Text(f'{self.n_errors} {const.ERROR_LINK_TEXT}', text_color='blue', enable_events=True, key='-ERRORS-')
            if self.n_errors > 0 else sg.Text(f'{self.n_errors} {const.ERROR_LINK_TEXT}', text_color='blue',
                                              key='-ERRORS-')]

        table = list()
        for invoice in self.invoices:
            irrf_value = '' if not invoice.taxes.irrf.value else invoice.taxes.irrf.value
            csrf_value = '' if not invoice.taxes.csrf.value else invoice.taxes.csrf.value
            table.append([invoice.serial_number, invoice.issuance_date, invoice.gross_value, invoice.taxes.iss.value,
                          irrf_value, csrf_value, invoice.net_value, invoice.nature])

        layout = [
            # [sg.Combo(self.companies, size=(30, 1), key='-COMBO-'), sg.Button('Filtrar'),
            #  sg.Button('Limpar Filtro', disabled=True)],
            [
             # sg.Text('CNPJ/CPF'),
             # sg.Input(size=(2, 1), change_submits=True, do_not_clear=True, key='-IN_FIL1-'),
             # sg.Text('.', pad=(0, 0)),
             # sg.Input(size=(3, 1), change_submits=True, do_not_clear=True, key='-IN_FIL2-'),
             # sg.Text('.', pad=(0, 0)),
             # sg.Input(size=(3, 1), change_submits=True, do_not_clear=True, key='-IN_FIL3-'),
             # sg.Text('/', pad=(0, 0)),
             # sg.Input(size=(4, 1), change_submits=True, do_not_clear=True, key='-IN_FIL4-'),
             # sg.Text('-', pad=(0, 0)),
             # sg.Input(size=(2, 1), change_submits=True, do_not_clear=True, key='-IN_FIL5-'),
             sg.Text('CNPJ/CPF'), sg.Input(size=(20, 1), key='-INPUT_FILTER-'), sg.Button('Filtrar'),
             sg.Button('Limpar Filtro', disabled=True), sg.Text('Natureza', pad=((98, 0), (0, 0))),
             sg.Input(size=(15, 1), key='-NATURE-'),
             sg.Button('Atualizar Natureza')],

            [sg.Table(values=table, headings=const.HEADER1, selected_row_colors=('black', 'gray'), key='table')],
            [sg.Button('Editar'), sg.Button('Atualizar')],
            inspection_data_cols,
            errors_link,
            [sg.Text()],
            [sg.Button('Lançar')]
        ]

        self.window = sg.Window('Resultados da Conferência', layout)

        temp_inv_lst = InvoicesList([])
        selected_row = -1
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                self.window.close()
                return False, InvoicesList([])

            # if event in ['-IN_FIL1-', '-IN_FIL2-', '-IN_FIL3-', '-IN_FIL4-', '-IN_FIL5-']:
            #     self.window[event].Update(re.sub("[^0-9]", "", values[event]))
            # if event == '-IN_FIL1-' and len(self.window[event].Get()) == 2:
            #     self.window['-IN_FIL2-'].SetFocus()
            # if event == '-IN_FIL2-' and len(self.window[event].Get()) == 3:
            #     self.window['-IN_FIL3-'].SetFocus()
            # if event == '-IN_FIL3-' and len(self.window[event].Get()) == 3:
            #     self.window['-IN_FIL4-'].SetFocus()
            # if event == '-IN_FIL4-' and len(self.window[event].Get()) == 4:
            #     self.window['-IN_FIL5-'].SetFocus()
            # if event == '-IN_FIL5-' and len(self.window[event].Get()) == 2:
            #     self.window['Filtrar'].SetFocus()

            if event == 'Filtrar':
                # _filter = values['-IN_FIL1-'] + values['-IN_FIL2-'] + values['-IN_FIL3-'] + \
                #          values['-IN_FIL4-'] + values['-IN_FIL5-']

                temp_inv_lst = self.invoices.cnpj_filter(values['-INPUT_FILTER-'], self.invoices.index(0).service_type)
                temp_lst = temp_inv_lst.get_gui_table()
                self.window['table'].Update(temp_lst)
                self.window['Limpar Filtro'].Update(disabled=False)
                continue

            if event == 'Limpar Filtro':
                self.window['table'].Update(self.invoices.get_gui_table())
                self.window['Limpar Filtro'].Update(disabled=True)
                continue

            if event == 'Editar':
                try:
                    selected_row = values['table'][0]
                    self.edit_row(const.HEADER2, table[selected_row])
                except Exception as e:
                    print(e)

            if event == 'Atualizar Natureza':
                lst = temp_inv_lst if temp_inv_lst else self.invoices
                nature = values['-NATURE-']
                for i in range(len(lst)):
                    if lst.index(i).set_nature(nature) < 0:
                        continue
                self.window['table'].Update(lst.get_gui_table())
                continue

            if event == 'Atualizar':
                row = [values[const.HEADER2[i]] for i in range(len(const.HEADER2))]
                table = self.update(table, selected_row, row)
                self.window.Element('-ERRORS-').Update(f'{self.n_errors} {const.ERROR_LINK_TEXT}')
                self.update(table)
                continue

            if event == '-ERRORS-':
                if not self.n_errors:
                    continue

                errors_indexes = [i for i, row in enumerate(table) if const.TAX_EXTRACTION_ERROR in row]
                errors_list = [self.invoices.index(i) for i in errors_indexes]

                errors_inv_list = InvoicesList(errors_list)
                errors_gui = EditableResultTable(errors_inv_list)
                err_values = errors_gui.show()

                resulting_table = None
                if err_values:
                    n_rows = int(len(err_values) / len(const.HEADER2))
                    n_columns = len(const.HEADER2)
                    resulting_table = errors_gui.get_table_values(err_values, n_rows, n_columns)

                if resulting_table is None:
                    continue

                new_table = list()
                i = 0
                for index, row in enumerate(table):
                    if index in errors_indexes:
                        new_table.append(resulting_table[i])
                        i += 1
                    else:
                        new_table.append(row)
                table = new_table
                self.update(table)
                continue

            if event == 'Lançar':
                if sg.popup('Deseja realmente lançar os dados no sistema?', custom_text=('Sim', 'Não')) == 'Sim':
                    break

        self.window.close()
        return True, self.invoices

    def edit_row(self, header: list, row: list) -> None:
        """Atualiza campos de edição de dados."""
        [self.window.Element(header[i]).Update(row[i]) for i in range(len(header))]

    def update(self, table: list, selected_row: int = None, row: list = None) -> list and int:
        """Atualiza tabela de conferência com os dados no formato adequado."""
        if selected_row is None:  # se selected_row = None, a atualização vem de outra tela
            self.window.Element('table').Update(values=table)
            self.n_errors = self.invoices.number_of_errors()
            self.window.Element('-ERRORS-').Update(value=f'{self.n_errors} {const.ERROR_LINK_TEXT}')
            return table

        row = row[:2] + [row[i] if row[i] in ['', '-'] else round(float(row[i].replace(',', '.')), 2)
                         for i in range(2, 7)] + [int(row[7])]
        table = [table[i] if i != selected_row else row for i in range(len(table))]
        self.window.Element('table').Update(values=table)

        self.invoices.update_invoice(selected_row, row)
        self.n_errors = self.invoices.number_of_errors()
        return table
