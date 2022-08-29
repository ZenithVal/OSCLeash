from pythonosc.udp_client import SimpleUDPClient
from threading import Thread
import json
import os
import time

from Controllers.DataController import DefaultConfig, ConfigSettings, Leash
from Controllers.PackageController import Package
from Controllers.ThreadController import Program

def createDefaultConfigFile(configPath): # Creates a default config
    try:
        with open("config.json", "w") as cf:
            json.dump(DefaultConfig, cf)

        print("Default config file created")
        time.sleep(3)

    except Exception as e:
        print(e)
        exit()

if __name__ == "__main__":

    #*************Setup*************#
    program = Program()
    program.setWindowTitle()
    program.cls()

    # Test if Config file exists. Create the default if it does not.
    configRelativePath = "./config.json"
    if not os.path.exists(configRelativePath):
        print("Config file was not found...", "\nCreating default config file...")
        createDefaultConfigFile(configRelativePath)
    else:
        print("Config file found\n")

    configData = json.load(open(configRelativePath)) # Config file should be prepared at this point.
    settings = ConfigSettings(configData) # Get settings from config file
    
    # Collect Data for leash
    
    # TODO: Only currently works for one leash (Prepped for more)
    # Notes: There is only one source of contacts for all Leashes. This means
    #   that the pull result is dependent on the FIRST leash pulled. In a 
    #   case that multiple are pulled, pick one that is in control.
    
    leashes = [] 
    for leashName in configData["PhysboneParameters"]:
        leashes.append(Leash(leashName, configData["DirectionalParamaters"], settings))

    # Manage data coming in
    package = Package()

    for leash in leashes:
        package.listen(leash)

    serverThread = Thread(target=package.runServer, args=(settings.IP, settings.ListeningPort))
    serverThread.start()
    time.sleep(.1)

    if serverThread.is_alive():
        Thread(target=program.leashRun, args=(leashes[0],)).start()
    
    time.sleep(10)