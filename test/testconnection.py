from src.PyAgent.connection.client import Client, DriveExample

instanceClient = Client(port=3001, vision=False)

for step in range(instanceClient.steps,0,-1):
    instanceClient.GetServerInput()
    DriveExample(instanceClient)
    instanceClient.RespondToServer()
    instanceClient.Shutdown()