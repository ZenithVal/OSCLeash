from pythonosc.dispatcher import Dispatcher
from threading import Lock,Thread,Timer

#TODO: Create method to collect data from 
class Package:
    
    __dispatcher = Dispatcher()
    __statelock = Lock()

    def receiveData(self):
        # Paramaters to read
        Package.__dispatcher.map("/avatar/parameters/",self.OnRecieve) #Z Positive

    def OnRecieve(address,value):
        print("\nThe address is:",address,"\nThe value is:",value)
       
