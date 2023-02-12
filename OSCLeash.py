from Controllers.AsyncDispatcher import AsyncDispatcher
#from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from Controllers.Leash import LeashActions
from Controllers.Movement import MovementController, ZERO_BUNDLE
from Controllers.Bootstrap import bootstrap, printInfo
import PySimpleGUI as sg
from threading import Thread
import asyncio
import darkdetect
import time
import os
from colorama import init, Fore
import socket
from Controllers.TrioOSCServer import TrioOSCServer
import trio
from timing_util import timing


init() # Initialize colorama
config, vrActive = bootstrap()
leashCollection = [x for x in config["PhysboneParameters"]]
printInfo(config)

def dispatcherMap(dispatcher: AsyncDispatcher, actions: LeashActions):
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
        if config["GUITheme"] != "":
            sg.theme(config["GUITheme"])
        else:
            if darkdetect.isDark():
                sg.theme('DarkPurple5')   # Add a touch of color
            else:
                sg.theme('LightPurple')   # Add a touch of color
        print("")
        # All the stuff inside your window.
        # ToDo prepolulate with multiple sections for Physbone names in Config.json
        self.mainLayout = [  [sg.Text('Leash Name:'), (sg.Text('Null', key='leash-name'))],
                    [sg.Text('Leash X:'), (sg.Text('Null', key='leash-x'))],
                    [sg.Text('Leash Y:'), (sg.Text('Null', key='leash-y'))],
                    [sg.Text('Leash Z:'), (sg.Text('Null', key='leash-z'))],
                    [sg.Text('Leash Turn:'), (sg.Text('Null', key='leash-turn'))],
                    [sg.Text('Current Scale:'), (sg.Text('Null', key='current-scale'))],]


        # Create the Window
        self.window = sg.Window('OSCLeash - GUI', self.mainLayout, enable_close_attempted_event=True)

    
    # Event Loop to process "events" and get the "values" of the inputs
    async def run(self, gui_input: trio.MemoryReceiveChannel, cancel_scope: trio.CancelScope):
        self.window.finalize()
        self.window.set_min_size((250, 100))
        while True:
            event, values = self.window.read(0)
            if event == sg.WIN_CLOSED or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT: # if user closes window
                #out_q.put("gui-exit")
                
                cancel_scope.cancel()
            try:
                values = gui_input.receive_nowait()

                # if config['Logging']:
                #     print(f" Debug Print: {values}") # Debug print of gui values
                if len(values['active-leashes']):
                    self.window['leash-name'].update(values['active-leashes'][-1])
                else:
                    self.window['leash-name'].update("None")
                self.window['leash-x'].update(values['vector'][0])
                self.window['leash-y'].update(values['vector'][1])
                self.window['leash-z'].update(values['vector'][2])
                self.window['leash-turn'].update(values['turn'])
                self.window['current-scale'].update(str(round(values['scale']/config['ScaleDefault']*100))+"%")
            except trio.WouldBlock:
                pass
            await trio.sleep(0.001)


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


async def log_worker(log_input: trio.MemoryReceiveChannel):
    while True:
        async with log_input:
            async for msg in log_input:
                print(msg)
        

async def movement_worker(worker_input: trio.MemoryReceiveChannel, worker_output: trio.MemorySendChannel, vrActive, client: SimpleUDPClient):
    movement = MovementController(config, worker_input, worker_output, vrActive)
    if config['XboxJoystickMovement']:
        movement.setup_xbox_movement()

    lastZeroFixerSent = time.time()

    while True:        
        await trio.sleep(0)
        bundle = await movement.sendMovement()

        if bundle is not None:
            # Arm lock Fix
            # Thanks to McArdellje on the VRChat Canny for the workaround!
            # https://feedback.vrchat.com/feature-requests/p/osc-locks-arms
            if not config['XboxJoystickMovement'] and config['ArmLockFix']:
                now = time.time()
                if now - lastZeroFixerSent > config['ArmLockFixInterval']:
                    lastZeroFixerSent = now
                    bundle = ZERO_BUNDLE
                    for msg in bundle:
                        client.send_message(msg[0], msg[1])
                    await trio.sleep(config['ArmLockFixDuration'])

            for msg in bundle:
                client.send_message(msg[0], msg[1])
        

async def init_main():
    gui = App()

    # Start OSC System
    dispatcher = AsyncDispatcher()

    server = TrioOSCServer((config['IP'], config['ListeningPort']), dispatcher)
    if not checkBindable(config['IP'], config['ListeningPort']):
        print(Fore.RED + "Failed to bind to port, is another instance of OSCLeash running?", Fore.RESET)
        raise SystemExit

    client = SimpleUDPClient(config['IP'], config['SendingPort'])
    
    if not config['VerticalMovement']: 
        vrActive = False
    else:
        vrActive = True
    
    cancel_scope = trio.CancelScope()
    with cancel_scope:
        async with trio.open_nursery() as nursery:
            leash_output, movement_input = trio.open_memory_channel(0)
            movement_output, gui_input   = trio.open_memory_channel(0)
            
            async with leash_output, movement_input, movement_output, gui_input:
                actions = LeashActions(config, leash_output.clone())
                dispatcherMap(dispatcher, actions)
                
                nursery.start_soon(
                    server.start
                )
                nursery.start_soon(
                    movement_worker, movement_input.clone(), movement_output.clone(), vrActive, client
                )
                if config['GUIEnabled']:
                    nursery.start_soon(
                        gui.run, gui_input.clone(), cancel_scope
                    )
                
            
if __name__ == "__main__":
    trio.run(init_main)
