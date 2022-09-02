"""
Small example OSC client
"""
import random
import time

from pythonosc import udp_client

LeashNameString = "Leash_South"
PORT = 9001
IP = "127.0.0.1"

def sendData():
  
  Directional = random.random()
  LeashZPos = 0.0
  LeashZNeg = 0.0
  LeashXPos = 0.0
  LeashXNeg = 0.0
  
  if Directional >= .75:    # North
    LeashZPos = 1.0
  elif Directional >= .50:  # South
    LeashZNeg = 1.0
  elif Directional >= .25:   # East
    LeashXPos = 1.0
  else:                     # West
    LeashXNeg = 1.0

  #IsGrabbedState = bool(random.getrandbits(1))
  IsGrabbedState = True
  #StretchValue = random.random()
  StretchValue = 1

  print(f"Sending {LeashNameString} information:\n\tGrabbed: {IsGrabbedState}\n\tStretch: {StretchValue}\n\tZ+: {LeashZPos}\n\tZ-: {LeashZNeg}\n\tX+: {LeashXPos}\n\tX-: {LeashXNeg}")

  client.send_message("/avatar/parameters/Leash_Z+", LeashZPos)
  client.send_message("/avatar/parameters/Leash_Z-", LeashZNeg)
  client.send_message("/avatar/parameters/Leash_X+", LeashXPos)
  client.send_message("/avatar/parameters/Leash_X-", LeashXNeg)
  client.send_message(f"/avatar/parameters/{LeashNameString}_Stretch", StretchValue)
  client.send_message(f"/avatar/parameters/{LeashNameString}_IsGrabbed", IsGrabbedState)

  time.sleep(2)

if __name__ == "__main__":

  client = udp_client.SimpleUDPClient(IP, PORT)

  for x in range(10000):
    sendData()
