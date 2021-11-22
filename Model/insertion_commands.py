# import PySimpleGUI as sg
from Model.constants import SYS_PATH
from Model.sql import SQLCommands

from datetime import datetime
# import pyperclip


class InsertionCommands:
    def __init__(self, commands: list, client_fed_id: int, client_code, service_type: int):
        self.commands = commands
        self.client_fed_id = client_fed_id
        self.client_code = client_code
        self.service_type = service_type

        now = datetime.now()
        self.month = now.month
        self.current_date = now.strftime('%d.%m.%Y')

    def to_string(self) -> str:
        # transforma a matriz commands em uma lista
        commands_list = list()
        for cmds in self.commands:
            for cmd in cmds:
                commands_list.append(cmd)

        text = ';\n\n'.join([command for command in commands_list]) + ';'
        return text

    def updates_commands(self) -> str:
        # sql_commands = SQLCommands(self.service_type)
        service_str_path = r'\tomado' if self.service_type else r'\prestado'
        try:
            with open(SYS_PATH + service_str_path + fr'\{self.client_fed_id}.txt', 'r') as fin:
                text = fin.read()
                text = text.replace('CLIENT_CODE', f'{self.client_code}')
                text = text.replace('MONTH', str(self.month - 2))
                text = text.replace('CURRENT_DATE', self.current_date)
        except Exception as e:
            print(e)
            return ''

        return text

    @staticmethod
    def create_delete_commands(min_launch_key, min_withheld_key):
        commands = f'DELETE FROM LCTOFISSAI WHERE CODIGOEMPRESA = 641 AND CHAVELCTOFISSAI >= {min_launch_key};\n' \
                  f'DELETE FROM LCTOFISSAICFOP WHERE CODIGOEMPRESA = 641 AND CHAVELCTOFISSAI >= {min_launch_key};\n' \
                  f'DELETE FROM LCTOFISSAIRETIDO WHERE CODIGOEMPRESA = 641 AND ' \
                   f'CHAVELCTOFISSAI >= {min_withheld_key};\n' \
                  f'DELETE FROM LCTOFISSAIVALORISS WHERE CODIGOEMPRESA = 641 AND CHAVELCTOFISSAI >= {min_launch_key};'

        with open(SYS_PATH + r'\delete_commands.txt', 'w') as fout:
            print(commands, file=fout)
