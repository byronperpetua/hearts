from HeartsGUI import HeartsGUI
from Client import Client
from Server import SimpleServer
from threading import Thread

def main():
    client = Client()
    server = SimpleServer()
    gui = HeartsGUI(client)
    client.connect_to_host(None, '67.249.80.138')
    server.setup()
    Thread(target=client.loop, args=(gui,)).start()
    Thread(target=server.test_send).start()
    gui.start()


if __name__ == '__main__':
    main()
