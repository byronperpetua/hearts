from GUI import GUI
from Client import Client
from threading import Thread


def main():
    client = Client()
    gui = GUI(client)
    gui.start()


if __name__ == '__main__':
    main()
