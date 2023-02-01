from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from Controllers.Leash import LeashActions
from Controllers.Movement import MovementController
from Controllers.Bootstrap import bootstrap, printInfo
import PySimpleGUI as sg
from queue import LifoQueue as Queue
import asyncio
import darkdetect
import os
from colorama import init, Fore
import socket
init() # Initialize colorama
config = bootstrap()
leashCollection = [x for x in config["PhysboneParameters"]]
printInfo(config)


def dispatcherMap(dispatcher: Dispatcher, actions: LeashActions):
    for leash in leashCollection:
            dispatcher.map(f'/avatar/parameters/{leash}_Stretch', actions.updateStretch)
            dispatcher.map(f'/avatar/parameters/{leash}_IsGrabbed', actions.updateGrabbed)

    for v in config['DirectionalParameters'].values():
        dispatcher.map(f'/avatar/parameters/{v}', actions.updateDirectional)
    
    dispatcher.map(f'/avatar/parameters/{config["ScaleParameter"]}', actions.updateScale)
    dispatcher.map(f'/avatar/parameters/{config["DisableParameter"]}', actions.updateDisable)
    dispatcher.map(f'/avatar/change', actions.updateScale)

       
class App():            
    def __init__(self):
        sg.theme(config['GUITheme'])   # Add a touch of color
        # All the stuff inside your window.
        # ToDo prepolulate with multiple sections for Physbone names in Config.json
        self.mainLayout = [  [sg.Text('Leash Name:'), (sg.Text('Null', key='leash-name'))],
                    [sg.Text('Leash X:'), (sg.Text('Null', key='leash-x'))],
                    [sg.Text('Leash Z:'), (sg.Text('Null', key='leash-z'))],
                    [sg.Text('Leash Turn:'), (sg.Text('Null', key='leash-turn'))],
                    [sg.Text('Current Scale:'), (sg.Text('Null', key='current-scale'))],]

                            
        # Create the Window
        self.window = sg.Window('OSCLeash - GUI', self.mainLayout, enable_close_attempted_event=True)
        
        # Event Loop to process "events" and get the "values" of the inputs
    
    async def run(self, in_q: Queue, out_q: Queue):    
        self.window.finalize()
        self.window.set_min_size((250, 100))
        while True:
            event, values = self.window.read(0)
            if event == sg.WIN_CLOSED or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT: # if user closes window
                out_q.put("gui-exit")
                raise SystemExit
            if in_q != None and in_q.qsize() > 0:
                values = in_q.get()
                if config['Logging']:
                    print(values) # Debug print of gui values
                if len(values['active-leashes']):
                    self.window['leash-name'].update(values['active-leashes'][-1])
                else:
                    self.window['leash-name'].update("None")
                self.window['leash-x'].update(values['vector'][0])
                self.window['leash-z'].update(values['vector'][2])
                self.window['leash-turn'].update(values['turn'])
                self.window['current-scale'].update(str(round(values['scale']/config['ScaleDefault']*100))+"%")
            await asyncio.sleep(0)

# Thanks again, ChatGPT!
def checkBindable(host, port, timeout=5.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.bind((host, port))
        sock.close()
        return True
    except:
        return False
    
    
async def init_main(in_q: Queue, out_q: Queue, gui_q: Queue):
    # Start OSC System    
    dispatcher = Dispatcher()
    server = AsyncIOOSCUDPServer((config['IP'], config['ListeningPort']), dispatcher, asyncio.get_event_loop())
    if not checkBindable(config['IP'], config['ListeningPort']):
        print(Fore.RED + "Failed to bind to port, is another instance of OSCLeash running?", Fore.RESET)
        raise SystemExit

    transport, protocol = await asyncio.wait_for(server.create_serve_endpoint(), 5)  # Create datagram endpoint and start serving
    client = SimpleUDPClient(config['IP'], config['SendingPort'])
    
    actions = LeashActions(config, in_q, out_q)
    dispatcherMap(dispatcher, actions)
    movement = MovementController(config, out_q, gui_q)
    movement.setup_xbox_movement()


    while True:
        
        if config['Logging'] and not ['DisableGUI']:
            if not gui_q.empty():
                print(gui_q.get(block=False))
                
        bundle = movement.sendMovement()
        if bundle is not None: 
            for msg in bundle:
                client.send_message(msg[0], msg[1])
        await asyncio.sleep(0)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    in_q = Queue()
    out_q = Queue()
    gui_q = Queue()
    gui = App()
    try:
        mainLogic = asyncio.ensure_future(init_main(in_q, out_q, gui_q))
        # Hide the GUI if the user doesn't want it
        if not config['DisableGUI']:
            guiLogic = asyncio.ensure_future(gui.run(gui_q, in_q))
        asyncio.get_event_loop().run_forever()

    except Exception as e:
        print(e)
        try:
            mainLogic.cancel()
            if not config['DisableGUI']:
                guiLogic.cancel()

        except asyncio.exceptions as e:
            pass
    finally:
        loop.close()
