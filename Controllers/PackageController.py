import time
import ctypes #Required for colored error messages.
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from threading import Lock, Thread

from Controllers.DataController import Leash
from Controllers.ThreadController import Program

class Package:
    
    def __init__(self, leashCollection):
        self.__dispatcher = Dispatcher()
        self.__statelock = Lock()
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

    def listenLeash(self, leashCollection):
        for leash in leashCollection:
            self.__dispatcher.map(f'/avatar/parameters/{leash.Name}_Stretch',self.__updateStretch, leash) #Physbone Stretch Value
            self.__dispatcher.map(f'/avatar/parameters/{leash.Name}_IsGrabbed',self.__updateGrabbed, leash) #Physbone Grab Status
            self.__dispatcher.map(f'/avatar/parameters/{leash.Name}_IsPosed',self.__UpdatePosed, leash) #Physbone Grab Status

    def listenParam(self, leash):
        self.__dispatcher.map(f'/avatar/parameters/{leash.Z_Positive_ParamName}',self.__updateZ_Positive) #Z Positive
        self.__dispatcher.map(f'/avatar/parameters/{leash.Z_Negative_ParamName}',self.__updateZ_Negative) #Z Negative

        self.__dispatcher.map(f'/avatar/parameters/{leash.X_Positive_ParamName}',self.__updateX_Positive) #X Positive
        self.__dispatcher.map(f'/avatar/parameters/{leash.X_Negative_ParamName}',self.__updateX_Negative) #X Negative

        #Right now Y+ and - are only used for compensation, maybe in the future we'll actually move the player up down.
        self.__dispatcher.map(f'/avatar/parameters/{leash.Y_Positive_ParamName}',self.__updateY_Positive) #Y Positive
        self.__dispatcher.map(f'/avatar/parameters/{leash.Y_Negative_ParamName}',self.__updateY_Negative) #Y Negative

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

    def __updateY_Positive(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                leash.Y_Positive = value
                self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)

    def __updateY_Negative(self, addr, value):
        try:
            for leash in self.leashes:
                self.__statelock.acquire()
                leash.Y_Negative = value
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
                    Thread(target=program.leashRun, args=(currLeash,)).start()

            self.__statelock.release()
        except Exception as e:
            print(e)
            time.sleep(5)
    
    def __UpdatePosed(self, addr, extraArgs, value):
        try:
            currLeash: Leash = extraArgs[0]
            self.__statelock.acquire()
            currLeash.Posed = value
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