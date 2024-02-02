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
            print('\x1b[1;32;40m' + 'OSCLeash is Running' + '\x1b[0m')  
        else:
            leash.printDirections()

        #Movement Math
        outputMultiplier = leash.Stretch * leash.settings.StrengthMultiplier
        VerticalOutput = self.clamp((leash.Z_Positive - leash.Z_Negative) * outputMultiplier)
        HorizontalOutput = self.clamp((leash.X_Positive - leash.X_Negative) * outputMultiplier)

        Y_Combined = leash.Y_Positive + leash.Y_Negative
        #Up/Down Deadzone, stops movement if pulled too high or low.
        if (Y_Combined) >= leash.settings.UpDownDeadzone:
            VerticalOutput = 0.0
            HorizontalOutput = 0.0
        #Up/Down Compensation
        if leash.settings.UpDownCompensation != 0:
            Y_Modifier = self.clamp(1.0 - ((Y_Combined) * leash.settings.UpDownCompensation))
            VerticalOutput /= Y_Modifier
            HorizontalOutput /= Y_Modifier
            # This is not linear... I don't know, I think I might've failed math.

        #Turning Math
        if leash.settings.TurningEnabled and leash.Stretch > leash.settings.TurningDeadzone:
            TurningSpeed = leash.settings.TurningMultiplier

            match leash.LeashDirection:
                case "North":
                    if leash.Z_Positive < leash.settings.TurningGoal:
                        TurningSpeed *= HorizontalOutput
                        if leash.X_Positive > leash.X_Negative:
                            # Right
                            TurningSpeed += leash.Z_Negative
                        else: 
                            # Left
                            TurningSpeed -= leash.Z_Negative
                    else: 
                        TurningSpeed = 0.0
                case "South":
                    if leash.Z_Negative < leash.settings.TurningGoal:
                        TurningSpeed *= -HorizontalOutput
                        if leash.X_Positive > leash.X_Negative:
                            # Left
                            TurningSpeed -= leash.Z_Positive
                        else:
                            # Right
                            TurningSpeed += leash.Z_Positive
                    else:
                        TurningSpeed = 0.0
                case "East":
                    if leash.X_Positive < leash.settings.TurningGoal:
                        TurningSpeed *= VerticalOutput
                        if leash.Z_Positive > leash.Z_Negative:
                            # Right
                            TurningSpeed += leash.X_Negative
                        else:
                            # Left
                            TurningSpeed -= leash.X_Negative
                    else:   
                        TurningSpeed = 0.0
                case "West":
                    if leash.X_Negative < leash.settings.TurningGoal:
                        TurningSpeed *= -VerticalOutput
                        if leash.Z_Positive > leash.Z_Negative:
                            # Left
                            TurningSpeed -= leash.X_Positive
                        else:
                            # Right
                            TurningSpeed += leash.X_Positive
                    else:
                        TurningSpeed = 0.0

            TurningSpeed = self.clamp(TurningSpeed)
        else:
            TurningSpeed = 0.0

        #Leash is grabbed
        if leash.Grabbed: 
            self.updateProgram(True, counter)

            if leash.settings.Logging:
                if leash.wasGrabbed == False:
                    print('\x1b[1;32;40m' + f"{leash.Name} grabbed" + '\x1b[0m')
                    leash.wasGrabbed = True
            else:
                print(f"{leash.Name} is grabbed")

            if leash.Stretch > leash.settings.RunDeadzone: #Running
                self.leashOutput(VerticalOutput, HorizontalOutput, TurningSpeed, 1, leash.settings)
            elif leash.Stretch > leash.settings.WalkDeadzone: #Walking
                self.leashOutput(VerticalOutput, HorizontalOutput, TurningSpeed, 0, leash.settings)
            else: #Not stretched enough to move.
                self.leashOutput(0.0, 0.0, 0.0, 0, leash.settings)
            
            time.sleep(leash.settings.ActiveDelay)
            Thread(target=self.leashRun, args=(leash, counter+1)).start()# Run thread if still grabbed

        elif leash.Grabbed != leash.wasGrabbed:
            if leash.settings.Logging:
                print('\x1b[1;33;40m' + f"{leash.Name} dropped" + '\x1b[0m')
            else:
                print(f"{leash.Name} dropped")

            leash.Active = False
            leash.resetMovement()
            self.leashOutput(0.0, 0.0, 0.0, 0, leash.settings)

            leash.wasGrabbed = False
            self.resetProgram()
        
        else: # Only used at the start
            if not leash.settings.Logging:
                print("Waiting for Initial Input")

            leash.Active = False
            self.leashOutput(0.0, 0.0, 0.0, 0, leash.settings)
            self.resetProgram()

            time.sleep(leash.settings.InactiveDelay)

        statelock.release()

    def leashOutput(self, vert: float, hori: float, turn: float, runType: bool, settings: ConfigSettings):

        oscClient = SimpleUDPClient(settings.IP, settings.SendingPort)

        #TODO: Remove this.
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
            #Normal OSC outputs  function
            oscClient.send_message("/input/Vertical", vert)
            oscClient.send_message("/input/Horizontal", hori)
            if settings.TurningEnabled: 
                oscClient.send_message("/input/LookHorizontal", turn)
            oscClient.send_message("/input/Run", runType)

        if not settings.TurningEnabled: 
            print(f"\tVert: {vert} | Hori: {hori} | Run: {runType}") 
        else:
            print(f"\tVert: {vert} | Hori: {hori} | Run: {runType} | Turn: {turn}")

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
    