from Model.constants import SYS_PATH

from datetime import datetime


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

    def updates_commands(self, min_date, max_date) -> str:
        service_str_path = r'\tomado' if self.service_type else r'\prestado'
        try:
            with open(SYS_PATH + service_str_path + fr'\{self.client_fed_id}.txt', 'r') as fin:
                text = fin.read()
                text = text.replace('CLIENT_CODE', f'{self.client_code}')
                text = text.replace('MIN_DATE', f'{min_date[0]}.{min_date[1]}.{min_date[2]}')
                text = text.replace('MAX_DATE', f'{max_date[0]}.{max_date[1]}.{max_date[2]}')
        except Exception as e:
            print(e)
            return ''

        return text
