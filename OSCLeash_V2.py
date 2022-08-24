from asyncore import dispatcher
from threading import Lock,Thread,Timer
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from dataclasses import dataclass
import DataController
import os
import ctypes

# Set window name on the Window
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW("OSCLeash")

# Console Clear
def cls():
    """Clears Console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("\n-------------------Main function-------------------\n")
    Settings = DataController.ConfigSettings("Config.json")

    # Settings confirmation
    Settings.printValues()

main()