class ISS:
    def __init__(self, outer):
        self.outer = outer

        self.is_withheld = self.is_withheld()
        self.value = self.outer.data['valorissqn'] if self.is_withheld else ''
        self.aliquot = self.outer.data['aliquota'] if self.is_withheld else 0
        self.calc_basis = self.outer.gross_value if self.is_withheld else 0

    def is_withheld(self):
        """Verifica se há retencao de ISS com base no CFPS e CST"""

        iss_withheld = False
        if self.outer.provider.city.lower() in ['florianopolis', 'florianópolis']:
            if self.outer.cst in ['2', '4', '6', '10']:
                iss_withheld = True

        elif self.outer.cfps in ['9205', '9206'] and self.outer.cst in ['0', '1']:
            iss_withheld = True

        return iss_withheld
