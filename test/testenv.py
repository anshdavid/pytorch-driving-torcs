from src.gym.env import TorcsEnv
from src.architecture.agent import Agent
import json


instanceEnv = TorcsEnv(port=3001, debug=False)
instanceAgent = Agent(instanceEnv.action_dict_)


if instanceEnv.InitStage():
    print(f"starting round ...")
else:
    print(f"unable to initialize round")

steps = instanceEnv.steps
while steps:
    observation, reward, done, _ = instanceEnv.step(
        instanceAgent.SampleAction()
    )
    print(json.dumps(observation, indent=2))
    steps -= 1

print(f"ending round ...")
instanceEnv.restart()
