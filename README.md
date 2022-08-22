# OSCLeash

A simple system to make a functional "Leash" in VRC using OSC. Can be adapated for different sources like a tail.
If you're smarter and want to improve this code, by all means, PLEASE do so.


### Prerequisites:
- Python 3.10
- Python-osc 1.8.0 
https://pypi.org/project/python-osc/

### Setup
1. Define IP and ports in config.json
2. Drop the Prefab onto the root of your avatar
3. Assign the stuff

uh....


### Parameters

| Parameter | Description |
| --- | --- |
|Leash_IsGrabbed | Physbone IsGrabbed Value
|Leash_Stretch | Physbone Stretch Status
| Z+ | Z Positive |
| Z- | Z Negative |
| X+ | Z Positive |
| X- | Z Negative |

### Credits

- @FrostbyteVR babied me through 90% of the process of making the python script.
- @I5UCC I stared at the code of his ThumbParamsOSC for a long time to learn a bit. The setup for the config reading is also from that.
