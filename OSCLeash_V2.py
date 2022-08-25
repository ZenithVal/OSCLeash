from asyncore import dispatcher
from threading import Lock,Thread,Timer
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from dataclasses import dataclass
import os
import ctypes

#test objects
from DataController import ConfigSettings, Leash
from PackageManager import Package

# Set window name on the Window
def setWindowTitle():
    if os.name == 'nt':
        os.system("OSCLeash")

    # if os.name == 'nt':
    #     ctypes.windll.kernel32.SetConsoleTitleW("OSCLeash")

# Console Clear
def cls():
    """Clears Console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    
    setWindowTitle()
    cls()

    print("\n-------------------Main function-------------------\n")
    settings = ConfigSettings("Config.json")

    # Settings confirmation
    #settings.printInfo()

    leash = Leash("Config.json")
    print(leash.configParameters)
    
    



main()
