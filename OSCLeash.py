from threading import Thread
import json
import os
import time

from Controllers.DataController import DefaultConfig, ConfigSettings, Leash
from Controllers.PackageController import Package
from Controllers.ThreadController import Program

def createDefaultConfigFile(configPath): # Creates a default config
    try:
        with open(configPath, "w") as cf:
            json.dump(DefaultConfig, cf)

        print("Default config file created")
        time.sleep(3)

    except Exception as e:
        print(e)
        time.sleep(5)
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

    # Add controller input if user installs vgampad
    if settings.XboxJoystickMovement:
        try:
            import vgamepad as vg
            settings.addGamepadControls(vg.VX360Gamepad(), vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER) # Add emulated gamepad
        except Exception as e:
            print(e)
            time.sleep(5)

    
    # Collect Data for leash

    leashes = []
    for leashName in configData["PhysboneParameters"]:
        leashes.append(Leash(leashName, configData["DirectionalParameters"], settings))

    try:
        # Manage data coming in
        if len(leashes) == 0: raise Exception("No leashes found. Please update config file.")
        package = Package(leashes)
        package.listen()

        # Start server
        serverThread = Thread(target=package.runServer, args=(settings.IP, settings.ListeningPort))
        serverThread.start()
        time.sleep(.1)
        
        #initialize input
        if serverThread.is_alive():
            leashes[0].Active = True
            Thread(target=program.leashRun, args=(leashes[0],)).start()
        else: raise Exception()
            
    except Exception as e:
        print(e)
        time.sleep(10)