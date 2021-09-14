import PySimpleGUI as sg
from Model.constants import ERROR_LINK_TEXT, TAX_EXTRACTION_ERROR

import View.invoices_inspection as inv_inspect
from Model.invoices_inspection_lib import number_of_errors


def show_results_table(table_header: list, table: list, n_errors: int) -> list or None:
    """Mostra tabela de resultados simplificada por conta do número grande de notas conferidas."""
    inputs_text_header = ['Nº Nota', 'Data', 'Valor Bruto', 'ISS', 'IR',
                          'CSRF', 'Valor Líquido', 'Natureza']

    inputs_header = [sg.Text(h, size=(10, 1), justification='center') for h in inputs_text_header]
    inputs = [sg.Input(key=k, size=(12, 1), justification='center') for k in inputs_text_header]

    inspection_data_layouts = [[[inputs_header[i]], [inputs[i]]] for i in range(len(inputs))]
    inspection_data_cols = [[sg.Column(inspection_data_layouts[i], pad=(0, 0)) for i in range(len(inputs))]]

    errors_link = [sg.Text(f'{n_errors} {ERROR_LINK_TEXT}', text_color='blue', enable_events=True, key='-ERRORS-')
                   if n_errors > 0 else sg.Text(f'{n_errors} {ERROR_LINK_TEXT}', text_color='blue', key='-ERRORS-')]

    layout = [
        [sg.Table(values=table, headings=table_header, selected_row_colors=('black', 'gray'), key='table')],
        [sg.Button('Editar'), sg.Button('Atualizar')],
        inspection_data_cols,
        errors_link,
        [sg.Text()],
        [sg.Button('Lançar')]
    ]

    window = sg.Window('Resultados da Conferência', layout)

    selected_row = -1
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == 'Editar':
            try:
                selected_row = values['table'][0]
                edit_row(window, inputs_text_header, table[selected_row])
            except Exception as e:
                print(e)
        if event == 'Atualizar':
            row = [values[inputs_text_header[i]] for i in range(len(inputs_text_header))]
            table = update_table(window, table, selected_row, row)

        if event == '-ERRORS-':
            if not n_errors:
                continue
            errors_indexes = [i for i, row in enumerate(table) if TAX_EXTRACTION_ERROR in row]
            errors_table = [row for i, row in enumerate(table) if TAX_EXTRACTION_ERROR in row]
            resulting_table = inv_inspect.editable_table(errors_table)

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
            n_errors = update_table(window, table)[1]

        if event == 'Lançar':
            if sg.popup('Deseja realmente lançar os dados no sistema?', custom_text=('Sim', 'Não')) == 'Sim':
                window.close()
                return table

    window.close()


def edit_row(window: sg.Window, header: list, row: list) -> None:
    """Atualiza campos de edição de dados."""
    [window.Element(header[i]).Update(row[i]) for i in range(len(header))]


def update_table(window: sg.Window, table: list, selected_row: int = None, row: list = None) -> list and int:
    """Atualiza tabela de conferência com os dados no formato adequado."""
    if not selected_row:  # se selected_row = None, a atualização vem de outra tela
        window.Element('table').Update(values=table)
        n_errors = number_of_errors(table)
        window.Element('-ERRORS-').Update(value=f'{n_errors} {ERROR_LINK_TEXT}')
        return table, n_errors

    row = row[:2] + [row[i] if row[i] in ['', '-'] else round(float(row[i])) for i in range(2, 7)] + [int(row[7])]
    table = [table[i] if i != selected_row else row for i in range(len(table))]
    window.Element('table').Update(values=table)
    return table, number_of_errors(table)
