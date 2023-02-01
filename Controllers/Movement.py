import math
import time
from colorama import Fore
from functools import wraps
from Throttle import ThrottleDecorator


DIRECTION_VECTORS = {'North': (0, 0, 1),
                     'South': (0, 0, -1),
                     'East': (1, 0, 0),
                     'West': (-1, 0, 0)}                    


class MovementController:
    def __init__(self, config, in_queue, gui_queue) -> None:
        self.config = config
        self.in_queue = in_queue
        self.gui_queue = gui_queue
        self.gamepad = None
        self.runButton = None

        
    def setup_xbox_movement(self):
        # Add controller input if user installs and enables vgamepad
        if self.config['XboxJoystickMovement']:
            try:
                import vgamepad as vg
                self.gamepad = vg.VX360Gamepad()
                self.runButton = vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER
            except Exception as e:
                print(Fore.RED + f'Error: {e}\nWarning: Switching to default OSC settings. Please wait...\n Check documentation for controller emulator tool.' + Fore.RESET)
                time.sleep(1)
                self.config['XboxJoystickMovement'] = False
                
    def makeMovement(self, leashData):
        if self.config['XboxJoystickMovement']: 
            #Xbox Emulation: REMOVE LATER WHEN OSC IS FIXED
            offset = 0.65

            self.gamepad.left_joystick_float(x_value_float=self.map_with_clamp(float(leashData['vector'][0]), offset*-1.0, offset, -1.0, 1.0), 
                                             y_value_float=self.map_with_clamp(float(leashData['vector'][2]), offset*-1.0, offset, -1.0, 1.0))
            if self.config['TurningEnabled']: 
                self.gamepad.right_joystick_float(x_value_float=self.map_with_clamp(float(leashData['turn']), -0.5, 0.5, -1.0, 1.0), 
                                                  y_value_float=0.0)
            # Run check
            if leashData['stretch']>=self.config['RunDeadzone']:
                self.gamepad.press_button(button=self.runButton)      
            else:
                self.gamepad.release_button(button=self.runButton)
            self.gamepad.update()
            #time.sleep(0.01)

        else:
            #Normal OSC outputs  function                    
            bundle = [
                ("/input/Vertical", leashData['vector'][2]),
                ("/input/Horizontal", leashData['vector'][0]),
                ("/input/Run", leashData['stretch']>=self.config['RunDeadzone'])
            ]
            if self.config['TurningEnabled']:
                turnOut = leashData['turn']
                if abs(turnOut) < self.config['TurningDeadzone']:
                    turnOut = 0.0
                bundle.append(("/input/LookHorizontal", turnOut))
            return bundle
                
    def calculateTurn(self, leashData):
        try:
            leashCardinal = leashData['active-leashes'][-1].split('_')[1]
        except:
            leashCardinal = 'North'
        return self.proportionalTurn(leashData['vector'], self.config['TurningKp'], leashCardinal)
    
    def throttle(func, delay):
        def decorator(func):
            decorator = ThrottleDecorator(func, delay)
            return wraps(func)(decorator)
        return decorator

    def sendMovement(self):
        @self.throttle(self.config['ActiveDelay'])
        def _sendMovement(self):
            if not self.in_queue.empty():
                queueData = self.in_queue.get(block=False)
                leashData = queueData['LeashActions']
                if self.config['TurningEnabled']:
                    turn = self.calculateTurn(leashData)
                else:
                    turn = 0.0
                leashData['turn'] = turn
                if leashData['stretch'] > self.config['WalkDeadzone']:
                    pass
                else:
                    leashData['vector'] = [0.0,0.0,0.0]
                
                self.gui_queue.put(leashData, block=False)
                return self.makeMovement(leashData)
        return _sendMovement(self)
        
    @staticmethod
    def proportionalTurn(current_vector, kp=1, direction='North'):
        target_direction = DIRECTION_VECTORS[direction]
        
        #thanks ChatGPT <3
        norm = math.sqrt(current_vector[0]**2 + current_vector[1]**2 + current_vector[2]**2)
        if norm == 0:
            return 0
        current_direction = (current_vector[0]/norm, current_vector[1]/norm, current_vector[2]/norm)
        
        if direction == 'North':
            error_vector = (current_direction[0] - target_direction[0])
        elif direction == 'South':
            error_vector = -(current_direction[0] - target_direction[0])
        elif direction == 'East':
            error_vector = (current_direction[2] - target_direction[2])
        elif direction == 'West':
            error_vector = -(current_direction[2] - target_direction[2])    
        
        return kp * error_vector
            
    # Stolen from @NicoHood and @st42 (github users) in a discussion about the
    # map() function being weird
    # https://github.com/arduino/ArduinoCore-API/issues/51#issuecomment-87432953
    @staticmethod
    def map_with_clamp(x, in_min, in_max, out_min, out_max):
        # if input is smaller/bigger than expected return the min/max out ranges value
        if x < in_min:
            return out_min
        elif x > in_max:
            return out_max

        # map the input to the output range.
        # round up if mapping bigger ranges to smaller ranges
        elif (in_max - in_min) > (out_max - out_min):
            return (x - in_min) * (out_max - out_min + 1) / (in_max - in_min + 1) + out_min
        # round down if mapping smaller ranges to bigger ranges
        else:
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
