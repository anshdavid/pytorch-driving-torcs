from typing import Set
from src.connection.client import Client
from src.architecture.agent import Agent
from src.gym.env import TorcsEnv

sensorAngle_: str = (
    "-45 -19 -12 -7 -4 -2.5 -1.7 -1 -.5 0 .5 1 1.7 2.5 4 7 12 19 45"
)
instanceClient = Client(sensorAngle=sensorAngle_, port=3001, debug=False)
instanceAgent = Agent(TorcsEnv.action_dict_)

action = dict()

print("round 1")

if not instanceClient.CreateConnection():
    print("connection creation failed")

instanceClient.InitSensors()
_, flag = instanceClient.RecvFromSever()
if flag < 0:
    exit()

for step in range(1000, 0, -1):

    obs, flag = instanceClient.RecvFromSever()
    if flag < 0:
        print("--->", flag, step)
        break
    else:
        # print(obs)
        # action = RandomDrive(obs)
        instanceClient.SendToServer(instanceAgent.SampleAction())


print("END")
action = dict()
action["meta"] = True
instanceClient.SendToServer(action)
_, _ = instanceClient.RecvFromSever()

instanceClient.ClientShutdown()