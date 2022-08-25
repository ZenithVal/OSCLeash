import json

class ConfigSettings:

    def __init__(self, configFileName):
        try:
            config = json.load(open(configFileName))
            print("Successfully read config.")

            self.IP = config["IP"]
            self.ListeningPort = config["ListeningPort"]
            self.SendingPort = config["SendingPort"]
            self.RunDeadzone = config["RunDeadzone"]
            self.WalkDeadzone = config["WalkDeadzone"]
            self.ActiveDelay = config["ActiveDelay"]
            self.InactiveDelay = config["InactiveDelay"]
            self.Logging = config["Logging"]
        except Exception as e:
            print('\x1b[1;31;40m' + 'Missing or incorrect config file. Loading default values.  ' + '\x1b[0m')
            print("\n", e,"was the exception")

            self.IP = "127.0.0.1"
            self.ListeningPort = 9001
            self.SendingPort = 9000
            self.RunDeadzone = 0.70
            self.WalkDeadzone = 0.15
            self.ActiveDelay = .1
            self.InactiveDelay = .5
            self.Logging = True
        
    def printValues(self):
        # Settings confirmation
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
    LeashWasGrabbed: bool = False
    LeashGrabbed: bool = False
    LeashStretch: float = 0
    Z_Positive: float = 0
    Z_Negative: float = 0
    X_Positive: float = 0
    X_Negative: float = 0
