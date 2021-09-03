import PySimpleGUI as sg


def show_results_table(table_header: list, table: list) -> list or None:
    """Mostra tabela de resultados simplificada por conta do número grande de notas conferidas."""
    inputs_text_header = ['Nº Nota', 'Data', 'Valor Bruto', 'ISS', 'IR',
                          'CSRF', 'Valor Líquido', 'Natureza']

    inputs_header = [sg.Text(h, size=(10, 1), justification='center') for h in inputs_text_header]
    inputs = [sg.Input(key=k, size=(12, 1), justification='center') for k in inputs_text_header]

    inspection_data_layouts = [[[inputs_header[i]], [inputs[i]]] for i in range(len(inputs))]
    inspection_data_cols = [[sg.Column(inspection_data_layouts[i], pad=(0, 0)) for i in range(len(inputs))]]

    layout = [
        [sg.Table(values=table, headings=table_header, selected_row_colors=('black', 'gray'), key='table')],
        [sg.Button('Editar'), sg.Button('Atualizar')],
        inspection_data_cols,
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

        if event == 'Lançar':
            if sg.popup('Deseja realmente lançar os dados no sistema?', custom_text=('Sim', 'Não')) == 'Sim':
                window.close()
                return table

    window.close()


def edit_row(window: sg.Window, header: list, row: list) -> None:
    """Atualiza campos de edição de dados."""
    [window.Element(header[i]).Update(row[i]) for i in range(len(header))]


def update_table(window: sg.Window, table: list, selected_row: int, row: list) -> list:
    """Atualiza tabela de conferência com os dados no formato adequado."""
    row = row[:2] + [row[i] if row[i] in ['', '-'] else round(float(row[i])) for i in range(2, 7)] + [int(row[7])]
    table = [table[i] if i != selected_row else row for i in range(len(table))]
    window.Element('table').Update(values=table)
    return table
