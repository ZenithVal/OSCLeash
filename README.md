
# OSCLeash
A "simple" system to make a functional "Leash" in VRchat using OSC as an input controller.  <br/>  I swear I'm not a disappointment to my parents. This is **kinda** user friendly now. <br/> This can be adapted to any pullable physbone; EG: A tail. 
<br/>

## How TF this work??
Here's a breakdown of the system in 4 steps.

**Step 1: Gather Leash Physbone Values** <br/> 
This one is simple. We receive the Leash_Stretch and Leash_Grabbed parameters. <br/> If Leash_Grabbed becomes true, we begin reading Leash_Stretch 

We'll use these values in this example: <br/> 
>Leash_IsGrabbed = True <br/> 
>Leash_Stretch = 0.95 <br/> 

**Step 2: Gather Directional Contact values** <br/> 
![Function Example](https://cdn.discordapp.com/attachments/606734710328000532/1011420984303165500/Example_Gif.gif) <br/> 
4 Contacts (Blue) surround a object with an aim constraint and a contact at the tip. (Yellow) <br/>  Based on where the constraint is aimed, it will give us 4 Values. 

If it was pointing South-South-East we would get...  <br/> 
>Leash_Z+ = 0.0 <br/> 
>Leash_Z- = 0.75 <br/> 
>Leash_X+ = 0.0 <br/> 
>Leash_X- = 0.25 <br/> 

**Step 3: MAAAATH!** <br/> 
Math is fun. Add the negative and positive contacts & multiply by the stretch value.
>(Z_Positive - Z_Negative) * Leash_Stretch = Vertical <br/> 
>(X_Positrive - Z_Negative) * Leash_Stretch = Horizontal <br/> 

So our calculation for speed output would look like: <br/>
>(0.0 - 0.75) * 0.95 = -0.7125 = Veritcal <br/>
>(0.25 - 0) * 0.95 = 0.2375 = Horizontal <br/>

**Step 4: Outputs** <br/> 
If either value is above the walking deadzone (default 0.15) we start outputting them instead of 0 <br/> If either value is above the running deadzone (0.7) we tell the player to run (x2 speed)

All movement values are relative to the VRC world's movement speed limits. <br/> So we'd be moving at 142.5% speed south and 47.5% speed to the east. <br/>

If the values are below the deadzones or _IsGrabbed is false, send 0s for the OSC values once.
<br/>

## Known issue WITH WORKAROUND.
As with RavenBuilds's take on the OSCLeash, using OSC as an input for movement causes you arms to be locked into desktop pose, please slap some support onto this canny! https://feedback.vrchat.com/feature-requests/p/osc-locks-arms

**TEMPORARY WORKAROUND**: Set "XboxJoystickMovement" to true in the config file. Instead of outputting movement with OSC, this will emulate an Xbox controller joystick! Skipping over the above issue enitely. This will probably be removed when VRC fixes the issue. Check the extra steps in setup for this.
<br/>

## Running the program
1. **Via an executable**
	- Download release zip from https://github.com/ZenithVal/OSCLeash/releases/tag/Main
	- Extract wherever.
	- Run Executable
3. **From the source**
	- Clone the github
	- Run `pip install -r requirements.txt` in the directory to install libraries
	- Run the python script

## Setup
Requires VRC3 Avatar SDK.
1. Download the program via one of the above methods.
2. Define config.json settings if needed.
3. Grab the prefab from releases https://github.com/ZenithVal/OSCLeash/releases/tag/Main
4. Set the source of `Leash Physbone` to whatever you like, and adjust it if needed.
5. The position constrain source on `Aim Target` should be assigned to the last bone of your leash.
6. If your phybone is off center, copy the constraint from above and paste it on the root of the prefab. 
        - The source should be the origin of your leash.
7. Make sure to reset OSC in the radial menu if this is being retrofit as an update to an avatar.
8. Run program.

There will be a setup guide/wiki later.
**If using executable with temporary xbox input workaround**
You need this installed https://github.com/ViGEm/ViGEmBus/releases & you must select the VRC window while running the tool.
<br/>

## Config
| Value | Use | default |
| --- | --- | --- |
| IP | Address to send OSC data to | 127.0.0.1 |
| ListeningPort | Port to listen for OSC data on | 9001 |
| Sending port | Port to send OSC data to | 9000 |
| RunDeadzone | Stretch value above this will cause running | 0.70 |
| WalkDeadzone | Stretch value above this will cause walking | 0.15 |
| ActiveDelay | Delay between OSC messages while leash is being grabbed | 0.1 second |
| InactiveDelay | Added delay between checks while Leash is not being grabbed. | 0.5 seconds |
| Logging | Logging for OSC messages being output | True
| XboxJoystickMovement | Esoteric workaround for VRC breaking animations upon OSC input | false
| PhysboneParamaters | A list of Physbones to use as leashes | below |
| DirectionalParamaters | A dictionary of contacts to use for direction calculation | below |
---------
### Physbone Parameters
The list of the parameters your leashes are using.
**WIP Functionaly, only one leash is supported right now.**

If you had two leashes, your list might look like this:
```json
        "PhysboneParameters":
        [
            "Leash1",
            "Leash2",
            "Dont_do_this_its_not_supported_yet"
        ],
```
The script will automatically read from the _IsGrabbed and _Stretch parameters correlating with the above.

---------
### Directional Parameters

If you wish to change the contacts to used for direction calculations, you can do so here.

```python
        "DirectionalParamaters":
        {
                "Z_Positive_Param": "Leash_Z+",
                "Z_Negative_Param": "Leash_Z-",
                "X_Positive_Param": "Leash_X+",
                "X_Negative_Param": "Leash_X-"
        }
```

# Default Config

```json
{
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "StrengthMultiplier": 1.2,
        "ActiveDelay": 0.1,     
        "InactiveDelay": 0.5,
        "Logging": true,
        "XboxJoystickMovement": false,
        
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
```

# Credits
- @ALeonic created Version 2 Rewrite
- @FrostbyteVR babied me through 90% of the process of making the python script.
- @I5UCC I stared at the code of his ThumbParamsOSC for a long time to learn a bit. Some lines are a carbon copy.
- Someone else did this but it was a closed source executable.