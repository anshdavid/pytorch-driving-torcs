from logging import debug
from src.connection.client import Client, RandomDrive

instanceClient = Client(port=3001, debug=True)

if not instanceClient.CreateConnection():
    print("connection creation failed")

if not instanceClient.InitSensors():
    print("init failed")

action = dict()

print("round 1")
for step in range(200,0,-1):

    obs, flag = instanceClient.RecvFromSever()
    if not flag: break
    action = RandomDrive(obs)
    instanceClient.SendToServer(action)

action = dict()
action['meta'] = True
instanceClient.SendToServer(action)
# instanceClient.Shutdown()
# exit()


print("round 2")
if not instanceClient.CreateConnection():
    print("connection creation failed")

if not instanceClient.InitSensors():
    print("init failed")


for step in range(200,0,-1):
    obs, flag = instanceClient.RecvFromSever()
    if not flag: break
    action = RandomDrive(obs)
    instanceClient.SendToServer(action)

action['meta'] = True
instanceClient.SendToServer(action)
instanceClient.Shutdown()