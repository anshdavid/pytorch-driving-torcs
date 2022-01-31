import sys
from typing import Dict, List, Set

import numpy
import sysv_ipc
from PIL import Image
from src.architecture.agent import Agent
from src.connection.client import Client
from src.gym.env import TorcsEnv
from src.utils import ACTION_SPACE, OBSERVATION_SAMPLE
from pprint import pprint


def Raw2RGB(buf, w, h):
    img = numpy.array(buf.reshape((h, w, 3)))
    img = numpy.flip(img, axis=0)
    return img


IMG_MODE = [None]  # , "YCbCr"]

instanceClient = Client()
instanceAgent = Agent(ACTION_SPACE)

action: Dict = {}


if not instanceClient.CreateConnection():
    print("connection creation failed")

instanceClient.InitSensors()
_, flag = instanceClient.RecvFromSever()
if flag < 0:
    exit()

shm = sysv_ipc.SharedMemory(1234, flags=0)

for i in range(10):
    _ = shm.read(640 * 480 * 3)

for step, idx in enumerate(range(500, 0, -1)):

    obs, flag = instanceClient.RecvFromSever()
    if flag < 0:
        print("--->", flag, step)
        break
    else:

        pprint({key: value for key, value in obs.items() if key in OBSERVATION_SAMPLE})
        # print(sys.getsizeof(obs))
        # print(obs.keys())

        # buf = shm.read(640 * 480 * 3)
        img = numpy.flip(
            numpy.array(numpy.frombuffer(shm.read(640 * 480 * 3), dtype=numpy.int8).reshape((480, 640, 3))),
            axis=0,
        )

        for mode in IMG_MODE:
            try:
                result = Image.fromarray((img * 255).astype(numpy.uint8), mode=mode)
                result.save(f"reports/video/{idx}-{mode}.jpg")
            except Exception as e:
                print(f"exception mode:{mode}, {e}")

        action = instanceAgent.SampleAction()
        action["gear"] = 1
        action["brake"] = 0
        action["accel"] = 0.1

        instanceClient.SendToServer(action)


print("END")
# instanceClient.SendToServer({"meta": True})
# _, _ = instanceClient.RecvFromSever()
instanceClient.ClientShutdown()
