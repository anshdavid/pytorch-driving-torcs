from typing import Set
from src.gym.env import TorcsEnv
from src.architecture.agent import Agent
import json


instanceEnv = TorcsEnv(port=3001, debug=False)
instanceAgent = Agent(instanceEnv.action_dict_)


if instanceEnv.InitStage():
    print(f"starting round ...")
else:
    print(f"unable to initialize round")
    exit()

steps = instanceEnv.steps
while True:
    observation, reward, done, _ = instanceEnv.step(instanceAgent.SampleAction())
    steps -= 1

print(f"ending round ...")
instanceEnv.reset()
