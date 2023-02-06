import json
import os
import sys
import time
from colorama import Fore
from pprint import pprint
# Default configs in case the user doesn't have one

DefaultConfig = {
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,

        "Logging": True,
        "GUIEnabled": True,
        "GUITheme": "",
        "StartWithSteamVR": False,

        "ActiveDelay": 0.05,
        "InactiveDelay": 0.5,

        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "StrengthMultiplier": 1.1,

        "TurningEnabled": False,
        "TurningMultiplier": 0.75,
        "TurningDeadzone": 0.15,
        "TurningGoal": 90,
        "TurningKp": 0.5,

        "XboxJoystickMovement": False,
        "BringGameToFront": False,
        "GameTitle": "VRChat",

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
        },

        "DisableParameter": "LeashDisable",

        "ScaleSlowdownEnabled": True,
        "ScaleParameter": "Go/ScaleFloat",
        "ScaleDefault": 0.25,

        "ArmLockFix": True,
        "ArmLockFixInterval": 0.7,
        "ArmLockFixDuration": 0.02,

        "VerticalMovement": True,
        "VerticalMovementSpeed": 0.1,
}

AppManifest = {
	"source" : "builtin",
	"applications": [{
		"app_key": "zenithval.LeashSC",
		"launch_type": "binary",
		"binary_path_windows": "./OSCLeash.exe",
		"is_dashboard_overlay": True,

		"strings": {
			"en_us": {
				"name": "OSCLeash",
				"description": "OSCLeash"
			}
		}
	}]
}

# From https://stackoverflow.com/a/42615559
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__+"/.."))
    
    
def combineJson(defaults: dict, config: dict):
    # Combine the default config with the user's config
    wasConfigMalformed = False
    config = config.copy()
    for key, value in defaults.items():
        if key not in config.keys():
            wasConfigMalformed = True
            config[key] = value
        elif isinstance(value, dict) and not isinstance(config[key], list):
            config[key], _wasConfigMalformed = combineJson(value, config[key])
            if _wasConfigMalformed:
                wasConfigMalformed = True
    return config, wasConfigMalformed

def setup_openvr():
    # Import openvr if user wants to autostart the app with SteamVR
    # if config["StartWithSteamVR"]: We don't need an if, this was called in an if.
    try:
        import openvr
        # Setting this to Overlay will start SteamVR, which sucks when testing stuff in just Unity
        vr = openvr.init(openvr.VRApplication_Utility)
        # Create an IVRApplications object
        applications = openvr.IVRApplications()

        # Save AppManifest to manifest.vrmanifest
        with open(f"{application_path}\\manifest.vrmanifest", "w") as f:
            f.write(json.dumps(AppManifest, indent=2))

        # Register the manifest file's absolute path with SteamVR
        manifest_path = os.path.abspath(f"{application_path}\\manifest.vrmanifest")
        error = openvr.EVRFirmwareError()
        applications.addApplicationManifest(manifest_path, False)
        #applications.removeApplicationManifest(manifest_path)
        if error.value != 0:
            print("Error adding manifest: ", error)
        else:
            applications.setApplicationAutoLaunch(AppManifest["applications"][0]["app_key"], True)
            print("Manifest added successfully")
            # Set the application to start automatically when SteamVR starts

        # Listen for the event that SteamVR is shutting down
        # This is a blocking call, so it will wait here until SteamVR shuts down
        #event = openvr.VREvent_t()
        #while True:
        #    if vr.pollNextEvent(event):
        #        if event.eventType == openvr.VREvent_Quit:
        #            break
        return True
    except Exception as e:
        print(Fore.RED + f'Error: {e}\nWarning: Was not able to import openvr!' + Fore.RESET)
        return False
        

def createDefaultConfigFile(configPath): # Creates a default config
    try:
        with open(configPath, "w") as cf:
            cf.write(json.dumps(DefaultConfig, indent=2))

        print("Default config file created")

    except Exception as e:
        print("Error creating default config file: ", e)
        raise e

