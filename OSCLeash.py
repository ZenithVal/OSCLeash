from asyncore import dispatcher
from threading import Lock,Thread,Timer
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from dataclasses import dataclass
import vgamepad as vg
import json
import os
import sys
import ctypes
import time

# Default config
DefaultConfig = {
    "IP" : "127.0.0.1",
    "ListeningPort" : 9001,
    "SendingPort" : 9000,
    "RunDeadzone" : 0.70,
    "WalkDeadzone" : 0.15,
    "ActiveDelay" : 0.1,
    "InactiveDelay" : 0.5,
    "Logging" : False,
    "XboxJoystickMovement" : False,
    "Parameters" : {
        "Z_Positive": "Leash_Z+",
        "Z_Negative": "Leash_Z-",
        "X_Positive": "Leash_X+",
        "X_Negative": "Leash_X-",
        "ContactParameter" : "Leash"
    }
}

# Set window name on the Window
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW("OSCLeash")

# Console Clear
def cls():
    """Clears Console"""
    os.system('cls' if os.name == 'nt' else 'clear')

# Source Path
def resource_path(relative_path):
    """Gets absolute path from relative path"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

#Load Config
try:
    configPath = os.path.join(os.path.join(resource_path('config.json')))
    if not os.path.isfile('config.json'):
        print('\x1b[1;31;40m' + 'Config missing. Creating...  ' + '\x1b[0m')
        with open('config.json', 'w') as outfile:
            json.dump(DefaultConfig, outfile, indent = 4)

    config = json.load(open(configPath))
    IP = config["IP"]
    ListeningPort = config["ListeningPort"]
    SendingPort = config["SendingPort"]
    RunDeadzone = config["RunDeadzone"]
    WalkDeadzone = config["WalkDeadzone"]
    ActiveDelay = config["ActiveDelay"]
    InactiveDelay = config["InactiveDelay"]
    Logging = config["Logging"]
    Parameters = config["Parameters"]
    XboxJoystickMovement = config["XboxJoystickMovement"]
    cls()
    print("Successfully read config.")
except Exception as e: 
    cls()
    print('\x1b[1;31;40m' + 'Missing or incorrect config file. Loading default values.  ' + '\x1b[0m')
    print('\x1b[1;31;40m' + 'Delete the config file for a new one to be generated.  ' + '\x1b[0m')
    print(e,"was the exception")
    IP = "127.0.0.1"
    ListeningPort = 9001
    SendingPort = 9000
    RunDeadzone = 0.70
    WalkDeadzone = 0.15
    ActiveDelay = .1
    InactiveDelay = .5
    Logging = False
    XboxJoystickMovement = False
    Parameters = {
        "Z_Positive": "Leash_Z+",
        "Z_Negative": "Leash_Z-",
        "X_Positive": "Leash_X+",
        "X_Negative": "Leash_X-",
        "ContactParameter": "Leash"
    }

# Settings confirmation
print('\x1b[1;32;40m' + 'OSCLeash is Running!' + '\x1b[0m')
if IP == "127.0.0.1":
    print("IP: Localhost")
else:  
    print("IP: Not Localhost? Wack.")
print("Listening on port", ListeningPort)
print("Sending on port",SendingPort)
print("Run Deadzone of {:.0f}".format(RunDeadzone*100)+"% stretch")
print("Walking Deadzone of {:.0f}".format(WalkDeadzone*100)+"% stretch")
print("Delays of {:.0f}".format(ActiveDelay*1000),"& {:.0f}".format(InactiveDelay*1000),"ms")
#print("Inactive delay of {:.0f}".format(InactiveDelay*1000),"ms")
if XboxJoystickMovement:
    gamepad = vg.VX360Gamepad()
    print("Emulating Xbox 360 Controller for input instead of OSC")

@dataclass
class LeashParameters:
    LeashWasGrabbed: bool = False
    LeashGrabbed: bool = False
    LeashStretch: float = 0
    Z_Positive: float = 0
    Z_Negative: float = 0
    X_Positive: float = 0
    X_Negative: float = 0

leash = LeashParameters()

statelock = Lock()
dispatcher = Dispatcher()

def OnReceive_ZPositive(address, value):
    statelock.acquire()
    leash.Z_Positive = value
    statelock.release()
    
def OnReceiver_ZNegative(address, value):
    statelock.acquire()
    leash.Z_Negative = value
    statelock.release()
    
def OnReceive_XPositive(address, value):
    statelock.acquire()
    leash.X_Positive = value
    statelock.release()
    
def OnReceiver_XNegative(address, value):
    statelock.acquire()
    leash.X_Negative = value
    statelock.release()
    
def OnReceiver_IsGrabbed(address, value):
    statelock.acquire()
    leash.LeashGrabbed = value
    statelock.release()
    
def OnReceiver_Stretch(address, value):
    statelock.acquire()
    leash.LeashStretch = value
    statelock.release()

# Paramaters to read
dispatcher.map(f'/avatar/parameters/{Parameters["Z_Positive"]}',OnReceive_ZPositive) #Z Positive
dispatcher.map(f'/avatar/parameters/{Parameters["Z_Negative"]}',OnReceiver_ZNegative) #Z Negative
dispatcher.map(f'/avatar/parameters/{Parameters["X_Positive"]}',OnReceive_XPositive) #X Positive
dispatcher.map(f'/avatar/parameters/{Parameters["X_Negative"]}',OnReceiver_XNegative) #X Negative
dispatcher.map(f'/avatar/parameters/{Parameters["ContactParameter"]}_Stretch',OnReceiver_Stretch) #Physbone Stretch Value
dispatcher.map(f'/avatar/parameters/{Parameters["ContactParameter"]}_IsGrabbed',OnReceiver_IsGrabbed) #Physbone Grab Status
#dispatcher.set_default_handler(OnRecieve) #This recieves everything, I think?

# Set up UDP OSC client   
oscClient = SimpleUDPClient(IP, SendingPort) 
def StartServer():
    try:
        server = BlockingOSCUDPServer((IP,ListeningPort),dispatcher)
        server.serve_forever()
    except:
        print('\x1b[1;31;41m' + '                                                            ' + '\x1b[0m')
        print('\x1b[1;31;40m' + '  Warning: An application is already running on this port!  ' + '\x1b[0m')
        print('\x1b[1;31;41m' + '                                                            ' + '\x1b[0m')

# Run Leash
def LeashRun():
    statelock.acquire()

    #Maths 
    VerticalOutput = (leash.Z_Positive-leash.Z_Negative) * leash.LeashStretch
    HorizontalOutput = (leash.X_Positive-leash.X_Negative) * leash.LeashStretch

    #Read Grab state
    LeashGrabbed = leash.LeashGrabbed

    if LeashGrabbed == True: #Leash is grabbed
        leash.LeashWasGrabbed = True #Has been grabbed 

    LeashReleased = leash.LeashGrabbed != leash.LeashWasGrabbed #Do Leash Grab states line up?
    if LeashReleased == True: #Reset Leash grab state
        leash.LeashWasGrabbed = False
    
    statelock.release()

    if LeashGrabbed == True: #GrabCheck
        if leash.LeashStretch > RunDeadzone: #Running deadzone
            LeashOutput(VerticalOutput,HorizontalOutput,1)
        elif leash.LeashStretch > WalkDeadzone: #Walking deadzone
            LeashOutput(VerticalOutput,HorizontalOutput,0)
        else: #Not stretched enough to move.
            LeashOutput(0.0,0.0,0)
    elif LeashReleased == True: #Leash was Dropped, send stop movement.
        LeashReleased = False
        LeashOutput(0.0,0.0,0)
        time.sleep(InactiveDelay)
        LeashOutput(0.0,0.0,0) #Double output, just in case.
    else:
        time.sleep(InactiveDelay) #Add 500ms when not grabbed; save on performance?

    #Wait 100ms, edge of human reaction time, probably?
    Timer(ActiveDelay,LeashRun).start()

# Output OSC
def LeashOutput(VerticalOutput:float,HorizontalOutput:float,RunOutput):
    if XboxJoystickMovement: #Xbox Emulation REMOVE LATER WHEN OSC IS FIXED
        gamepad.left_joystick_float(x_value_float=HorizontalOutput, y_value_float=VerticalOutput)
        if RunOutput == 1:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        else:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        gamepad.update()
    else: #Normal function
        oscClient.send_message("/input/Vertical", VerticalOutput)
        oscClient.send_message("/input/Horizontal", HorizontalOutput)
        oscClient.send_message("/input/Run", RunOutput)

    if Logging:
        print(
        "{:.2f}".format(VerticalOutput),"&",
        "{:.2f}".format(HorizontalOutput),"&",
        RunOutput)
        #print("",VerticalOutput,"&",HorizontalOutput,"&",RunOutput) #Way too many decimale places debug

thread=Thread(target=StartServer)
thread.start()
LeashRun()
LeashOutput(0.0,0.0,0)
