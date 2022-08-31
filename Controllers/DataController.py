import sys
import time
import ctypes #Required for colored error messages.

DefaultConfig = {
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "StrengthMultiplier": 1.2,
        "TurningEnabled": False,
        "TurningMultiplier": 0.5,
        "TurningDeadzone": .15,
        "TurningGoal": 90,
        "ActiveDelay": 0.1,     
        "InactiveDelay": 0.5,
        "Logging": True,
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
                "X_Negative_Param": "Leash_X-"
        }
}


class ConfigSettings:

    def __init__(self, configData):
            self.setSettings(configData) #Set config values
        
    def setSettings(self, configJson):
        try:
            self.IP = configJson["IP"]
            self.ListeningPort = configJson["ListeningPort"]
            self.SendingPort = configJson["SendingPort"]
            self.RunDeadzone = configJson["RunDeadzone"]
            self.WalkDeadzone = configJson["WalkDeadzone"]
            self.StrengthMultiplier = configJson["StrengthMultiplier"]
            self.TurningEnabled = configJson["TurningEnabled"]
            self.TurningMultiplier = configJson["TurningMultiplier"]
            self.TurningDeadzone = configJson["TurningDeadzone"]
            self.TurningGoal = (configJson["TurningGoal"]/180)
            self.ActiveDelay = configJson["ActiveDelay"]
            self.InactiveDelay = configJson["InactiveDelay"]
            self.Logging = configJson["Logging"]
            self.XboxJoystickMovement = configJson["XboxJoystickMovement"]
        except Exception as e: 
            print('\x1b[1;31;40m' + 'Malformed config file. Loading default values.' + '\x1b[0m')
            print(e,"was the exception\n")
            self.IP = DefaultConfig["IP"]
            self.ListeningPort = DefaultConfig["ListeningPort"]
            self.SendingPort = DefaultConfig["SendingPort"]
            self.RunDeadzone = DefaultConfig["RunDeadzone"]
            self.WalkDeadzone = DefaultConfig["WalkDeadzone"]
            self.StrengthMultiplier = DefaultConfig["StrengthMultiplier"]
            self.TurningEnabled = DefaultConfig["TurningEnabled"]
            self.TurningMultiplier = DefaultConfig["TurningMultiplier"]
            self.TurningDeadzone = DefaultConfig["TurningDeadzone"]
            self.TurningGoal = (DefaultConfig["TurningGoal"]/180)
            self.ActiveDelay = DefaultConfig["ActiveDelay"]
            self.InactiveDelay = DefaultConfig["InactiveDelay"]
            self.Logging = DefaultConfig["Logging"]
            self.XboxJoystickMovement = DefaultConfig["XboxJoystickMovement"]
            time.sleep(3)

    def addGamepadControls(self, gamepad, runButton):
        self.gamepad = gamepad
        self.runButton = runButton

    def printInfo(self):        
        print('\x1b[1;32;40m' + 'OSCLeash is Running!' + '\x1b[0m')

        if self.IP == "127.0.0.1":
            print("IP: Localhost")
        else:  
            print("IP: Not Localhost? Wack.")

        print("Listening on port", self.ListeningPort)
        print("Sending on port", self.SendingPort)
        print("Run Deadzone of {:.0f}".format(self.RunDeadzone*100)+"% stretch")
        print("Walking Deadzone of {:.0f}".format(self.WalkDeadzone*100)+"% stretch")
        print("Delays of {:.0f}".format(self.ActiveDelay*1000),"& {:.0f}".format(self.InactiveDelay*1000),"ms")
        if self.TurningEnabled: 
            print(f"Turning is enabled:\n\tMultiplier of {self.TurningMultiplier}\n\tDeadzone of {self.TurningDeadzone}\n\tGoal of {self.TurningGoal*180}°")
            
class Leash:

    def __init__(self, paraName, contacts, settings: ConfigSettings):
        
        self.Name: str = paraName
        self.settings = settings

        self.Stretch: float = 0
        self.Z_Positive: float = 0
        self.Z_Negative: float = 0
        self.X_Positive: float = 0
        self.X_Negative: float = 0

        # Booleans for thread logic
        self.Grabbed: bool = False
        self.wasGrabbed: bool = False
        self.Active: bool = False

        if settings.TurningEnabled:
            self.LeashDirection = paraName.split("_")[-1]

        self.Z_Positive_ParamName: str = contacts["Z_Positive_Param"]
        self.Z_Negative_ParamName: str = contacts["Z_Negative_Param"]
        self.X_Positive_ParamName: str = contacts["X_Positive_Param"]
        self.X_Negative_ParamName: str = contacts["X_Negative_Param"]

    def resetMovement(self):
        self.Z_Positive: float = 0
        self.Z_Negative: float = 0
        self.X_Positive: float = 0
        self.X_Negative: float = 0

    def printDirections(self):
        print("\nContact Directions:\n")

        print("{}: {}".format(self.Z_Positive_ParamName, self.Z_Positive))
        print("{}: {}".format(self.Z_Negative_ParamName, self.Z_Negative))
        print("{}: {}".format(self.X_Positive_ParamName, self.X_Positive))
        print("{}: {}".format(self.X_Negative_ParamName, self.X_Negative))