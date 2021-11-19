import Model.initiate as initiate
from Control.controller import Controller


class Main:
    @staticmethod
    def main():
        initiate.init()
        while True:
            Controller().run()


if __name__ == '__main__':
    Main().main()
