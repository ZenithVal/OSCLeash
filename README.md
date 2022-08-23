# OSCLeash

Hi, sorry, I swear I'm not a dissapointment to my parents. This is NOT user friendly yet. <br />
A "simple" system to make a functional "Leash" in VRchat using OSC as an input controller. <br /> 
Could be adapted to any pullable physbone; EG: A tail. <br />
If you're smarter and want to improve this code, by all means, PLEASE do so. 

## How TF this work??

Here's the prefab from releases but with some meshes for visual help.

There's two systems at play; one to "aim" what direction to move in and the physbone intelf that determines move speed.

On the Aim system, there's 4 Contact Recieverers, 2 position constraints, and 1 aim constraint.

4 proximity Contacts (Z+,Z-,X+,X-) are placed around a center point which has an aim constraint with a sender on the end that triggers the proximity contacts. 
1 Position constraint is locked to the ground plane and is tracked to another position constriant that's free moving and tracked to the end of the leash physbone system. This allows it to be free moving wherever. In hindsight... I don't know why there's two position constraints but it's too late now AAAAA. As the leash physbone moves around the directional, the aim constraint move along contact sender, triggering all the proximity contacts. We read that for OSC.

![Function Example](https://cdn.discordapp.com/attachments/606734710328000532/1011420984303165500/Example_Gif.gif)

(Z_Positive - Z_Negative) * Leash_Stretch = Vertical  <br />
(X_Positrive - Z_Negative) * Leash_Stretch = Horizontal

Output those two values back to VRC and boom, you're moving in the direction of the arrow based on how stretched the leash is. We use Leash_IsGrabbed as well to confirm it's actually being grabbed along with some other fancy stuff I don't really understand fully.

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
- Someone else did this but it was a closed source executable.
