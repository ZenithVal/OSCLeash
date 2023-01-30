import math
from pprint import pprint
import pygetwindow as gw


class LeashActions:
    def __init__(self, config, in_queue, out_queue) -> None:
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.config = config
        self.prefix = "/avatar/parameters/"
        self.posVector = [0.0,0.0,0.0]
        self.negVector = [0.0,0.0,0.0]
        self.isGrabbed = False
        self.stretch = 0.0
        self.activeLeashes = []
        self.scale = self.config['ScaleDefault']
        self.lastAvatar = None
        self.isDisabled = False

    def updateDirectional(self, address: str, magnitude: float):
        if self.isGrabbed and not self.isDisabled:
            direction = address[len(self.prefix):]
            # pprint(f"OSCServer: {direction} {magnitude}")
            if direction == self.config['DirectionalParameters']['Z_Positive_Param']:
                self.posVector[2] = magnitude
            elif direction == self.config['DirectionalParameters']['Z_Negative_Param']:
                self.negVector[2] = magnitude
            elif direction == self.config['DirectionalParameters']['X_Positive_Param']:
                self.posVector[0] = magnitude
            elif direction == self.config['DirectionalParameters']['X_Negative_Param']:
                self.negVector[0] = magnitude
            # elif direction == self.config['DirectionalParameters']['Y_Positive_Param']: # Y is not used in this project yet
            #     self.posVector[1] = magnitude
            # elif direction == self.config['DirectionalParameters']['Y_Negative_Param']:
            #     self.negVector[1] = magnitude
            
            #print(f'leash: {self.combinedVector()}')
            self.sendUpdate()

    def updateStretch(self, address: str, magnitude: float):
        if self.isGrabbed and not self.isDisabled:
            name = address[len(self.prefix):]
            suffix = "_Stretch"
            name = name[:-len(suffix)]
            #pprint(name)
            if name == self.activeLeashes[0]:
                self.stretch = magnitude
                # pprint(f"Stretchy: {address} {magnitude}")
            pass
        elif self.isGrabbed and self.isDisabled:
            self.stretch = 0.0

    def updateGrabbed(self, address: str, grabbed: bool):
        name = address[len(self.prefix):]
        suffix = "_IsGrabbed"
        name = name[:-len(suffix)]
        pprint(name)
        if grabbed:
            if name not in self.activeLeashes:
                self.activeLeashes.append(name)
        else:         
            if name in self.activeLeashes:
                self.activeLeashes.remove(name)
        
        self.isGrabbed = len(self.activeLeashes) > 0
        if self.isGrabbed and not self.isDisabled:
            # Bring VRChat window to Foreground
            if self.config['BringGameToFront'] and self.config['XboxJoystickMovement']:
                windows = gw.getWindowsWithTitle(self.config['GameTitle'])
                # Find the window with the exact title
                for window in windows:
                    if window.title == self.config['GameTitle']:
                        try:
                            window.activate()
                        except (SyntaxError, gw.PyGetWindowException):
                            print("Error: Could not bring {} to front?".format(self.config['GameTitle']))
                            pass
                        break
        else:
            self.stretch = 0.0
            self.posVector = [0.0,0.0,0.0]
            self.negVector = [0.0,0.0,0.0]
            self.sendUpdate()

        # print(f"OSCServer: {address} {grabbed} {self.isGrabbed}")

    def updateScale(self, address: str, variable: any):
        # Checking if the variable is a string, if it is, it's the avatar ID instead of the new scale
        if isinstance(variable, str):
            if variable != self.last_avatar:
                self.last_avatar = variable
                # self.scale = self.config['ScaleDefault']
                self.scale = self.config['ScaleDefault']
                self.isDisabled = False
        else:
            if variable <= self.config['ScaleDefault']:
                self.scale = variable
            else:
                self.scale = self.config['ScaleDefault']
        self.sendUpdate()


    def updateDisable(self, address: str, disabled: bool):
        self.isDisabled = disabled
    
    
    def combinedVector(self):
        if self.stretch >= self.config['WalkDeadzone']:
            modifier = self.stretch * self.config['StrengthMultiplier'] * self.scaleCurve(self.scale)
        else:
            modifier = 0
        return [self.clamp(x*modifier)-self.clamp(y*modifier) for x,y in zip(self.posVector, self.negVector)]

    def scaleCurve(self, inputScale):
        if self.config['ScaleSlowdownEnabled']:
            # magic math i did while high
            vector = [10, 5]
            scale = (inputScale/self.config['ScaleDefault']) * 0.25
            speed = math.sqrt(vector[0]**2 + vector[1]**2)
            curve = scale / math.log(speed + 1)
            vector[0] *= curve
            # vector[1] *= curve
            if vector[0] == 0:
                return self.scaleCurve(inputScale+0.01)
            return vector[0]
        else:
            return 1.0
    
    def __toDict__(self) -> str:
        return {"LeashActions": {
                'vector': self.combinedVector(),
                'grabbed': self.isGrabbed, 
                'stretch': self.stretch,
                'active-leashes': self.activeLeashes,
                'scale': self.scale}}
    
    def sendUpdate(self):
        self.out_queue.put(self.__toDict__())
    
    @staticmethod
    def clamp(num):
        return -1 if num < -1 else 1 if num > 1 else num
