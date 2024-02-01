
<div align="Center">
    <h3 align="Center">
        <!-- <a>
          <div style="float:right">
            <img src="https://raw.githubusercontent.com/ZenithVal/OSCLeash/main/Resources/VRChatOSCLeash.png" alt="Icon" width="50" >
          </div>
        </a> -->
        <!-- Todo: Make better header one day -->
      A VRChat OSC tool to move a player in the direction of a stretched Physbone. <br>
      For leashes, tails, or even hand holding!
    </h3>
    <div align="Center">
      <p align="Center">
        <a><img alt="Latest Version" src="https://img.shields.io/github/v/tag/ZenithVal/OSCLeash?color=informational&label=Version&sort=semver"></a>
        <a><img alt="Downloads" src="https://img.shields.io/github/downloads/ZenithVal/OSCLeash/total.svg?label=Downloads"></a>
        <br>
        <a href="https://discord.gg/7VAm3twDyy"><img alt="Discord Badge" src="https://img.shields.io/discord/955364088156921867?color=5865f2&label=Discord&logo=discord&logoColor=https%3A%2F%2Fshields.io%2Fcategory%2Fother"/></a>
        <a href="https://github.com/ZenithVal/OSCLeash/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/ZenithVal/OSCLeash?label=Liscense"></a>
      </p>
    </div>
</div>

<!-- Why you looking at the raw readme, this is horrid to read. -->

