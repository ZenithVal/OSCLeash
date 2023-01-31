from multiprocessing import Queue
import PySimpleGUI as sg           
import asyncio
from pprint import pprint

class App():            
    def __init__(self, config: dict):
        self.config = config
        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        # ToDo prepolulate with multiple sections for Physbone names in Config.json
        self.mainLayout = [  [sg.Text('Leash Name:'), (sg.Text('Null', key='leash-name'))],
                    [sg.Text('Leash X:'), (sg.Text('Null', key='leash-x'))],
                    [sg.Text('Leash Z:'), (sg.Text('Null', key='leash-z'))],
                    [sg.Text('Leash Turn:'), (sg.Text('Null', key='leash-turn'))],
                    [sg.Text('Current Scale:'), (sg.Text('Null', key='current-scale'))],]

        # self.configLayout = [  [sg.Text('IP:'), (sg.InputText(config['IP'], key='config-IP'))],
        #                        [sg.Text('Listening Port:'), (sg.InputText(config['ListeningPort'], key='config-ListeningPort'))],
        #                        [sg.Text('Sending Port:'), (sg.InputText(config['SendingPort'], key='config-SendingPort'))],
        #                        [sg.Text('Run Deadzone:'), (sg.InputText(config['RunDeadzone'], key='config-RunDeadzone'))],
        #                          [sg.Text('Walk Deadzone:'), (sg.InputText(config['WalkDeadzone'], key='config-WalkDeadzone'))],
        #                          [sg.Text('Strength Multiplier:'), (sg.InputText(config['StrengthMultiplier'], key='config-StrengthMultiplier'))],
        #                          [sg.Text('Turning Enabled:'), (sg., key='config-TurningEnabled'))],
        # ]
                            
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
                if self.window['Logging']:
                    print(values) # Debug print of gui values
                if len(values['active-leashes']):
                    self.window['leash-name'].update(values['active-leashes'][-1])
                else:
                    self.window['leash-name'].update("None")
                self.window['leash-x'].update(values['vector'][0])
                self.window['leash-z'].update(values['vector'][2])
                self.window['leash-turn'].update(values['turn'])
                self.window['current-scale'].update(str(round(values['scale']/self.config['ScaleNormal']*100))+"%")
            await asyncio.sleep(0)
        self.window.close()
