from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from threading import Lock, Thread

from Controllers.DataController import Leash
from Controllers.ThreadController import Program


#TODO: Find a way to trigger the run thread when grabbed is true
class Package:
    
    def __init__(self):
        self.__dispatcher = Dispatcher()
        self.__statelock = Lock()


    def listenTest(self, leash: Leash):
        print(leash.Name)

    def listen(self, leash: Leash):
        # Paramaters to read per leash
        self.__dispatcher.map(f'/avatar/parameters/{leash.Name}_Stretch',self.__updateStretch, leash) #Physbone Stretch Value
        self.__dispatcher.map(f'/avatar/parameters/{leash.Name}_IsGrabbed',self.__updateGrabbed, leash) #Physbone Grab Status
        
        self.__dispatcher.map(f'/avatar/parameters/{leash.Z_Positive_ParamName}',self.__updateZ_Positive, leash) #Z Positive
        self.__dispatcher.map(f'/avatar/parameters/{leash.Z_Negative_ParamName}',self.__updateZ_Negative, leash) #Z Negative
        self.__dispatcher.map(f'/avatar/parameters/{leash.X_Positive_ParamName}',self.__updateX_Positive, leash) #X Positive
        self.__dispatcher.map(f'/avatar/parameters/{leash.X_Negative_ParamName}',self.__updateX_Negative, leash) #X Negative

    def __updateZ_Positive(self, addr, extraArgs, value):
        try:
            leash: Leash = extraArgs[0]
            self.__statelock.acquire()
            leash.Z_Positive = value
            self.__statelock.release()
            #print("Z+: {}".format(leash.Z_Positive))
        except Exception as e:
            print(e)
            exit()

    def __updateZ_Negative(self, addr, extraArgs, value):
        try:
            leash: Leash = extraArgs[0]
            self.__statelock.acquire()
            leash.Z_Negative = value
            self.__statelock.release()
            #print("Z-: {}".format(leash.Z_Negative))
        except Exception as e:
            print(e)
            exit()

    def __updateX_Positive(self, addr, extraArgs, value):
        try:
            leash: Leash = extraArgs[0]
            self.__statelock.acquire()
            leash.X_Positive = value
            self.__statelock.release()
            #print("X+: {}".format(leash.X_Positive))
        except Exception as e:
            print(e)
            exit()

    def __updateX_Negative(self, addr, extraArgs, value):
        try:
            leash: Leash = extraArgs[0]
            self.__statelock.acquire()
            leash.X_Negative = value
            self.__statelock.release()
            #print("X-: {}".format(leash.X_Negative))
        except Exception as e:
            print(e)
            exit()

    def __updateStretch(self, addr, extraArgs, value):
        try:
            leash: Leash = extraArgs[0]
            self.__statelock.acquire()
            leash.Stretch = value
            self.__statelock.release()
            #print("Stretch: {}".format(leash.Stretch))
        except Exception as e:
            print(e)
            exit()
            
    def __updateGrabbed(self, addr, extraArgs, value):
        try:
            leash: Leash = extraArgs[0]
            program = Program()
            
            self.__statelock.acquire()
            leash.Grabbed = value
            if leash.Grabbed:
                Thread(target=program.leashRun, args=(leash,)).start()
            self.__statelock.release()

            #print("Grabbed: {}".format(leash.Grabbed))
        except Exception as e:
            print(e)
            exit()
    
    def runServer(self, IP, Port):
        server = osc_server.ThreadingOSCUDPServer(
        (IP, Port), self.__dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()