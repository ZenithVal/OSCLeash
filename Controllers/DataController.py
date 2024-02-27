import time
import os
import ctypes #Required for colored error messages.

DefaultConfig = {
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "StrengthMultiplier": 1.2,
        "UpDownCompensation": 1.0,
        "UpDownDeadzone": 0.5,
        "TurningEnabled": False,
        "TurningMultiplier": 0.80,
        "TurningDeadzone": 0.15,
        "TurningGoal": 90,
        "ActiveDelay": 0.02,
        "InactiveDelay": 0.5,
        "Logging": False,
        "XboxJoystickMovement": False,
        
        "PhysboneParameters":
        [
                "Leash"
        ],
        "DirectionalParameters":
        {
                "Z_Positive_Param": "Leash_Z+",
                "Z_Negative_Param": "Leash_Z-",
                "X_Positive_Param": "Leash_X+",
                "X_Negative_Param": "Leash_X-",
                "Y_Positive_Param": "Leash_Y+",
                "Y_Negative_Param": "Leash_Y-"
        }
}


class ConfigSettings:

    def __init__(self, configData):
            self.setSettings(configData) #Set config values
            self.printInfo() #Print config values
        
    def setSettings(self, configJson):
        try:
            self.IP = configJson["IP"]
            self.ListeningPort = configJson["ListeningPort"]
            self.SendingPort = configJson["SendingPort"]
            self.RunDeadzone = configJson["RunDeadzone"]
            self.WalkDeadzone = configJson["WalkDeadzone"]
            self.StrengthMultiplier = configJson["StrengthMultiplier"]
            self.UpDownCompensation = configJson["UpDownCompensation"]
            self.UpDownDeadzone = configJson["UpDownDeadzone"]
            self.TurningEnabled = configJson["TurningEnabled"]
            self.TurningMultiplier = configJson["TurningMultiplier"]
            self.TurningDeadzone = configJson["TurningDeadzone"]
            self.TurningGoal = (configJson["TurningGoal"]/180)
            self.ActiveDelay = configJson["ActiveDelay"]
            self.InactiveDelay = configJson["InactiveDelay"]
            self.Logging = configJson["Logging"]
            self.XboxJoystickMovement = configJson["XboxJoystickMovement"]
            self.Leashes = configJson["PhysboneParameters"]
        except Exception as e: 
            print('\x1b[1;31;40m' + 'Malformed Config.json contents. Was something missing?' + '\x1b[0m')
            print(f"Exception: {e}\nDefault Config will be loaded.\n")
            os.system("pause")
            print("")

            self.IP = DefaultConfig["IP"]
            self.ListeningPort = DefaultConfig["ListeningPort"]
            self.SendingPort = DefaultConfig["SendingPort"]
            self.RunDeadzone = DefaultConfig["RunDeadzone"]
            self.WalkDeadzone = DefaultConfig["WalkDeadzone"]
            self.StrengthMultiplier = DefaultConfig["StrengthMultiplier"]
            self.UpDownCompensation = DefaultConfig["UpDownCompensation"]
            self.UpDownDeadzone = DefaultConfig["UpDownDeadzone"]
            self.TurningEnabled = DefaultConfig["TurningEnabled"]
            self.TurningMultiplier = DefaultConfig["TurningMultiplier"]
            self.TurningDeadzone = DefaultConfig["TurningDeadzone"]
            self.TurningGoal = (DefaultConfig["TurningGoal"]/180)
            self.ActiveDelay = DefaultConfig["ActiveDelay"]
            self.InactiveDelay = DefaultConfig["InactiveDelay"]
            self.Logging = DefaultConfig["Logging"]
            self.XboxJoystickMovement = DefaultConfig["XboxJoystickMovement"]
            self.Leashes = DefaultConfig["PhysboneParameters"]

    def addGamepadControls(self, gamepad, runButton):
        self.gamepad = gamepad
        self.runButton = runButton

    def printInfo(self):        
        print('\x1b[1;32;40m' + 'Settings:' + '\x1b[0m')

        if self.Logging:
            print('\x1b\t[1;33;40m' + 'Logging is enabled' + '\x1b[0m')

        if self.IP == "127.0.0.1":
            print("\tIP: Localhost")
        else:  
            print("\tIP: Not Localhost? Interesting.")

        print(f"\tListening on port {self.ListeningPort}\n\tSending on port {self.SendingPort}")

        print("")

        AllLeashes = ""
        for leash in self.Leashes:
            AllLeashes += leash + ", "
        AllLeashes = AllLeashes[:-2]
        print(f"\tLeash name(s): {AllLeashes}")

        print(f"\tStrength Multiplier of {self.StrengthMultiplier}")
        print("\tDelays of {:.0f}".format(self.ActiveDelay*1000),"& {:.0f}".format(self.InactiveDelay*1000),"ms")
        print("\tRunning Deadzone of {:.0f}".format(self.RunDeadzone*100)+"% stretch")
        print("\tWalking Deadzone of {:.0f}".format(self.WalkDeadzone*100)+"% stretch")
        
        print(f"\tUp/Down Compensation of {self.UpDownCompensation} & {self.UpDownDeadzone*100}% Max Angle")

        if self.TurningEnabled: 
            print(f"\tTurning is enabled:")
            print(f"\t - Multiplier of {self.TurningMultiplier}")
            print(f"\t - Deadzone of {self.TurningDeadzone}")
            print(f"\t - Goal of {self.TurningGoal*180}°")

        print("")

            
class Leash:

    def __init__(self, paraName, contacts, settings: ConfigSettings):
        
        self.Name: str = paraName
        self.settings = settings

        self.Stretch: float = 0

        self.Z_Positive: float = 0
        self.Z_Negative: float = 0
        self.X_Positive: float = 0
        self.X_Negative: float = 0
        self.Y_Positive: float = 0
        self.Y_Negative: float = 0

        self.turningSpeed: float = 0

        # Booleans for thread logic
        self.Grabbed: bool = False
        self.wasGrabbed: bool = False
        self.Posed: bool = False
        self.Active: bool = False

        if settings.TurningEnabled:
            self.LeashDirection = paraName.split("_")[-1]

        self.Z_Positive_ParamName: str = contacts["Z_Positive_Param"] #Forward
        self.Z_Negative_ParamName: str = contacts["Z_Negative_Param"] #Backward
        self.X_Positive_ParamName: str = contacts["X_Positive_Param"] #Right
        self.X_Negative_ParamName: str = contacts["X_Negative_Param"] #Left
        self.Y_Positive_ParamName: str = contacts["Y_Positive_Param"] #Up
        self.Y_Negative_ParamName: str = contacts["Y_Negative_Param"] #Down

    def resetMovement(self):
        self.Z_Positive: float = 0
        self.Z_Negative: float = 0
        self.X_Positive: float = 0
        self.X_Negative: float = 0
        self.Y_Positive: float = 0
        self.Y_Negative: float = 0

    def printDirections(self):
        print(f"\tZ: {round((self.Z_Positive), 2)},{round((self.Z_Negative), 2)} |  X: {round((self.X_Positive), 2)},{round((self.X_Negative), 2)} | Y: {round((self.Y_Positive), 2)},{round((self.Y_Negative), 2)}")
