import json
import os

# Default configs in case the user doesn't have one

DefaultConfig = {
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "StrengthMultiplier": 1.2,
        "TurningEnabled": False,
        "TurningMultiplier": 0.75,
        "TurningDeadzone": 0.15,
        "TurningGoal": 90,
        "TurningKp": 0.5,
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
        },
        "ScaleSlowdownEnabled": True,
        "ScaleParameter": "Go/ScaleFloat",
        "ScaleNormal": 0.25,
        "BringGameToFront": False,
        "GameTitle": "VRChat",
        "AutoStartSteamVR": True,
        "DisableParameter": "LeashDisable",
        "DisableGUI": False,
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

def setup_openvr(config):
    # Import openvr if user wants to autostart the app with SteamVR
    if config["AutoStartSteamVR"]:
        try:
            import openvr
            vr = openvr.init(openvr.VRApplication_Utility)
            # Create an IVRApplications object
            applications = openvr.IVRApplications()

            # Save AppManifest to manifest.vrmanifest
            with open("./manifest.vrmanifest", "w") as f:
                f.write(json.dumps(AppManifest))
            
            # Register the manifest file's absolute path with SteamVR
            manifest_path = os.path.abspath("./manifest.vrmanifest")
            error = openvr.EVRFirmwareError()
            applications.addApplicationManifest(manifest_path, False)
            #applications.removeApplicationManifest(manifest_path)
            if error.value != 0:
                print("Error adding manifest: ", error)
            else:
                print("Manifest added successfully")
                # Set the application to start automatically when SteamVR starts
                applications.setApplicationAutoLaunch(AppManifest["applications"][0]["app_key"], True)
                
            # Listen for the event that SteamVR is shutting down
            # This is a blocking call, so it will wait here until SteamVR shuts down
            #event = openvr.VREvent_t()
            #while True:
            #    if vr.pollNextEvent(event):
            #        if event.eventType == openvr.VREvent_Quit:
            #            break

        
        except openvr.error_code.ApplicationError_InvalidManifest as e:
            print('\x1b[1;31;40m' + f'Error: {e}\nWarning: Was not able to import openvr!' + '\x1b[0m')

def createDefaultConfigFile(configPath): # Creates a default config
    try:
        with open(configPath, "w") as cf:
            json.dump(DefaultConfig, cf)

        print("Default config file created")

    except Exception as e:
        print("Error creating default config file: ", e)
        raise e

def bootstrap(configPath = "./config.json") -> dict:
    # Test if Config file exists. Create the default if it does not. Initialize OpenVR if user wants to autostart with SteamVR
    if not os.path.exists(configPath):
        print("Config file was not found...", "\nCreating default config file...")
        createDefaultConfigFile(configPath)
        setup_openvr(DefaultConfig)
        return DefaultConfig
    else:
        print("Config file found\n")
        with open(configPath, "r") as cf:
            config = json.load(cf)
        setup_openvr(config)
        return config        
        
        
        