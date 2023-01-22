import time
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from threading import Lock, Thread

from Controllers.DataController import Leash
from Controllers.ThreadController import Program

class Package:
    
    def __init__(self, leashCollection, out_queue):
        self.__dispatcher = Dispatcher()
        self.__statelock = Lock()
        self.out_queue = out_queue
        self.last_avatar = None
        try:
            if len(leashCollection) == 0: raise Exception("Leash collection empty within Package manager.")
            self.leashes = leashCollection
        except Exception as e:
            print(e)
            time.sleep(5)

    def listen(self):
        # parameters to read per leash
        self.listenLeash(self.leashes)
        self.listenParam(self.leashes[0])
        self.listenExtra(self.leashes[0])

    def listenLeash(self, leashCollection):
        for leash in leashCollection:
            self.__dispatcher.map(f'/avatar/parameters/{leash.Name}_Stretch',self.__updateStretch, leash) #Physbone Stretch Value
            self.__dispatcher.map(f'/avatar/parameters/{leash.Name}_IsGrabbed',self.__updateGrabbed, leash) #Physbone Grab Status

    def listenParam(self, leash: Leash):
        self.__dispatcher.map(f'/avatar/parameters/{leash.Z_Positive_ParamName}',self.__updateZ_Positive) #Z Positive
        self.__dispatcher.map(f'/avatar/parameters/{leash.Z_Negative_ParamName}',self.__updateZ_Negative) #Z Negative
        self.__dispatcher.map(f'/avatar/parameters/{leash.X_Positive_ParamName}',self.__updateX_Positive) #X Positive
        self.__dispatcher.map(f'/avatar/parameters/{leash.X_Negative_ParamName}',self.__updateX_Negative) #X Negative

    def listenExtra(self, leash: Leash):
        self.__dispatcher.map(f'/avatar/parameters/{leash.settings.ScaleParameter}',self.__updateScale)
        self.__dispatcher.map(f'/avatar/change',self.__updateScale)
        self.__dispatcher.map(f'/avatar/parameters/{leash.settings.DisableParameter}',self.__updateDisable)

    def __updateDisable(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                leash.Disabled = value
                self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)

    def __updateScale(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                # If the avatar changed, just set it to 100%
                if isinstance(value, str):
                    if value != self.last_avatar:
                        self.last_avatar = value
                        leash.CurrentScale = leash.settings.ScaleNormal
                        leash.Disabled = False
                else:
                    leash.CurrentScale = value
                self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)

    def __updateZ_Positive(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                leash.Z_Positive = value
                self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)

    def __updateZ_Negative(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                leash.Z_Negative = value
                self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)

    def __updateX_Positive(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                leash.X_Positive = value
                self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)

    def __updateX_Negative(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                leash.X_Negative = value
                self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)


    def __updateStretch(self, addr, extraArgs, value):
        try:
            leash: Leash = extraArgs[0]
            self.__statelock.acquire()
            leash.Stretch = value
            self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)
            
    def __updateGrabbed(self, addr, extraArgs, value):
        try:
            currLeash: Leash = extraArgs[0]
            self.__statelock.acquire()
            currLeash.Grabbed = value

            threadInProgress = False
            if currLeash.Grabbed:
                for leash in self.leashes:
                    if not leash.Name == currLeash.Name and leash.Active:
                        threadInProgress = True
                
                if not threadInProgress:
                    program = Program()
                    currLeash.Active = True
                    Thread(target=program.leashRun, args=(currLeash, 0, self.out_queue)).start()

            self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)
    
    def runServer(self, IP, Port):
        try:
            osc_server.ThreadingOSCUDPServer((IP, Port), self.__dispatcher).serve_forever()
        except Exception as e:
            print('\x1b[1;31;41m' + '                                                                    ' + '\x1b[0m')
            print('\x1b[1;31;40m' + '   Warning: An application might already be running on this port!   ' + '\x1b[0m')
            print('\x1b[1;31;41m' + '                                                                    \n' + '\x1b[0m')
            print(e)
            # No delay here as error message is displayed somewhere else when this fails