# OSCLeash

Hi, sorry, I swear I'm not a dissapointment to my parents. This is NOT user friendly yet. <br />
A "simple" system to make a functional "Leash" in VRchat using OSC as an input controller. <br /> 
Could be adapted to any pullable physbone; EG: A tail. <br />
If you're smarter and want to improve this code, by all means, PLEASE do so. 

## How TF this work??

Here's the prefab from releases but with some meshes for visual help.

There's two systems at play; one to "aim" what direction to move in and the physbone intelf that determines move speed.

On the Aim system, there's 4 Contact Recieverers, a position constraint, and an aim constraint.

4 proximity Contacts (Z+,Z-,X+,X-) are placed around a center point which has an aim constraint with a sender on the end that triggers the proximity contacts. 
1 Position constraint is locked to the ground plane and is tracked to the end of the leash physbone system. This allows it to be free moving wherever the end of the leash is but stay on the correct axis for the aim constraint. As the leash physbone moves around the directional, the aim constraint move along contact sender, triggering all the proximity contacts. We read that for OSC.

![Function Example](https://cdn.discordapp.com/attachments/606734710328000532/1011420984303165500/Example_Gif.gif)

(Z_Positive - Z_Negative) * Leash_Stretch = Vertical  <br />
(X_Positrive - Z_Negative) * Leash_Stretch = Horizontal

Output those two values back to VRC and boom, you're moving in the direction of the arrow based on how stretched the leash is. We use Leash_IsGrabbed as well to confirm it's actually being grabbed along with some other fancy stuff I don't really understand fully.

##

### Known issue

As with RavenBuilds's take on the OSCLeash, using OSC as an input for movement still causes you arms to be locked into desktop pose, please slap some support onto this canny! https://feedback.vrchat.com/feature-requests/p/osc-locks-arms

**TEMPORARY WORKAROUND**: Set "XboxJoystickMovement" to true in the config file. Instead of outputting movement with OSC, this will emulate an Xbox controller joystick! Skipping over the above issue enitely. Might break, dunno. This will probably be removed when VRC fixes the issue.

##

### Running the source:
- Clone the github
- Run `pip install -r requirements.txt` in the directory to install libraries
- Run the python script

### Running Executable
- Download release zip from https://github.com/ZenithVal/OSCLeash/releases/tag/Main
- Extract wherever.
- Run Executable

##

### Setup
Requires VRC3 Avatar SDK.

1. Downlaod & get the program running via one of the above methods.
2. Define config.json setting; EG IP, Port, & paramaters (last bit coming soon)
3. Grab the prefab from the releases https://github.com/ZenithVal/OSCLeash/releases/tag/Main
4. Drop the Prefab onto the root of your avatar (You can scale the prefab down smaller, as long as it's done uniformially and you don't go too small)
5. Set the source of the constraint on "Aim Target" to the end of your "leash"
6. Set the source of the physbone leash to your leash, tail ect, or delete and make your own. 
7. Set "Paramater" on your leash's physbone to "Leash" 
8. Your leash needs to be able to stretch, at least a tiny bit. 

I'll make a setup picture guide later.

#

### Config

| Config | Use | default |
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

#### Custom paramaters 
(Still WIP functionality, the config for them won't change them yet)

| Paramater | Description |
| --- | --- |
|Leash_IsGrabbed | Physbone IsGrabbed value |
|Leash_Stretch | Physbone Stretch percent | 
| Leash_Z+ | Z Positive |
| Leash_Z- | Z Negative |
| Leash_X+ | X Positive |
| Leash_X- | X Negative |

##

### Default Config

```json
{
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "ActiveDelay": 0.1,     
        "InactiveDelay": 0.5,
        "Logging": true,
        "XboxJoystickMovement": false,   
        "Parameters":
        {
                "I GAVE UP ON THESE, THEY DON'T WORK": "if someone knows how, lmk lol",
                "Z_Positive_Param": "/avatar/parameters/Leash_Z+",
                "Z_Negative_Param": "/avatar/parameters/Leash_Z-",
                "X_Positive_Param": "/avatar/parameters/Leash_X+",
                "X_Negative_Param": "/avatar/parameters/Leash_Z-",
                "LeashGrab_Param": "/avatar/parameters/Leash_IsGrabbed",
                "LeashStretch_Param": "/avatar/parameters/Leash_Stretch"
        }
}


```
#
### Credits

- @FrostbyteVR babied me through 90% of the process of making the python script.
- @I5UCC I stared at the code of his ThumbParamsOSC for a long time to learn a bit. Some lines are a carbon copy.
- Someone else did this but it was a closed source executable.
