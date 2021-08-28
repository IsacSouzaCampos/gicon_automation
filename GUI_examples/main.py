import PySimpleGUI as sg


def main():
    header = [sg.T(f'header{i}', pad=(14, 0)) for i in range(5)]
    inputs = [[sg.In(((j * 5) + i), size=(10, 1), pad=(0, 0)) for i in range(5)] for j in range(10)]

    layout = [
        header,
        [sg.Column(inputs, scrollable=True)]
    ]

    frame = [
        [sg.Frame('Title', layout)],
        [sg.OK(size=(5, 1)), sg.Button('Cancel', size=(5, 1))]
    ]

    window = sg.Window('Test', frame)
    event, values = window.read()
    print(event, values)

    window.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
