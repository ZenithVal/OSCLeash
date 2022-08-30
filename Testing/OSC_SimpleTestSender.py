"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time
import json

from pythonosc import udp_client


if __name__ == "__main__":
  try:
    configData = json.load(open("../config.json"))
  except Exception as e:
    print(e)
    exit()

  client = udp_client.SimpleUDPClient(configData["IP"], configData["ListeningPort"])

  for x in range(10000):
    randNum = random.random()
    leashName = "Leash"
    boolTest = bool(random.getrandbits(1))
    print("{} out of 10,000:\n\tValue: {}\n\tBool: {}".format(x, randNum, boolTest))
    client.send_message("/avatar/parameters/Leash_Z+", randNum)
    client.send_message("/avatar/parameters/Leash_Z-", 0)
    client.send_message("/avatar/parameters/Leash_X+", randNum)
    client.send_message("/avatar/parameters/Leash_X-", 0)
    client.send_message(f"/avatar/parameters/{leashName}_Stretch", randNum)
    client.send_message(f"/avatar/parameters/{leashName}_IsGrabbed", boolTest)
    time.sleep(0.5)