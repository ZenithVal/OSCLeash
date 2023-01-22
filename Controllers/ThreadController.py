from pythonosc.udp_client import SimpleUDPClient
from threading import Lock, Thread
import time
import os
from Controllers.DataController import ConfigSettings, Leash
from pprint import pprint
import pygetwindow as gw
import math


class Program:

    # Class variable to determine if the program is running on a thread (Prevents multiple threads)
    __running = False 
    def __init__(self, do_print:bool = False):
        self.do_print = do_print
        self.setWindowTitle()
        # self.cls()
    
    def print(self, *args, **kwargs):
        if self.do_print: 
            print(args, kwargs)
        else:
            pass
        
    def resetProgram(self):
        Program.__running = False 
    
    def updateProgram(self, runBool:bool, countValue:int):
        Program.__running = runBool

    def scaleCurve(self, currentScale, normalScale):
        # magic math i did while high
        vector = [10, 5]
        scale = (currentScale/normalScale) * 0.25
        speed = math.sqrt(vector[0]**2 + vector[1]**2)
        curve = scale / math.log(speed + 1)
        vector[0] *= curve
        vector[1] *= curve
        return vector[0]

    #@timing
    def leashRun(self, leash: Leash, counter:int = 0, out_queue = None):

        if counter == 0 and Program.__running or not leash.Active:
            return
        
        if counter < 0: # Prevents int overflow possibility by resetting counter at continuation state
            counter = 1
        
        statelock = Lock()
        statelock.acquire()
        
        leash.settings.printInfo()
        if leash.settings.Logging:
            leash.printDirections()

        #Quick scaling ratio math
        ScaleRatio = 1
        if leash.settings.ScaleParameter != "" and leash.settings.ScaleSlowdownEnabled:
            ScaleRatio = self.scaleCurve(leash.CurrentScale, leash.settings.ScaleNormal)
            if ScaleRatio == 0 or ScaleRatio < 0:
                ScaleRatio = 0.01
            elif ScaleRatio > 1:
                ScaleRatio = 1

        self.print("Last Scale:")
        scalePercent = round(ScaleRatio*100, 3)
        self.print(str(scalePercent)+"%")
        self.print("\nCurrent Status:\n")

        #Movement Math
        VerticalOutput = self.clamp((leash.Z_Positive - leash.Z_Negative) * leash.Stretch * leash.settings.StrengthMultiplier * ScaleRatio)
        HorizontalOutput = self.clamp((leash.X_Positive - leash.X_Negative) * leash.Stretch * leash.settings.StrengthMultiplier * ScaleRatio)
                
        #Turning Math
        if leash.settings.TurningEnabled and leash.Stretch > leash.settings.TurningDeadzone and leash.Grabbed:
            TurnDirect = None
            match leash.LeashDirection:
                case "North":
                    if leash.Z_Positive < leash.settings.TurningGoal:
                        if leash.X_Positive > leash.X_Negative:
                            TurnDirect = "R"
                        else:
                            TurnDirect = "L"                 
                case "South":
                    if leash.Z_Negative < leash.settings.TurningGoal:
                        if leash.X_Positive > leash.X_Negative:
                            TurnDirect = "L"
                        else:
                            TurnDirect = "R"
                case "East":
                    if leash.X_Positive < leash.settings.TurningGoal:
                        if leash.Z_Positive > leash.Z_Negative:
                            TurnDirect = "L"
                        else:
                            TurnDirect = "R"                
                case "West":
                    if leash.X_Negative < leash.settings.TurningGoal:
                        if leash.Z_Positive > leash.Z_Negative:
                            TurnDirect = "R"
                        else:
                            TurnDirect = "L"

            #Directional Output
            if TurnDirect == "L":
                TurningSpeed = self.clampNeg(-1.0 * ((leash.Stretch - leash.settings.TurningDeadzone) * leash.settings.TurningMultiplier))
            elif TurnDirect == "R":
                TurningSpeed = self.clampPos(1.0 * ((leash.Stretch - leash.settings.TurningDeadzone) * leash.settings.TurningMultiplier))
            else:
                TurningSpeed = 0.0
        else:
            TurningSpeed = 0.0


        #Leash is grabbed
        if leash.Grabbed and leash.Disabled == False: 
            self.updateProgram(True, counter)

            if leash.wasGrabbed == False:
                leash.wasGrabbed = True
                self.print("{} Leash recently grabbed".format(leash.Name))
                
                # Bring VRChat window to Foreground
                if leash.settings.BringGameToFront:
                    windows = gw.getWindowsWithTitle(leash.settings.GameTitle)
                    # Find the window with the exact title
                    for window in windows:
                        if window.title == leash.settings.GameTitle:
                            try:
                                window.activate()
                            except (SyntaxError, gw.PyGetWindowException):
                                self.print("Error: Could not bring {} to front?".format(leash.settings.GameTitle))
                                pass
                            break

            else:
                self.print("{} is grabbed".format(leash.Name))

            if leash.Stretch > leash.settings.RunDeadzone: #Running deadzone
                self.leashOutput(VerticalOutput, HorizontalOutput, TurningSpeed, scalePercent, True, leash, out_queue)
            elif leash.Stretch > leash.settings.WalkDeadzone: #Walking deadzone
                self.leashOutput(VerticalOutput, HorizontalOutput, TurningSpeed, scalePercent, False, leash, out_queue)
            else: #Not stretched enough to move.
                self.leashOutput(0.0, 0.0, 0.0, scalePercent, False, leash, out_queue)
            
            time.sleep(leash.settings.ActiveDelay)
            Thread(target=self.leashRun, args=(leash, counter+1, out_queue)).start()# Run thread if still grabbed
        
        elif leash.Grabbed != leash.wasGrabbed:
            self.print("{} has been released".format(leash.Name))
            leash.Active = False
            leash.resetMovement()
            self.leashOutput(0.0, 0.0, 0.0, scalePercent, False, leash, out_queue)

            leash.wasGrabbed = False

            self.resetProgram()\
            
            time.sleep(leash.settings.InactiveDelay)
        
        else: # Only used at the start
            self.print("Waiting...")

            leash.Active = False
            self.leashOutput(0.0, 0.0, 0.0, scalePercent, False, leash, out_queue)
            self.resetProgram()

            time.sleep(leash.settings.InactiveDelay)

        statelock.release()
    
    def leashOutput(self, vert: float, hori: float, turn: float, scale: float, runType: bool, leash: Leash, out_queue):
        #Output to queue
        settings = leash.settings
        if out_queue != None:
            out_queue.put(item=(leash.Name, vert, hori, turn, scale), block=False)
        
        oscClient = SimpleUDPClient(settings.IP, settings.SendingPort)

        #Xbox Emulation: REMOVE LATER WHEN OSC IS FIXEDpytho
        if settings.XboxJoystickMovement: 
            self.print("\nSending through Emulated controller input\n")
            offset = 1
            settings.gamepad.left_joystick_float(x_value_float=float(hori * offset), y_value_float=float(vert * offset))
            if settings.TurningEnabled: 
                settings.gamepad.right_joystick_float(x_value_float=float(turn * offset), y_value_float=0.0)
            if runType == 1:
                settings.gamepad.press_button(button=settings.runButton)      
            else:
                settings.gamepad.release_button(button=settings.runButton)
            settings.gamepad.update()

        else:
            #Normal OSC outputs  function
            self.print("\nSending through oscClient\n")
            oscClient.send_message("/input/Vertical", vert)
            oscClient.send_message("/input/Horizontal", hori)
            if settings.TurningEnabled: 
                oscClient.send_message("/input/LookHorizontal", turn)
            oscClient.send_message("/input/Run", runType)


        self.print(f"\tVertical: {vert}\n\tHorizontal: {hori}\n\tRun: {runType}")
        if settings.TurningEnabled: self.print(f"\tTurn: {turn}")

    def clamp (self, n):
        return max(-1.0, min(n, 1.0))

    def clampPos (self, n):
        return max(0.0, min(n, 0.99999))

    def clampNeg (self, n):
        return max(-0.99999, min(n, 0.0))

    def cls(self): # Console Clear
        """Clears Console"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def setWindowTitle(self): # Set window title
        if os.name == 'nt':
            os.system("title OSCLeash")
