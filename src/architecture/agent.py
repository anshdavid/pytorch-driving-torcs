from typing import Collection, Dict
import numpy as np
from gym import spaces
from collections import OrderedDict


class DriverAction:
    def __init__(self):
        self.actionstr = str()
        # "d" is for data dictionary.
        self.d = {
            "accel": 0.2,
            "brake": 0,
            "clutch": 0,
            "gear": 1,
            "steer": 0,
            "focus": [-90, -45, 0, 45, 90],
            "meta": 0,
        }

    def clip_to_limits(self):
        self.d["steer"] = np.clip(self.d["steer"], -1, 1)
        self.d["brake"] = np.clip(self.d["brake"], 0, 1)
        self.d["accel"] = np.clip(self.d["accel"], 0, 1)
        self.d["clutch"] = np.clip(self.d["clutch"], 0, 1)
        if self.d["gear"] not in [-1, 0, 1, 2, 3, 4, 5, 6]:
            self.d["gear"] = 0
        if self.d["meta"] not in [0, 1]:
            self.d["meta"] = 0
        if type(self.d["focus"]) is not list or min(self.d["focus"]) < -180 or max(self.d["focus"]) > 180:
            self.d["focus"] = 0

    def __repr__(self):
        self.clip_to_limits()
        out = str()
        for k in self.d:
            out += "(" + k + " "
            v = self.d[k]
            if not type(v) is list:
                out += "%.3f" % v
            else:
                out += " ".join([str(x) for x in v])
            out += ")"
        return out


class Agent(object):
    def __init__(self, actionDict: Dict[str, spaces.Box]):
        self.actionSpace = spaces.Dict(actionDict)

    # def act(self, ob, reward, done):
    #     focus, speedX, speedY, speedZ, opponents, rpm, track, wheelSpinVel = ob
    #     # random action
    #     return np.tanh(np.random.randn(self.dim_action))    #type:ignore

    # def ClipToLimits(self):
    #     # There pretty much is never a reason to send the server
    #     # something like (steer 9483.323). This comes up all the time
    #     # and it's probably just more sensible to always clip it than to
    #     # worry about when to. The "clip" command is still a snakeoil
    #     # utility function, but it should be used only for non standard
    #     # things or non obvious limits (limit the steering to the left,
    #     # for example). For normal limits, simply don't worry about it.

    #     self.action['steer']= clip(self.action['steer'], -1, 1)
    #     self.action['brake']= clip(self.action['brake'], 0, 1)
    #     self.action['accel']= clip(self.action['accel'], 0, 1)
    #     self.action['clutch']= clip(self.action['clutch'], 0, 1)

    #     if self.action['gear'] not in [-1, 0, 1, 2, 3, 4, 5, 6]:
    #         self.action['gear']= 0

    #     if self.action['meta'] not in [0,1]:
    #         self.action['meta']= 0

    #     if type(self.action['focus']) is not list or \
    #         min(self.action['focus'])<-180 or \
    #         max(self.action['focus'])>180:
    #         self.action['focus']= 0

    def SampleAction(self) -> OrderedDict:
        return self.actionSpace.sample()
