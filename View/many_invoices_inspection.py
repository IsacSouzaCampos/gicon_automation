import PySimpleGUI as sg


def show_results_table(header: list, table: list) -> list or None:
    layout = [
        [sg.Table(values=table, headings=header, selected_row_colors=('black', 'gray'), key='table')],
        [sg.Button('Editar'), sg.Button('Atualizar')],
        [sg.Input(key='invoice_n', size=(12, 20)), sg.Input(key='date', size=(12, 20)),
         sg.Input(key='gross_value', size=(12, 20)), sg.Input(key='iss', size=(12, 20)),
         sg.Input(key='ir', size=(12, 20)), sg.Input(key='csrf', size=(12, 20)),
         sg.Input(key='net_value', size=(12, 20)), sg.Input(key='nature', size=(12, 20))],
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
                edit_row(window, table[selected_row])
            except Exception as e:
                print(e)
        if event == 'Atualizar':
            row = [values['invoice_n'], values['date'],
                   values['gross_value'], values['iss'],
                   values['ir'], values['csrf'],
                   values['net_value'], values['nature']]
            table = update_table(window, table, selected_row, row)

        if event == 'Lançar':
            if sg.popup('Deseja realmente lançar os dados no sistema?', custom_text=('Sim', 'Não')) == 'Sim':
                window.close()
                return table

    window.close()


def edit_row(window: sg.Window, row: list) -> None:
    window.Element('invoice_n').Update(int(row[0]))
    window.Element('date').Update(row[1])

    float_values = {'gross_value': 2, 'iss': 3, 'ir': 4, 'csrf': 5, 'net_value': 6}
    for key in float_values:
        i = float_values[key]
        if row[i] and row[i] != '-':
            window.Element(key).Update(round(float(row[i]), 2))
        else:
            window.Element(key).Update(row[i])

    window.Element('nature').Update(int(row[7]))


def update_table(window: sg.Window, table: list, selected_row: int, row: list) -> list:
    table = [table[i] if i != selected_row else row for i in range(len(table))]
    window.Element('table').Update(values=table)
    return table
