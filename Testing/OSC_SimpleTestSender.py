"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time
import json

from pythonosc import udp_client

def sendData(leashName):
  for x in range(10000):
    randNum1 = random.random()
    randNum2 = random.random()
    randNum3 = random.random()
    boolTest = bool(random.getrandbits(1))

    print("{}: {} out of 10,000:\n\tRandValue1: {}\n\tRandValue2: {}\n\tRandValue3: {}\n\tBool: {}".format(leashName, x, randNum1, randNum2, randNum3, boolTest))

    client.send_message("/avatar/parameters/Leash_Z+", 0.2)
    client.send_message("/avatar/parameters/Leash_Z-", 0)
    client.send_message("/avatar/parameters/Leash_X+", 0.8)
    client.send_message("/avatar/parameters/Leash_X-", 0)
    client.send_message(f"/avatar/parameters/{leashName}_Stretch", 1.0)
    client.send_message(f"/avatar/parameters/{leashName}_IsGrabbed", True)

    time.sleep(0.5)

if __name__ == "__main__":
  try:
    configData = json.load(open("../Config.json"))
  except Exception as e:
    print(e)
    exit()

  client = udp_client.SimpleUDPClient(configData["IP"], configData["ListeningPort"])

  for leashName in configData["PhysboneParameters"]:
    sendData(leashName)