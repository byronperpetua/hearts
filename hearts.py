from Client import Client
from GUI import GUI

def main():
    client = Client()
    gui = GUI(client)
    gui.start()

if __name__ == '__main__':
    main()
