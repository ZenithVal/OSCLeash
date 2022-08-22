# OSCLeash

Hi sorry, I swear I'm not a dissapointment to my parents. <br />
A simple system to make a functional "Leash" in VRchat using OSC. Can be adapated for different sources like a tail. <br />
If you're smarter and want to improve this code, by all means, PLEASE do so. 

##

### Running the source:
- Clone the github
- Aquire Prereqs
  - Python 3.10
  - Python-osc 1.8.0 https://pypi.org/project/python-osc/
  - That's PROBABLY it? I literally don't know.
- Run the python script

### Running Executable
- Download release zip
- Extract wherever.
- Run Executable

##

### Setup
1. Define IP and ports in config.json
3. Drop the Prefab onto the root of your avatar (Found in releases)
4. Set the source of the constraint on "Aim Target" to the end of your "leash"
5. Set "Paramater" on your leash's physbone to "Leash" 
6. Your leash needs to be able to stretch, at least a tiny bit.

uh....
Requires VRC3 Avatar SDK.

##

### Parameters

| Parameter | Description |
| --- | --- |
|Leash_IsGrabbed | Physbone IsGrabbed Value
|Leash_Stretch | Physbone Stretch Status
| Z+ | Z Positive |
| Z- | Z Negative |
| X+ | Z Positive |
| X- | Z Negative |

##

### Default Config

```
{
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "Paramaters":
        {
                "I GAVE UP ON THESE, THEY DON'T WORK": "if someone knows how, lmk lol",
                "Z_Positive_Param": "/avatar/parameters/Z+",
                "Z_Negative_Param": "/avatar/parameters/Z-",
                "X_Positive_Param": "/avatar/parameters/X+",
                "X_Negative_Param": "/avatar/parameters/Z-",
                "LeashGrab_Param": "/avatar/parameters/Leash_IsGrabbed",
                "LeashStretch_Param": "/avatar/parameters/Leash_Stretch"
        }
}
```

### Credits

- @FrostbyteVR babied me through 90% of the process of making the python script.
- @I5UCC I stared at the code of his ThumbParamsOSC for a long time to learn a bit. Some lines are a carbon copy.
- Someone else did this but it was a closed source executable... Too sus for me.
