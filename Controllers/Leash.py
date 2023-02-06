import math
from pprint import pprint
import pygetwindow as gw
from timing_util import timing

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
        self.maxQ = 10

    def updateDirectional(self, address: str, magnitude: float):
        if self.isGrabbed and not self.isDisabled and self.outQueueSize() < self.maxQ:
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
            elif direction == self.config['DirectionalParameters']['Y_Positive_Param']:
                self.posVector[1] = magnitude
            elif direction == self.config['DirectionalParameters']['Y_Negative_Param']:
                self.negVector[1] = magnitude
            
            #print(f'leash: {self.combinedVector()}')
            self.sendUpdate()

    def updateStretch(self, address: str, magnitude: float):
        if self.isGrabbed and not self.isDisabled and self.outQueueSize() < self.maxQ:
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
        if name.endswith(suffix):
            name_trimmed = name[:-len(suffix)]
        else:
            name_trimmed = name
        pprint(f"{name_trimmed} event: {grabbed}")
        if grabbed:
            if name_trimmed not in self.activeLeashes:
                self.activeLeashes.append(name_trimmed)
        else:         
            if name_trimmed in self.activeLeashes:
                self.activeLeashes.remove(name_trimmed)
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
            # Clear the out queue
            self.clearOutQueue()
                
            self.stretch = 0.0
            self.posVector = [0.0,0.0,0.0]
            self.negVector = [0.0,0.0,0.0]
            self.sendUpdate()

        # print(f"OSCServer: {address} {grabbed} {self.isGrabbed}")

    def updateScale(self, address: str, variable: any):
        # Checking if the variable is a string, if it is, it's the avatar ID instead of the new scale
        if isinstance(variable, str):
            if variable != self.lastAvatar:
                self.lastAvatar = variable
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
        if disabled:
            self.activeLeashes.clear()
            self.updateGrabbed(address, True)
        else:
            self.activeLeashes.clear()
            self.updateGrabbed(address, False)
     
    def combinedVector(self):
        if self.stretch >= self.config['WalkDeadzone']:
            modifier = self.stretch * self.config['StrengthMultiplier'] * self.scaleCurve(self.scale)
        else:
            modifier = 0
        
        vector = [self.clamp(x*modifier)-self.clamp(y*modifier) for x,y in zip(self.posVector, self.negVector)]
        rawVector = [self.clamp(x)-self.clamp(y) for x,y in zip(self.posVector, self.negVector)]
        # vector correction
        vectorMagnitude = math.sqrt(rawVector[0]**2 + rawVector[1]**2 + rawVector[2]**2)
        # print(f"Vector {vector} RawVector: {rawVector} nStretch: {self.stretch} vectorMagnitude: {vectorMagnitude}")
        print(f"Pre math Vector: {vector} RawVector: {rawVector} nStretch: {self.stretch} vectorMagnitude: {vectorMagnitude}")
        #correct vector by scaling it with the magnitude of the raw vector
        if vectorMagnitude > 0:
            vector = [x/vectorMagnitude for x in vector]

        print(f"Post Math Vector {vector} RawVector: {rawVector} nStretch: {self.stretch} vectorMagnitude: {vectorMagnitude}")
        
                    
        # print("YCompensate:")
        # try:
        #     #YCompensate = 1.0/(self.posVector[0]+self.negVector[0]+self.posVector[2]+self.negVector[2])
        #     #xyz = (self.posVector[0]-self.negVector[0]+self.posVector[1]-self.negVector[1]+self.posVector[2]-self.negVector[2])
        #     #xyz = vector[0]+vector[1]+vector[2]
        #     xyz = (self.posVector[0]+self.negVector[0]+self.posVector[1]+self.negVector[1]+self.posVector[2]+self.negVector[2])
        #     print(xyz)
        #     #xz = (self.posVector[0]-self.negVector[0]+self.posVector[2]-self.negVector[2])
        #     #xz = vector[0]+vector[2]
        #     xz = (self.posVector[0]+self.negVector[0]+self.posVector[2]+self.negVector[2])
        #     print(xz)
        #     YCompensate = xyz/xz
        # except ZeroDivisionError:
        #     YCompensate = 1.0
        # print(YCompensate)

        # TODO Make "0.4" config option
        if (self.posVector[1] < 0.4 and self.negVector[1] < 0.4) or not self.config['VerticalMovement']:
            vector[0] = self.clamp(vector[0])
            vector[1] = 0.0
            vector[2] = self.clamp(vector[2])
            return vector

        return vector
    def clearOutQueue(self):
        while not self.out_queue.qsize() == 0:
            self.out_queue.get()
            self.out_queue.task_done()
                
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

    def outQueueSize(self) -> int:
        return self.out_queue.qsize()

    def sendUpdate(self):
        if not self.outQueueSize() == 1:
            self.clearOutQueue()
        self.out_queue.put(self.__toDict__())
    
    @staticmethod
    def clamp(num) -> float:
        return -1.0 if num < -1.0 else 1.0 if num > 1.0 else num
