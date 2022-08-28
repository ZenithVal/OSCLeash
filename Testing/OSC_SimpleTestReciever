import argparse
import math
import json

from pythonosc import dispatcher
from pythonosc import osc_server

def check_result(addr, value):
    print("Address: {} --- Value: {}".format(addr, value))

if __name__ == "__main__":
    try:
        configData = json.load(open("../config.json"))
    except Exception as e:
        print(e)
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
        type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/input/Vertical", check_result)
    dispatcher.map("/input/Horizontal", check_result)
    dispatcher.map("/input/Run", check_result)

    server = osc_server.ThreadingOSCUDPServer(
        (configData["IP"], configData["SendingPort"]), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()