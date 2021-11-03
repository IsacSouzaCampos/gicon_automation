from Model.constants import SYS_PATH


class CNAE:
    def __init__(self, code, description):
        self.code = code
        self.description = description
        self.full_code = self.gen_full_code()

    def gen_full_code(self):
        with open(fr'{SYS_PATH}\cnae.csv', 'r') as fin:
            for line in fin.readlines():
                values = line.split(',')
                if self.code == values[0]:
                    v = values[1].replace('\n', '')
                    return (self.code + v) if len(v) == 4 else (self.code + '0' + v)
