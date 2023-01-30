import time
import vgamepad as vg
gamepad = vg.VX360Gamepad()
time.sleep(3)
# The lowest value that VRChat actually responds to:
#gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.286)
gamepad.right_joystick_float(x_value_float=0.3, y_value_float=0.0)
gamepad.update()
print("Starting")
while True:
    time.sleep(1)