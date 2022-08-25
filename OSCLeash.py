from asyncore import dispatcher
from inspect import Parameter
from threading import Lock,Thread,Timer
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from dataclasses import dataclass
import json
import os
import sys
import ctypes
import time

# Set window name on the Window
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW("OSCLeash")

# Console Clear
def cls():
    """Clears Console"""
    os.system('cls' if os.name == 'nt' else 'clear')

# Source Path
# def resource_path(relative_path):
#     """Gets absolute path from relative path"""
#     base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
#     return os.path.join(base_path, relative_path)

#Load Config
try:
    config = json.load(open('Config.json'))
    
    IP = config["IP"]
    ListeningPort = config["ListeningPort"]
    SendingPort = config["SendingPort"]
    RunDeadzone = config["RunDeadzone"]
    WalkDeadzone = config["WalkDeadzone"]
    StrengthMultiplier = config["StrengthMultiplier"]
    ActiveDelay = config["ActiveDelay"]
    InactiveDelay = config["InactiveDelay"]
    Logging = config["Logging"]
    XboxJoystickMovement = config["XboxJoystickMovement"]
    cls()
    print("Successfully read config.")
except Exception as e: 
    cls()
    print('\x1b[1;31;40m' + 'Missing or incorrect config file. Loading default values.  ' + '\x1b[0m')
    print(e,"was the exception")
    IP = "127.0.0.1"
    ListeningPort = 9001
    SendingPort = 9000
    RunDeadzone = 0.70
    WalkDeadzone = 0.15
    StrengthMultiplier = 1.2    
    ActiveDelay = .1
    InactiveDelay = .5
    Logging = True
    XboxJoystickMovement = False

# Settings confirmation
print('\x1b[1;32;40m' + 'OSCLeash is Running!' + '\x1b[0m')
if IP == "127.0.0.1":
    print("IP: Localhost")
else:  
    print("IP: Not Localhost? Wack.")
print("Listening on port", ListeningPort)
print("Sending on port",SendingPort)
print("Running Deadzone of {:.0f}".format(RunDeadzone*100)+"% stretch")
print("Walking Deadzone of {:.0f}".format(WalkDeadzone*100)+"% stretch")
print("Delays of {:.0f}".format(ActiveDelay*1000),"& {:.0f}".format(InactiveDelay*1000),"ms")
#print("Inactive delay of {:.0f}".format(InactiveDelay*1000),"ms")
if XboxJoystickMovement:
    try:
        import vgamepad as vg
        gamepad = vg.VX360Gamepad()
        print("Emulating Xbox 360 Controller for input instead of OSC")
    except Exception as e:
        print(e)
        print('\x1b[1;31;40m' + 'Tool required for controller emulation not installed. Check the docs.' + '\x1b[0m') 

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

#Recieve paramaters and adjust values
def OnRecieve(address,value):
    parameter = address.split("/")[3]
    statelock.acquire()
    match parameter:
        case "Leash_IsGrabbed":
            leash.LeashGrabbed=value
        case "Leash_Stretch":
            leash.LeashStretch=value
        case "Leash_Z+":
            leash.Z_Positive=value
            print("this worked")
        case "Leash_Z-":
            leash.Z_Negative=value
        case "Leash_X+":
            leash.X_Positive=value
        case "Leash_X-":
            leash.X_Negative=value          
    #print(f"{parameter}: {value}") #This Prints every input
    statelock.release() 

# # Paramaters to read
# dispatcher.map("/avatar/parameters/Leash_Z+",OnRecieve) #Z Positive
# dispatcher.map("/avatar/parameters/Leash_Z-",OnRecieve) #Z Negative
# dispatcher.map("/avatar/parameters/Leash_X+",OnRecieve) #X Positive
# dispatcher.map("/avatar/parameters/Leash_X-",OnRecieve) #X Negative
# dispatcher.map("/avatar/parameters/Leash_Stretch",OnRecieve) #Physbone Stretch Value
# dispatcher.map("/avatar/parameters/Leash_IsGrabbed",OnRecieve) #Physbone Grab Status
# #dispatcher.set_default_handler(OnRecieve) #This recieves everything, I think?

#------------------------Testing area------------------------#


ParaConfig = config["Parameters"]

dispatcher.map("/avatar/parameters", OnRecieve) #Testing to see if value returns the same based shortened address

# Paramaters to read
# dispatcher.map(ParaConfig["Z_Positive_Param"], OnRecieve) #Z Positive
# dispatcher.map(ParaConfig["Z_Negative_Param"], OnRecieve) #Z Negative
# dispatcher.map(ParaConfig["X_Positive_Param"], OnRecieve) #X Positive
# dispatcher.map(ParaConfig["X_Negative_Param"], OnRecieve) #X Negative
# dispatcher.map(ParaConfig["LeashStretch_Param"], OnRecieve) #Physbone Stretch Value
# dispatcher.map(ParaConfig["LeashGrab_Param"], OnRecieve) #Physbone Grab Status
#dispatcher.set_default_handler(OnRecieve) #This recieves everything, I think?

#------------------------Testing area------------------------#

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

#clamp float values between -1 and 1
def clamp (n):
    return max(-1.0, min(n, 1.0))

# Run Leash
def LeashRun():
    statelock.acquire()

    #Maths 
    VerticalOutput = clamp((leash.Z_Positive-leash.Z_Negative) * leash.LeashStretch * StrengthMultiplier)
    HorizontalOutput = clamp((leash.X_Positive-leash.X_Negative) * leash.LeashStretch * StrengthMultiplier)

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
    if XboxJoystickMovement: #Xbox Emulation: REMOVE LATER WHEN OSC IS FIXED
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