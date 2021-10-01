class Company:
    def __init__(self, cnpj, name, city=None, code=None):
        self.cnpj = cnpj
        self.name = name

        self.city = 'Florianópolis' if city.lower() == 'florianopolis' else city

        self.code = code
