from pythonosc.udp_client import SimpleUDPClient
from threading import Lock, Thread
import time
import os
import ctypes #Required for colored error messages.

from Controllers.DataController import ConfigSettings, Leash

class Program:

    # Class variable to determine if the program is running on a thread (Prevents multiple threads)
    __running = False 

    def resetProgram(self):
        Program.__running = False 
    
    def updateProgram(self, runBool:bool, countValue:int):
        Program.__running = runBool

    def leashRun(self, leash: Leash, counter:int = 0):

        if counter == 0 and Program.__running or not leash.Active:
            return
        
        if counter < 0: # Prevents int overflow possibility by resetting counter at continuation state
            counter = 1
        
        statelock = Lock()
        statelock.acquire()

        if not leash.settings.Logging:
            self.cls()
            print("Current Status:")

        # leash.settings.printInfo() 
        # Lets not print this every time, it actually costs performance.
            
        if leash.settings.Logging:
            leash.printDirections()

        #Movement Math
        outputMultiplier = leash.Stretch * leash.settings.StrengthMultiplier
        VerticalOutput = self.clamp((leash.Z_Positive - leash.Z_Negative) * outputMultiplier)
        HorizontalOutput = self.clamp((leash.X_Positive - leash.X_Negative) * outputMultiplier)

        #Up/Down Deadzone, stops movement if pulled too high or low.
        if (leash.Y_Positive + leash.Y_Negative) > leash.settings.UpDownDeadzone:
            VerticalOutput = 0
            HorizontalOutput = 0

        #Up/Down Compensation
        elif leash.settings.UpDownCompensation != 0:
            Y_Modifier = self.clamp(1.0 - ((leash.Y_Positive + leash.Y_Negative) * leash.settings.UpDownCompensation))
            VerticalOutput /= Y_Modifier
            HorizontalOutput /= Y_Modifier
            # This is not linear... I don't know, I think I might've failed math.

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
        if leash.Grabbed: 
            self.updateProgram(True, counter)

            if leash.wasGrabbed == False:
                leash.wasGrabbed = True
                print("{} grabbed".format(leash.Name))

            if leash.Stretch > leash.settings.RunDeadzone: #Running
                self.leashOutput(VerticalOutput, HorizontalOutput, TurningSpeed, 1, leash.settings)
            elif leash.Stretch > leash.settings.WalkDeadzone: #Walking
                self.leashOutput(VerticalOutput, HorizontalOutput, TurningSpeed, 0, leash.settings)
            else: #Not stretched enough to move.
                self.leashOutput(0.0, 0.0, 0.0, 0, leash.settings)
            
            time.sleep(leash.settings.ActiveDelay)
            Thread(target=self.leashRun, args=(leash, counter+1)).start()

        elif leash.Grabbed != leash.wasGrabbed:
            print("{} dropped".format(leash.Name))

            leash.Active = False
            leash.resetMovement()
            self.leashOutput(0.0, 0.0, 0.0, 0, leash.settings)

            leash.wasGrabbed = False

            time.sleep(2)
            self.resetProgram()
        
        else: # Only used at the start
            print("Waiting...")

            leash.Active = False
            self.leashOutput(0.0, 0.0, 0.0, 0, leash.settings)
            self.resetProgram()

            time.sleep(leash.settings.InactiveDelay)

        statelock.release()

    def leashOutput(self, vert: float, hori: float, turn: float, runType: bool, settings: ConfigSettings):

        oscClient = SimpleUDPClient(settings.IP, settings.SendingPort)

        #TODO: Remove this one day.
        if settings.XboxJoystickMovement: 
            settings.gamepad.left_joystick_float(x_value_float=float(hori), y_value_float=float(vert))
            if settings.TurningEnabled: 
                settings.gamepad.right_joystick_float(x_value_float=float(turn), y_value_float=0.0)
            if runType == 1:
                settings.gamepad.press_button(button=settings.runButton)      
            else:
                settings.gamepad.release_button(button=settings.runButton)
            settings.gamepad.update()

        else:
            oscClient.send_message("/input/Vertical", vert)
            oscClient.send_message("/input/Horizontal", hori)
            if settings.TurningEnabled: 
                oscClient.send_message("/input/LookHorizontal", turn)
            oscClient.send_message("/input/Run", runType)

        
        print(f"\tVert: {vert} | Hori: {hori} | Run: {runType}") 
        if settings.TurningEnabled: print(f"\tTurn: {turn}")

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
            ctypes.windll.kernel32.SetConsoleTitleW("OSCLeash")
    
