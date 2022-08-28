from cProfile import run
from DataController import DefaultConfig, ConfigSettings, Leash
from PackageManager import Package
from pythonosc.udp_client import SimpleUDPClient
from threading import Lock,Thread
import json
import os
import time

def setWindowTitle(): # Set window name on the Window
    if os.name == 'nt':
        os.system("OSCLeash")


def cls(): # Console Clear
    """Clears Console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def createDefaultConfigFile(configPath): # Creates a default config
    try:
        with open("config.json", "w") as cf:
            json.dump(DefaultConfig, cf)

        print("Default config file created")

    except Exception as e:
        print(e)
        exit()

def leashRun(leash: Leash): # TODO: make work for one leash

    cls()
    leash.settings.printInfo()
    print("\nCurrent Status:\n")

    statelock = Lock()
    
    statelock.acquire()

    #Movement
    VerticalOutput = (leash.Z_Positive - leash.Z_Negative) * leash.Stretch * leash.settings.StrengthMultiplier
    HorizontalOutput = (leash.X_Positive - leash.X_Negative) * leash.Stretch * leash.settings.StrengthMultiplier

    #Grab state
    LeashGrabbed = leash.Grabbed
    LeashReleased = leash.Grabbed != leash.wasGrabbed #Do Leash Grab states line up?

    if leash.Grabbed: #Leash is grabbed

        if leash.wasGrabbed == False:
            leash.wasGrabbed = True
            print("Leash recently grabbed")
        else:
            print("Leash is grabbed")

        if leash.Stretch > leash.settings.RunDeadzone: #Running deadzone
            leashOutput(VerticalOutput, HorizontalOutput, True, leash.settings)
        elif leash.Stretch > leash.settings.WalkDeadzone: #Walking deadzone
            leashOutput(VerticalOutput, HorizontalOutput, False, leash.settings)
        else: #Not stretched enough to move.
            leashOutput(0.0, 0.0, 0, leash.settings)
        
        time.sleep(leash.settings.ActiveDelay)
        Thread(target=leashRun, args=(leash,)).start()# Run thread if still grabbed
     
    elif leash.Grabbed != leash.wasGrabbed:
        print("Leash has been released")
        leash.wasGrabbed = False
        leash.resetMovement()
        leashOutput(0.0, 0.0, 0, leash.settings)
        time.sleep(leash.settings.InactiveDelay)
        Thread(target=leashRun, args=(leash,)).start() #temp test
    
    else:
        print("Waiting...")
        time.sleep(leash.settings.InactiveDelay)
        Thread(target=leashRun, args=(leash,)).start() #temp test

    statelock.release()

def leashOutput(vert: float, hori: float, runType: int, settings: ConfigSettings):

    oscClient = SimpleUDPClient(settings.IP, settings.SendingPort)

    #Xbox Emulation: REMOVE LATER WHEN OSC IS FIXED
    if settings.XboxJoystickMovement:
        print("\nSending through Emulated controller input\n")
        try:
            import vgamepad as vg
            gamepad = vg.VX360Gamepad()
            print("Emulating Xbox 360 Controller for input instead of OSC")

            gamepad.left_joystick_float(x_value_float=hori, y_value_float=vert)
            if runType == 1:
                gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)      
            else:
                gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            gamepad.update()

        except Exception as e:
            print(e)
            print('\x1b[1;31;40m' + 'Tool required for controller emulation not installed. Please check the documentation.' + '\x1b[0m') 
            exit()

    else:
        #Normal function
        print("\nSending through oscClient\n")
        oscClient.send_message("/input/Vertical", vert)
        oscClient.send_message("/input/Horizontal", hori)
        oscClient.send_message("/input/Run", runType) # recommend using bool instead of int if possible

    print("\tVertical: {}\n\tHorizontal: {}\n\tRun: {}".format(vert,hori,runType))
    
if __name__ == "__main__":

    #*************Setup*************#
    setWindowTitle()
    cls()

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

    Thread(target=package.runServer, args=(settings.IP, settings.ListeningPort)).start()
    Thread(target=leashRun, args=(leashes[0],)).start()
    