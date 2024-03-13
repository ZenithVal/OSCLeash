from threading import Thread
import json
import sys
import os
import time

from Controllers.DataController import DefaultConfig, ConfigSettings, Leash
from Controllers.PackageController import Package
from Controllers.ThreadController import Program

def createDefaultConfigFile(configPath): # Creates a default config
    try:
        with open(configPath, "w") as cf:
            json.dump(DefaultConfig, cf, indent=4)

        print("Default config file created\n")
        time.sleep(2)

    except Exception as e:
        print(e)
        os.system("pause")
        exit()


if __name__ == "__main__":

    #*************Setup*************#
    program = Program()
    program.setWindowTitle()
    program.cls()

    # Make sure to change this to the correct version number on releases.
    print('\x1b[1;32;40m' + "OSCLeash v2.1.3" + '\x1b[0m')

    # Test if Config file exists. Create the default if it does not.
    configRelativePath = "./Config.json"
    if not os.path.exists(configRelativePath):
        # print error message in red
        print('\x1b[1;31;40m' + "Config file was not found...", "\nCreating default config file..." + '\x1b[0m')
        createDefaultConfigFile(configRelativePath)
    else:
        print("Config file found\n")

    # load settings
    try:
        configData = json.load(open(configRelativePath))
    except Exception as e:
        print('\x1b[1;31;40m' + 'Malformed Config.json file. Fix or delete it to generate a new one.' + '\x1b[0m')
        print(f"{e}\nDefault Config will be loaded.\n")

        configData = DefaultConfig
        os.system("pause")
        
    settings = ConfigSettings(configData)

    time.sleep(1)

    # TODO: Remove Xbox support if not needed
    if settings.XboxJoystickMovement:
        try:
            import vgamepad as vg
            settings.addGamepadControls(vg.VX360Gamepad(), vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER) # Add emulated gamepad
        except Exception as e:
            print('\x1b[1;31;40m' + f'Error: {e}\nWarning: Switching to default OSC settings. Please wait...\n Check documentation for controller emulator tool.' + '\x1b[0m')
            settings.XboxJoystickMovement = False
            os.system("pause")

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
            print("Started, awaiting input...")
            Thread(target=program.leashRun, args=(leashes[0],)).start()
        else: raise Exception()
            
    except Exception as e:
        print(e)
        os.system("pause")
        os.execl(sys.executable, sys.executable, *sys.argv)