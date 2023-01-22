from threading import Thread
import threading
import json
import os
import time
from queue import LifoQueue
from queue import SimpleQueue
from Controllers.DataController import DefaultConfig, AppManifest, ConfigSettings, Leash
from Controllers.PackageController import Package
from Controllers.ThreadController import Program
from OSCLeashGUI import App
from pprint import pprint

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

#*************Setup*************#

program = Program(do_print=False)

# Test if Config file exists. Create the default if it does not.
configRelativePath = "./config.json"
if not os.path.exists(configRelativePath):
    print("Config file was not found...", "\nCreating default config file...")
    createDefaultConfigFile(configRelativePath)
else:
    print("Config file found\n")

configData = json.load(open(configRelativePath)) # Config file should be prepared at this point.
settings = ConfigSettings(configData) # Get settings from config file

def setup_xbox_movement():
    # Add controller input if user installs vgampad
    if settings.XboxJoystickMovement:
        try:
            import vgamepad as vg
            settings.addGamepadControls(vg.VX360Gamepad(), vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER) # Add emulated gamepad
        except Exception as e:
            print('\x1b[1;31;40m' + f'Error: {e}\nWarning: Switching to default OSC settings. Please wait...\n Check documentation for controller emulator tool.' + '\x1b[0m')
            settings.XboxJoystickMovement = False
            time.sleep(7)

def setup_openvr():
    # Import openvr if user wants to autostart the app with SteamVR
    if settings.AutoStartSteamVR:
        try:
            import openvr
            vr = openvr.init(openvr.VRApplication_Utility)
            # Create an IVRApplications object
            applications = openvr.IVRApplications()

            # Save AppManifest to manifest.vrmanifest
            with open("./manifest.vrmanifest", "w") as f:
                f.write(json.dumps(AppManifest))
            
            # Register the manifest file's absolute path with SteamVR
            manifest_path = os.path.abspath("./manifest.vrmanifest")
            error = openvr.EVRFirmwareError()
            applications.addApplicationManifest(manifest_path, False)
            #applications.removeApplicationManifest(manifest_path)
            if error.value != 0:
                print("Error adding manifest: ", error)
            else:
                print("Manifest added successfully")
                
            # Listen for the event that SteamVR is shutting down
            # This is a blocking call, so it will wait here until SteamVR shuts down
            #event = openvr.VREvent_t()
            #while True:
            #    if vr.pollNextEvent(event):
            #        if event.eventType == openvr.VREvent_Quit:
            #            break

            
        except openvr.error_code.ApplicationError_InvalidManifest as e:
            print('\x1b[1;31;40m' + f'Error: {e}\nWarning: Was not able to import openvr!' + '\x1b[0m')
            time.sleep(7)

def queue_reader(queue):
    while True:
        if queue.qsize() > 0:
            item = queue.get()
            print(item)
            print(queue.qsize())
            queue.task_done()
        else:
            time.sleep(.1)

# gui

app = App()
    

# Collect Data for leash
leash_queue = LifoQueue()
exception_queue = SimpleQueue()
leashes = []
for leashName in configData["PhysboneParameters"]:
    leashes.append(Leash(leashName, configData["DirectionalParameters"], settings))

try:
    # Manage data coming in
    if len(leashes) == 0: raise Exception("No leashes found. Please update config file.")
    package = Package(leashes, leash_queue)
    package.listen()

    # Start server
    serverThread = Thread(target=package.runServer, args=(settings.IP, settings.ListeningPort))
    serverThread.start()
    time.sleep(1)

    # Check if the server thread died
    serverThreadAlive = False
    for thread in threading.enumerate():
        if "runServer" in str(thread.name):
            serverThreadAlive = True
            break
    if not serverThreadAlive:
        raise ConnectionError("OSC Listener died. Please check your IP and port settings.")

    setup_xbox_movement()
    setup_openvr()

    guiThread = Thread(target=app.run, args=(leash_queue, exception_queue))
    guiThread.start()
        

    while True:
        time.sleep(.5)
        if exception_queue.qsize() > 0:
            item = exception_queue.get()
            if item == 'exit':
                raise SystemExit
        

except (KeyboardInterrupt, SystemExit, ConnectionError):
    print('Exiting...')

    os.kill(os.getpid(), 9) # Stupid and janky way to kill the program, but at least it works.    
    
except Exception as e:
    print(e)
    time.sleep(10)