from typing import Set
from src.connection.client import Client, RandomDrive
import json

sensorAngle_: str = "-45 -19 -12 -7 -4 -2.5 -1.7 -1 -.5 0 .5 1 1.7 2.5 4 7 12 19 45"
instanceClient = Client(sensorAngle=sensorAngle_, port=3001, debug=False)

action = dict()

print("round 1")

if not instanceClient.CreateConnection():
    print("connection creation failed")

instanceClient.InitSensors()
_, flag = instanceClient.RecvFromSever()
if flag < 0: exit()

for step in range(1000,0,-1):

    obs, flag = instanceClient.RecvFromSever()
    if flag < 0:
        print("--->", flag, step)
        break
    else:
        # print(obs)
        action = RandomDrive(obs)
        instanceClient.SendToServer(action)


print("END")
action = dict()
action['meta'] = True
instanceClient.SendToServer(action)
_, _ = instanceClient.RecvFromSever()

instanceClient.ClientShutdown()