# Download & Setup
Download and extract the latest OSCLeash zip [from releases](https://github.com/ZenithVal/OSCLeash/releases). <br>
__This app does not provide a model for a Leash at this time.__ <Br>

<details><summary>Setup Steps (Click the Arrow!)</summary>

1. Grab the prefab `(OSCLeash.prefab)` [from releases](https://github.com/ZenithVal/OSCLeash/releases) and drop it into your Unity project.
2. Place the prefab on the root of your model. (**NOT a child of armature**) Don't break prefab!
3. Select the `Compass` object and assign the source of the `Position constraint` to the **first** bone of your leash.
4. You can find `Aim Needle` as a child of compass. Assign the source of the `Aim Constraint` to the **last** bone of your leash.
5. (**Optional**) You can animate the compass object off for remote users using IsLocal. Saves some performance!
6. Enable OSC in VRChat settings. (Or reset OSC if you updated an avatar!) ~ [Tutorial](https://raw.githubusercontent.com/ZenithVal/OSCLeash/main/Resources/HowResetOSC.png)
7. Run the OSCLeash app and get pulled about!
8. Visit [Config](#config) and fine tune settings for your taste

---
</details><br>

If you're having issues, make sure to see the [FAQ](#faq) section. <br>
If all else fails, feel free to reach out in the #OSC-Talkin channel in [my Discord](https://discord.gg/7VAm3twDyy) 

<br>


# Config
After running OSCleash at least once, an OSCLeash.json file will be generated. <br>
You can open the json file in your favorite text editor and fine tune your OSCLeash.

<details><summary>Table of Configation settings</summary>

---

| Value                 | Info                                                           | Default     |
|:--------------------- | -------------------------------------------------------------- |:-----------:|
| IP                    | Address to send OSC data to                                    | 127.0.0.1   |
| ListeningPort         | Port to listen for OSC data on                                 | 9001        |
| Sending port          | Port to send OSC data to                                       | 9000        |
| RunDeadzone           | Minimum Stretch % to cause running                             | 0.70        |
| WalkDeadzone          | Minimum Stretch % to start walking                             | 0.15        |
| StrengthMultiplier    | Multiplies speed values but they can't go above (1.0)          | 1.2         |
| UpDownCompensation    | % of compensation to apply for Up/Down angles                  | 1.0         |
| UpDownDeadzone        | If Up/Down pulling is above this %, disable movement           | 0.75        |
| FreezeIfPosed         | Freeze the user in place if the leash is posed                 | false       | 
| TurningEnabled        | Enable turning functionality                                   | false       |
| TurningMultiplier     | Adjust turning speed                                           | 0.75        |
| TurningDeadzone       | Minimum Stretch % to start turning                             | .15         |
| TurningGoal           | Goal degree range for turning. (degrees, 0-144) (0° to 144°)   | 90          |
| ActiveDelay           | Delay between OSC messages while the leash is being grabbed    | 0.1 seconds |
| InactiveDelay         | Delay between non-essential OSC messages                       | 0.5 seconds |
| Logging               | Logging for Directional compass inputs                         | false       |
| XboxJoystickMovement  | Deprecrated, Alternate movement input method                   | false       |
| PhysboneParameters    | A list of Physbones to use as leashes                          | see below   |
| DirectionalParameters | A list of contacts to use for direction calculation            | see below   |
---
</details><br>

<details><summary>Default Config.json</summary>

---
```json
{
        "IP": "127.0.0.1",
        "ListeningPort": 9001,
        "SendingPort": 9000,
        "RunDeadzone": 0.70,
        "WalkDeadzone": 0.15,
        "StrengthMultiplier": 1.2,
        "TurningEnabled": false,
        "TurningMultiplier": 0.75,
        "TurningDeadzone": 0.15,
        "TurningGoal": 90,
        "ActiveDelay": 0.01,
        "InactiveDelay": 0.5,
        "Logging": false,
        "XboxJoystickMovement": false,
        
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
```
---
</details><br>

<details><summary>Physbone Parameters</summary>

---
This is a list of all the Physbones you're using with OSCLeash. <br> 

```json
        "PhysboneParameters":
        [
            "Leash",
            "Leash2",
            "Leash3"
        ],
```

OSCLeash listens for the _IsGrabbed and _Stretch parameters for every listed leash.

---
</details><br>

<details><summary>Multiple Leashes</summary>

---
This requires an understanding of Physbones Parameters, Animations, and Constraints. <br/>
 - Add a new source to `Compass` and `Aim Needle` for each extra leash. 0 Weight by default
 - Depending on which leash `_IsGrabbed`, animate the weights to match the Grabbed leash.

 ---
</details><br>

<details><summary>Turning Functionality</summary>

---
**⚠️ Motion sickness warning ⚠️** 

If you want to enable this feature, set `TurningEnabled` to **True**.<br/>
`Currently Supports North, East, South, & West`<br/>

If you had a leash up front and you want to turn to match the direction it's pulled from (EG: a Collar with the leash on the front) Set set the parameter on your Leash Physbone and config to `Leash_North`.

<details><summary>Config File</summary>

```json
        "PhysboneParameters":
        [
            "Leash_North"
        ],
```
</details><br>

We parse the direction to control turning so `"Tail_South"` would work. <br>
Whenever this leash is grabbed and pulled past the deadzone it will begin to turn. <br/>It will continue to turn until it is greater than the TurningDeadzone value. <br/>

---

<details><summary>Nerd Stuff</summary>

Here's the simplified logic of the system.

```python
if LeashDirection == "North" and Z_Positive < TurningGoal:
    TurningSpeed = ((X_Negative - X_Positive) * LeashStretch * TurningMultiplier)
```
</details><br>

</details><br>

<details><summary>Extra stuff for nerds!</summary>

# How OSCLeash works

## Step 1: Get Leash Physbone parameters

We receive the Leash_Stretch and Leash_Grabbed parameters.  
If Leash_Grabbed becomes true, we begin reading Leash_Stretch 

We'll use these values in this example:  

> Leash_IsGrabbed = True<br/>Leash_Stretch = $0.95$


## Step 2: Gather Directional Contact values

<img src="https://cdn.discordapp.com/attachments/606734710328000532/1011420984303165500/Example_Gif.gif" title="" alt="Function Example" width="502"> 
4 Contacts (Blue) surround a object with an aim constraint and a contact at the tip. (Yellow) <br/>

Based on where the constraint is aimed, it will give us 4 values. <br/>

If it was pointing South-South-West, we would get:

> Leash_Z+ = $0.0$<br/>Leash_Z- = $0.75$<br/>Leash_X+ = $0.0$<br/>Leash_X- = $0.25$ 


## Step 3: Math

Math is fun. Add the negative and positive contacts & multiply by the stretch value.

> (Z_Positive - Z_Negative) * Leash_Stretch = Vertical<br/>(X_Positive - X_Negative) * Leash_Stretch = Horizontal 

So our calculation for speed output would look like:

> $(0.0 - 0.75) * 0.95 = -0.7125$ = Veritcal<br/>$(0.0 - 0.25) * 0.95 = -0.2375$ = Horizontal


## Step 4: Outputs

If either value is above the walking deadzone (default 0.15) we start outputting them instead of 0. <br/>If either value is above the running deadzone (0.7) we tell the player to run (x2 speed)

All movement values are relative to the VRC world's movement speed limits. <br/>So we'd be moving at $142.5$% speed south and $47.5$% speed to the West. 

If the values are below the deadzones or _IsGrabbed is false, send 0s for the OSC values once to stop movement. 

</details>

<br>


# FAQ

<details><summary>Click to Expand</summary>
<br>
<!--
**Q:** <br>
**A:** 
-->

**Q:** OSCLeash says grabbed but I don't get moved. <br>
**A1:** This can happen if your leash physbone does not have any stretch. <br>
**A2:** Make sure self interaction is `enabled`, it's needed for the direction calculation.

---

**Q:** I did avatar setup correctly but the app isn't getting ANYTHING at all. <br>
**A1:** Make sure to reset OSC, this can be done manually by deleting the OSC and OSC.bak folders at `C:\Users\(Your username)\AppData\LocalLow\VRChat\VRChat` <br>

---

**Q:** The direction it pulls is not accurate <br>
**A1:** Make sure your physbone isn't too limited in angle or too short! If it can't move it can't get an accurate location. <br>
**A2:** If your scaling up very large, scale down the `Compass` game object to compensate ~ contacts have a max size!

---

**Q:** How can I run OSCLeash with my other OSC apps? <br>
**A:** Try out an OSC Router, like [OSC Switch](https://github.com/KaleidonKep99/OpenSoundControlSwitch). I'll add OSCquery support when they it can whitelist parameters (Or when I get around to a performant C# rewrite) <br>

---

**Q:** My Question/Issue isn't answered above <br>
**A:** [Discord](https://discord.gg/7VAm3twDyy) or [Git Issue](https://github.com/ZenithVal/OSCLeash/issues)

</details><br>

# Credits & Liscenses

- App Rope Icon | [Game-icons.net](https://game-icons.net/1x1/delapouite/locked-heart.html) under [CC by 3.0](https://creativecommons.org/licenses/by/3.0/)
- @ALeonic is responsible for a majority of v2 (Threading is scary!)
- @FrostbyteVR walked me through the proccess of making v1
- Someone else did this but it was a closed source executable