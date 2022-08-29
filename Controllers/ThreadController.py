from pythonosc.udp_client import SimpleUDPClient
from threading import Lock, Thread
import time
import os
import ctypes #Required for colored error messages.

from Controllers.DataController import ConfigSettings, Leash

class Program:

    # Class variable to determine if the program is running on a thread (Prevents multiple threads)
    __running = False 
    __threadCounter = 0

    def resetProgram(self):
        Program.__running = False 
        Program.__threadCounter = 0
    
    def updateProgram(self, runBool:bool, countValue:int):
        Program.__running = runBool
        Program.__threadCounter = countValue

    def leashRun(self, leash: Leash, counter:int = 0): # TODO: make work for one leash

        if counter == 0 and Program.__running:
            return

        statelock = Lock()
        statelock.acquire()
        
        # self.cls()
        leash.settings.printInfo()
        leash.printDirections()
        print("\nCurrent Status:\n")

        #Movement
        VerticalOutput = self.clamp((leash.Z_Positive - leash.Z_Negative) * leash.Stretch * leash.settings.StrengthMultiplier)
        HorizontalOutput = self.clamp((leash.X_Positive - leash.X_Negative) * leash.Stretch * leash.settings.StrengthMultiplier)

        #Grab state
        LeashGrabbed = leash.Grabbed
        LeashReleased = leash.Grabbed != leash.wasGrabbed #Do Leash Grab states line up?

        if leash.Grabbed: #Leash is grabbed
            self.updateProgram(True, counter)

            if leash.wasGrabbed == False:
                leash.wasGrabbed = True
                print("Leash recently grabbed")
            else:
                print("Leash is grabbed")

            if leash.Stretch > leash.settings.RunDeadzone: #Running deadzone
                self.leashOutput(VerticalOutput, HorizontalOutput, True, leash.settings)
            elif leash.Stretch > leash.settings.WalkDeadzone: #Walking deadzone
                self.leashOutput(VerticalOutput, HorizontalOutput, False, leash.settings)
            else: #Not stretched enough to move.
                self.leashOutput(0.0, 0.0, 0, leash.settings)
            
            time.sleep(leash.settings.ActiveDelay)
            Thread(target=self.leashRun, args=(leash, counter+1)).start()# Run thread if still grabbed
        
        elif leash.Grabbed != leash.wasGrabbed:
            print("Leash has been released")

            leash.resetMovement()
            self.leashOutput(0.0, 0.0, 0, leash.settings)

            leash.wasGrabbed = False

            self.resetProgram()
            time.sleep(leash.settings.InactiveDelay)    

            # Thread(target=self.leashRun, args=(leash,)).start() -NOTE: No longer needed as "IsGrabbed" will start a new thread instead
        
        else: # Only used at the start
            print("Waiting...")

            self.resetProgram()
            time.sleep(leash.settings.InactiveDelay)
            # Thread(target=self.leashRun, args=(leash,)).start() -NOTE: No longer needed as "IsGrabbed" will start a new thread instead

        statelock.release()

    def leashOutput(self, vert: float, hori: float, runType: int, settings: ConfigSettings):

        oscClient = SimpleUDPClient(settings.IP, settings.SendingPort)

        #Xbox Emulation: REMOVE LATER WHEN OSC IS FIXED
        if settings.vgamepadImported:
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
                print('\x1b[1;31;40m' + 'Tool required for controller emulation not installed. Please check the documentation.\n' + '\x1b[0m') 
                exit()

        else:
            #Normal function
            print("\nSending through oscClient\n")
            oscClient.send_message("/input/Vertical", vert)
            oscClient.send_message("/input/Horizontal", hori)
            oscClient.send_message("/input/Run", runType) # recommend using bool instead of int if possible

        print("\tVertical: {}\n\tHorizontal: {}\n\tRun: {}".format(vert,hori,runType))

    def clamp (self, n):
        return max(-1.0, min(n, 1.0))

    def cls(self): # Console Clear
        """Clears Console"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def setWindowTitle(self): # Set window name on the Window
        if os.name == 'nt':
            os.system("OSCLeash")

    