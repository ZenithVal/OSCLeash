import PySimpleGUI as sg
from queue import LifoQueue
from queue import SimpleQueue
            
           
class App():            
    def __init__(self):
        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        # ToDo prepolulate with multiple sections for Physbone names in Config.json
        self.layout = [  [sg.Text('Leash Name:'), (sg.Text('Null', key='ln'))],
                    [sg.Text('Leash Verti:'), (sg.Text('Null', key='lv'))],
                    [sg.Text('Leash Horiz:'), (sg.Text('Null', key='lh'))],
                    [sg.Text('Leash Turn:'), (sg.Text('Null', key='lt'))],
                    [sg.Text('Current Scale:'), (sg.Text('Null', key='cs'))],]

        # Create the Window
        self.window = sg.Window('OSCLeash - GUI', self.layout, enable_close_attempted_event=True)
        
        # Event Loop to process "events" and get the "values" of the inputs
    
    def run(self, queue:LifoQueue, exception_queue:SimpleQueue):    
        self.window.finalize()
        self.window.set_min_size((300, 100))
        while True:
            event, values = self.window.read(100)
            if event == sg.WIN_CLOSED or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'Cancel': # if user closes window or clicks cancel
                exception_queue.put("exit")
                raise SystemExit
            if queue != None and queue.qsize() > 0:
                values = queue.get()
                self.window['ln'].update(values[0])
                self.window['lv'].update(values[1])
                self.window['lh'].update(values[2])
                self.window['lt'].update(values[3])
                self.window['cs'].update(str(values[4])+"%")
        self.window.close()
    
if __name__ == "__main__":
    app = App()
    testq = LifoQueue()
    exception_queue = SimpleQueue()
    app.run(testq, exception_queue)()
    

