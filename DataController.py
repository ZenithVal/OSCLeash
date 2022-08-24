import json

class ConfigSettings:

    def __init__(self, configFileName = None):
        try:
            config = json.load(open(configFileName))

            print("Successfully read config.\n")
            self.setSettings(config) #Set config values

        except Exception as e:
            print('\x1b[1;31;40m' + 'Missing or incorrect config file. Loading default values.  ' + '\x1b[0m')
            print(e,"\n")

            self.setSettings() #set default values

        
    def setSettings(self, configJson = None):
        self.IP = "127.0.0.1" if configJson is None else configJson["IP"]
        self.ListeningPort = 9001 if configJson is None else configJson["ListeningPort"]
        self.SendingPort = 9000 if configJson is None else configJson["SendingPort"]
        self.RunDeadzone = 0.70 if configJson is None else configJson["RunDeadzone"]
        self.WalkDeadzone = 0.15 if configJson is None else configJson["WalkDeadzone"]
        self.ActiveDelay = .1 if configJson is None else configJson["ActiveDelay"]
        self.InactiveDelay = .5 if configJson is None else configJson["InactiveDelay"]
        self.Logging = True if configJson is None else configJson["Logging"]

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

    def __init__(self, configFileName = None):

        try:
            config = json.load(open(configFileName))

            print("Successfully read config.\n")
            self.getConfigParameters(config) #Set config values

        except Exception as e:

            print('\x1b[1;31;40m' + 'Missing or incorrect config file. Loading default values.  ' + '\x1b[0m')
            print(e,"\n")

            self.getConfigParameters() #set default values
        
    def getConfigParameters(self, configJson = None):

        if configJson is not None:
            self.configParameters = configJson["Parameters"]

        else: #Load default values
            self.configParameters = {
                "Leash_Z+",
                "Leash_Z-",
                "Leash_X+",
                "Leash_Z-",
                "Leash_IsGrabbed",
                "Leash_Stretch"
            }