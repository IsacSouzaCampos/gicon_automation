import PySimpleGUI as sg
import os

import Model.constants as const
from Model.invoices_list import InvoicesList
from Model.filter import Filter

from View.warnings import Warnings


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

        radio = [True, False]
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
                    if not values['Selecionar Pasta'] and not self.folder:
                        sg.popup('Selecione uma pasta para a conferência!')
                        continue
                    self.service_type = 1
                    self.folder = values['Selecionar Pasta'] or self.folder
                    self.xml_files = [f for f in os.listdir(self.folder) if '.xml' in f]
                    break
                else:
                    sg.popup('Selecione o tipo de conferência a ser feita!')

        window.close()
        # return folder_name, xml_file_names, service_type


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

        table = self.invoices.get_gui_table()

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

        layout = [
            [sg.Frame('Tabela de Resultados', frame, key='-FRAME-')],
            errors_link,
            [sg.Text()],
            button
        ]

        self.window = sg.Window('Resultados da Conferênca', layout, finalize=True)

        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED or event is None:
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

                invoices, changed = self.service_details(self.invoices, header, selected_row, index)
                if changed:
                    table = invoices.get_gui_table()
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
    def __init__(self, invoices: InvoicesList, n_errors: int = None):
        self.invoices = invoices
        self.n_errors = n_errors
        self.window = None

    def show(self):
        """Mostra tabela de resultados simplificada por conta do número grande de notas conferidas."""

        table = list()
        for invoice in self.invoices:
            irrf_value = '' if not invoice.taxes.irrf.value else invoice.taxes.irrf.value
            csrf_value = '' if not invoice.taxes.csrf.value else invoice.taxes.csrf.value
            table.append([invoice.serial_number, invoice.issuance_date, invoice.gross_value, invoice.taxes.iss.value,
                          irrf_value, csrf_value, invoice.net_value, invoice.nature, invoice.withheld_type])

        if self.n_errors > 0:
            errors_link = sg.Text(f'{self.n_errors} {const.ERROR_LINK_TEXT}',
                                  text_color='blue', enable_events=True, key='-ERRORS-')
        else:
            errors_link = sg.Text(f'{self.n_errors} {const.ERROR_LINK_TEXT}', text_color='blue', key='-ERRORS-')

        withheld_types = {'Órgãos, Autarquias e Fundacoes Federais': 1,
                          'Demais Entidades da Administração Pública Federal': 2,
                          'Pessoas Jurídicas de Direito Privado': 3,
                          'Órgãos, Autarquias e Fundacoes dos Estados, Distrito Federal e Municípios': 4,
                          'Sociedade Cooperativa': 5,
                          'Fabricantes de Veículos e Máquinas': 6
                          }

        aditional_data_layout = [
            [sg.Text('Num. Empresa ', pad=((0, 0), (10, 10))),
             sg.Input(size=(14, 1), key='-COMPANY_NUMBER-', pad=((0, 550), (10, 10)))
             ]
        ]
        aditiona_data_frame = sg.Frame('Dados Adicionais', aditional_data_layout)

        layout = [
            [sg.Table(values=table, headings=const.HEADER1, selected_row_colors=('black', 'gray'), key='-TABLE-')],
            [sg.Text(f'{len(self.invoices)} registros', key='-N_REGISTERS-'), errors_link],
            [aditiona_data_frame],
            [sg.Button('Gerar SQL')],
        ]

        self.window = sg.Window('Resultados da Conferência', layout)

        temp_invs_lst = InvoicesList([])
        temp_table = list()
        temp_table_idxs = list()
        selected_row = -1
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                self.window.close()
                return False, InvoicesList([])

            if event == 'Filtrar':
                selected_fed_id = None
                if values['-RAD11-']:
                    selected_fed_id = 0
                elif values['-RAD12-']:
                    selected_fed_id = 1

                withheld_type = withheld_types[values['-WITHHELD_TYPE_FILTER-']] if values['-WITHHELD_TYPE_FILTER-'] \
                    else None

                temp_table_idxs, temp_invs_lst = Filter(self.invoices, values['-FED_ID_FILTER-'], selected_fed_id,
                                                        values['-ISS_FILTER-'], values['-IRRF_FILTER-'],
                                                        values['-CSRF_FILTER-'], values['-CNAE_CODE-'],
                                                        withheld_type).run()
                temp_table = temp_invs_lst.get_gui_table()
                self.window['-TABLE-'].Update(temp_table)
                self.window['-N_REGISTERS-'].Update(f'{len(temp_table)} registros')
                self.window['Limpar Filtro'].Update(disabled=False)

            if event == '-UPDATE_FILTER-':
                invs_lst = temp_invs_lst if temp_table else self.invoices
                nature = values['-NATURE-']
                wh_type_value = values['-WITHHELD_TYPE_UPDATE-']
                withheld_type = withheld_types[wh_type_value] if wh_type_value != '' else None

                if nature != '' and len(nature) != 7:
                    Warnings.msg('Natureza deve possuir 7 caracteres.')
                    continue
                try:
                    nature = int(nature) if nature else ''
                except Exception as e:
                    print(e)
                    Warnings.msg('Formato de natureza errado.')
                    continue

                for invoice in invs_lst:
                    invoice.nature = nature if nature else invoice.nature
                    invoice.withheld_type = withheld_type if withheld_type else None

                if temp_table:
                    temp_table = invs_lst.get_gui_table()
                    self.update(temp_table)
                    self.invoices.update(temp_table_idxs, temp_table)
                    table = self.invoices.get_gui_table()
                else:
                    table = invs_lst.get_gui_table()
                    self.update(table)
                self.window['-NATURE-'].Update('')

            if event == '-RESET-':
                if sg.popup('Deseja resetar Natureza e Tipo de Retenção?', custom_text=('Sim', 'Não')) == 'Sim':
                    for invoice in self.invoices:
                        invoice.reset_withheldtype()
                    table = self.invoices.get_gui_table()
                    self.update(table)

            if event == 'Limpar Filtro':
                self.window['-TABLE-'].Update(self.invoices.get_gui_table())
                self.window['-N_REGISTERS-'].Update(f'{len(self.invoices)} registros')
                self.window['Limpar Filtro'].Update(disabled=True)
                temp_invs_lst = InvoicesList([])
                temp_table = []

            if event == 'Editar':
                try:
                    selected_row = values['-TABLE-'][0]
                    if not len(temp_table):
                        self.edit_row(const.HEADER2, table[selected_row])
                    else:
                        self.edit_row(const.HEADER2, temp_table[selected_row])
                    self.window['Atualizar'].Update(disabled=False)
                except Exception as e:
                    print(e)

            if event == 'Atualizar':
                row = [values[const.HEADER2[i]] for i in range(len(const.HEADER2))]
                table = self.update(table, selected_row, row)
                self.window.Element('-ERRORS-').Update(f'{self.n_errors} {const.ERROR_LINK_TEXT}')
                self.update(table)
                self.window['Atualizar'].Update(disabled=True)

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

            if event == 'Gerar SQL':
                if self.n_errors > 0:
                    sg.popup('Há notas com erros na conferência. Corrija-as antes de lançar.')
                    continue
                if values['-COMPANY_NUMBER-']:
                    num = values['-COMPANY_NUMBER-']
                    for invoice in self.invoices:
                        invoice.client.set_code(num)
                break

        self.window.close()
        return True, self.invoices

    def edit_row(self, header: list, row: list) -> None:
        """Atualiza campos de edição de dados."""
        [self.window.Element(header[i]).Update(row[i]) for i in range(len(header))]

    def update(self, table: list, selected_row: int = None, row: list = None) -> list and int:
        """Atualiza tabela de conferência com os dados no formato adequado."""
        if selected_row is None:  # se selected_row = None, a atualização vem de outra tela
            self.window.Element('-TABLE-').Update(values=table)
            self.n_errors = self.invoices.number_of_errors()
            self.window.Element('-ERRORS-').Update(value=f'{self.n_errors} {const.ERROR_LINK_TEXT}')
            return table

        row = row[:2] + [row[i] if row[i] in ['', '-'] else round(float(row[i].replace(',', '.')), 2)
                         for i in range(2, 7)] + [int(row[7])]

        self.invoices.update_invoice(selected_row, row)
        table = self.invoices.get_gui_table()
        self.window.Element('-TABLE-').Update(values=table)
        self.n_errors = self.invoices.number_of_errors()
        return table
