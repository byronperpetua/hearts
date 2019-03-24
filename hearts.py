from Client import Client
from GUI import GUI
import os
import sys
from threading import Thread

def main():
    client = Client()
    gui = GUI(client)
    gui.start()


if __name__ == '__main__':
    main()