def bootstrap(configPath = f"{application_path}\\Config.json") -> dict:
    # Test if Config file exists. Create the default if it does not. Initialize OpenVR if user wants to autostart with SteamVR
    print(f"Checking for config file at {configPath}...")
    if not os.path.exists(configPath):
        print(f"Config file was not found...", "\nCreating default config file...")
        time.sleep(2)
        createDefaultConfigFile(configPath)
        #printInfo(DefaultConfig)
        return DefaultConfig, setup_openvr()
    else:
        print("Config file found\n")
        try:
            with open(configPath, "r") as cf:
                _config = json.load(cf)
            config, wasConfigMalformed = combineJson(DefaultConfig, _config)
            if wasConfigMalformed:
                oldConfigPath = configPath + ".old"
                with open(oldConfigPath, "w") as cfo:
                    cfo.write(json.dumps(_config, indent=2))
                with open(configPath, "w") as cf:
                    cf.write(json.dumps(config, indent=2))
                print(Fore.RED + 'Malformed config file. Loading default values.' + Fore.RESET)
                print("Your config file has been backed up to " + f"{oldConfigPath}\n")
                time.sleep(2)
            return config, setup_openvr()
        except Exception as e: #Catch a malformed config file.
            print(Fore.RED + 'Malformed config file. Loading default values.' + Fore.RESET)
            print(e,"was the exception\n")
            time.sleep(2)
            return DefaultConfig, setup_openvr()


def printInfo(config):
    print(Fore.GREEN + 'OSCLeash is Running!' + Fore.RESET)

    if config['IP'] == "127.0.0.1":
        print("IP: Localhost")
    else:
        print("IP: Not Localhost? Wack.")

    print(f"Listening on port {config['ListeningPort']}\nSending on port {config['SendingPort']}")
    print("Delays of {:.0f}".format(config['ActiveDelay']*1000),"& {:.0f}".format(config['InactiveDelay']*1000),"ms")

    print("")

    if config['Logging']:
        print("Logging is enabled")
    else:
        print("Logging is disabled")

    if config['GUIEnabled']:
        print("GUI is enabled:")
        if config["GUITheme"] != "":
            print(f'\tAttempting to use {config["GUITheme"]} as the theme')
        else:
            print(f"\tUsing standard theme")
    else:
        print("GUI is disabled")


    if config['StartWithSteamVR']:
        print("OSCLeash will start with SteamVR")
        # try:
        #     setup_openvr()
        # except Exception as e:
        #     print(e)

    print("")

    print("Run Deadzone of {:.0f}".format(config['RunDeadzone']*100)+"% stretch")
    print("Walking Deadzone of {:.0f}".format(config['WalkDeadzone']*100)+"% stretch")

    if config['TurningEnabled']:
        print(f"Turning is enabled:\n\tMultiplier of {config['TurningMultiplier']}\n\tDeadzone of {config['TurningDeadzone']}\n\tGoal of {config['TurningGoal']*180}°")
    else:
        print("Turning is disabled")

    if config['ScaleSlowdownEnabled']:
        print(f"Scaling is enabled:\n\tListening to {config['ScaleParameter']}\n\tDefault scale of {config['ScaleDefault']}")
    else:
        print("Scaling is disabled")

    if config['DisableParameter'] != "":
        print(f"Disable Parameter set to {config['DisableParameter']}")
    else:
        print("Disable Parameter not used")

    print("")

    # XBOX SUPPORT: Remove later when not needed.
    if config['XboxJoystickMovement']:
        print("Controller emulation is enabled.")
        if config['BringGameToFront']:
            print(f"The {config['GameTitle']} window will be brought to the front when required" )
    else:
        print(f'Controller support is disabled')
        if config['ArmLockFix']:
            print(f"OSC Arm Lock Fix is enabled. Interval of {config['ArmLockFixInterval']}s, and will wait for {config['ArmLockFixDuration']}s")
        else:
            print("OSC Arm Lock Fix is disabled")

    print("")

# config['']
