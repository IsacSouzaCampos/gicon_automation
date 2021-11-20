class Company:
    def __init__(self, fed_id, name, city=None, code=None):
        self.fed_id = fed_id
        self.name = name

        self.city = 'Florianópolis' if city.lower() == 'florianopolis' else city

        self.code = code

    def set_code(self, code):
        self.code = code
