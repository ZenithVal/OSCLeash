from asyncore import dispatcher
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

# Source Path
def resource_path(relative_path):
    """Gets absolute path from relative path"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Load Config
config = json.load(open(os.path.join(os.path.join(resource_path('config.json')))))
IP = config["IP"]
ListeningPort = config["ListeningPort"]
SendingPort = config["SendingPort"]
RunDeadzone = config["WalkDeadzone"]
WalkDeadzone = config["WalkDeadzone"]

# Console Clear
def cls():
    """Clears Console"""
    os.system('cls' if os.name == 'nt' else 'clear')

cls() #Comment this out if stuff breaks lmao
print("OSCLeash is Running! Good luck!")
if IP == "127.0.0.1":
    print("IP: Localhost")
else:  
    print("IP: Not Localhost, wtf?")
print("Listening on...", ListeningPort)
print("Sending on...", SendingPort)

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
        case "Leash_Z-":
            leash.Z_Negative=value
        case "Leash_X+":
            leash.X_Positive=value
        case "Leash_X-":
            leash.X_Negative=value          
    #print(f"{parameter}: {value}") #This Prints every input
    statelock.release()

# Paramaters to read
dispatcher.map("/avatar/parameters/Leash_Z+",OnRecieve) #Z Positive
dispatcher.map("/avatar/parameters/Leash_Z-",OnRecieve) #Z Negative
dispatcher.map("/avatar/parameters/Leash_X+",OnRecieve) #X Positive
dispatcher.map("/avatar/parameters/Leash_X-",OnRecieve) #X Negative
dispatcher.map("/avatar/parameters/Leash_Stretch",OnRecieve) #Physbone Stretch Value
dispatcher.map("/avatar/parameters/Leash_IsGrabbed",OnRecieve) #Physbone Grab Status
#dispatcher.set_default_handler(OnRecieve) #This recieves everything, I think?

# Set up UDP OSC client   
oscClient = SimpleUDPClient(IP, SendingPort) 
def StartServer():
    server = BlockingOSCUDPServer((IP,ListeningPort),dispatcher)
    server.serve_forever()

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
        time.sleep(0.3)
        LeashOutput(0.0,0.0,0) #Double output, just in case.
    else:
        time.sleep(0.5) #Add 600ms when not grabbed; save on performance?

    #Wait 100ms, edge of human reaction time, probably?
    Timer(0.1,LeashRun).start()

# Output OSC
def LeashOutput(VerticalOutput:float,HorizontalOutput:float,RunOutput):
    oscClient.send_message("/input/Vertical", VerticalOutput)
    oscClient.send_message("/input/Horizontal", HorizontalOutput)
    oscClient.send_message("/input/Run", RunOutput)
    print("",VerticalOutput,"&",HorizontalOutput,"&",RunOutput)

thread=Thread(target=StartServer)
thread.start()
LeashRun()
LeashOutput(0.0,0.0,0)
