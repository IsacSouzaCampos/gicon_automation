class Company:
    def __init__(self, fed_id, name, city=None, code=None):
        self.fed_id = fed_id
        self.name = name
        self.estab_num = self.fed_id[-6:-2]
        self.is_parent = True if int(self.estab_num) == 1 else False

        self.city = 'Florianópolis' if city.lower() == 'florianopolis' else city

        self.code = code

    def set_code(self, code):
        self.code = code
