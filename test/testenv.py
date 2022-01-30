import json
import time
from pprint import pprint
from typing import Optional

from src.architecture.agent import Agent
from src.gym.env import TorcsEnv
from src.utils import (ACTION_SPACE, OBSERVATION_SAMPLE, StopContainer,
                       StopTorcs)

# from src.logger import logger
CONTAINER_ID: Optional[str] = None

with TorcsEnv() as env:

    assert env

    CONTAINER_ID = env.containerID

    agent = Agent(ACTION_SPACE)

    for step, idx in enumerate(range(500, 0, -1)):

        obs, flag = env.client.RecvFromSever()

        if flag < 0:
            print("--->", flag, step)
            break
        else:
            pprint({key: value for key, value in obs.items() if key in OBSERVATION_SAMPLE})

        action = agent.SampleAction()
        action["gear"] = 1
        action["brake"] = 0

        env.client.SendToServer(action)

    env.client.ServerRestart()

if CONTAINER_ID:
    StopTorcs(CONTAINER_ID)
    time.sleep(5)
    StopContainer(CONTAINER_ID)

