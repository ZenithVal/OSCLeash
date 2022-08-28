
DefaultConfig = {
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "StrengthMultiplier": 1.2,
        "ActiveDelay": 0.1,     
        "InactiveDelay": 0.5,
        "Logging": True,
        "XboxJoystickMovement": False,
        
        "PhysboneParameters":
        [
                "Leash"
        ],

        "DirectionalParamaters":
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
        self.IP = configJson["IP"]
        self.ListeningPort = configJson["ListeningPort"]
        self.SendingPort = configJson["SendingPort"]
        self.RunDeadzone = configJson["RunDeadzone"]
        self.WalkDeadzone = configJson["WalkDeadzone"]
        self.StrengthMultiplier = configJson["StrengthMultiplier"]
        self.ActiveDelay = configJson["ActiveDelay"]
        self.InactiveDelay = configJson["InactiveDelay"]
        self.Logging = configJson["Logging"]
        self.XboxJoystickMovement = configJson["XboxJoystickMovement"]

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
        #print("Inactive delay of {:.0f}".format(InactiveDelay*1000),"ms")



class Leash:

    def __init__(self, paraName, contacts, settings: ConfigSettings):
        
        self.Name: str = paraName
        self.settings = settings

        self.Stretch: float = 0
        self.Z_Positive: float = 0
        self.Z_Negative: float = 0
        self.X_Positive: float = 0
        self.X_Negative: float = 0

        self.Grabbed: bool = False
        self.wasGrabbed: bool = False

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
        print("{}: {}".format(self.Z_Positive_ParamName, self.Z_Positive))
        print("{}: {}".format(self.Z_Negative_ParamName, self.Z_Negative))
        print("{}: {}".format(self.X_Positive_ParamName, self.X_Positive))
        print("{}: {}".format(self.X_Negative_ParamName, self.X_Negative))