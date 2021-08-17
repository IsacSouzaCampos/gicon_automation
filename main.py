import Model.excel_file as excel_file
import View.main_gui as gui


def main():
    folder, xml_files = gui.main_gui()
    excel_file.make_excel_file(folder, xml_files)


if __name__ == '__main__':
    main()
