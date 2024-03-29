import logging
from optparse import Option
from typing import DefaultDict, Dict, Optional, Set, Tuple, Union

import numpy
import math
from src import gym
from src.connection.client import Client
from src.utils import StartContainer, StartTorcs, StopContainer, StopTorcs
from src.logger import logger

from gym import spaces, Env
from collections import OrderedDict
import time
from src.utils import (
    DEFAULT_SENSOR_ANGLES,
    OBSERVATION_KEYS,
    OBSERVATION_SAMPLE,
    SERVERCODE_IDENTIFIED,
    SERVERCODE_OBSERVATION,
)

logger = logging.getLogger(__name__)


class TorcsEnv(Env):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3001,
        sid: str = "SCR",
        sensorAngle: str = DEFAULT_SENSOR_ANGLES,
        verbose: bool = False,
        timeout: int = 15,
        delay: float = 0,
        trackname: str = None,
        vision: bool = False,
        imgHeight: int = 480,
        imgWidth: int = 640,
    ) -> None:

        super().__init__()

        self._containerID: Optional[str] = ""
        self.vision = vision

        self.client = Client(host, port, sid, sensorAngle, verbose, timeout, delay)

    @property
    def containerID(self):
        return self._containerID

    @containerID.setter
    def containerID(self, value: Optional[str]) -> None:
        self._containerID = value

    def __enter__(self):

        self.containerID = StartContainer()
        if self.containerID is None:
            logger.error("unable to start torcs container")
            exit(-1)

        time.sleep(3.0)

        StartTorcs(self.containerID, vision=self.vision)

        time.sleep(3.0)

        if not self.client.CreateConnection():
            logger.error("connection creation failed")
            exit(-1)

        if not self.client.InitSensors():
            logger.error("init sensors failed")
            exit(-1)

        _, flag = self.client.RecvFromSever()
        if flag not in [SERVERCODE_IDENTIFIED, SERVERCODE_OBSERVATION]:
            logger.error("client identification failed")
            exit(-1)

        return self

    def __exit__(self, *args):
        logger.info(f"exit env context with {args}")
        # if self.containerID:
        #     self.close()

    def close(self) -> None:
        if self.containerID:
            self.client.ServerRestart()

            time.sleep(5)
            StopTorcs(self.containerID)

            time.sleep(5)
            StopContainer(self.containerID)


# class TorcsEnv(Client):
#     def __init__(
#         self,
#         host: str = "localhost",
#         port: int = 3001,
#         sid: str = "SCR",
#         sensorAngle: str = DEFAULT_SENSOR_ANGLES,
#         verbose: bool = False,
#         timeout: int = 15,
#         delay: float = 0,
#         trackname: str = None,
#         containerID: str = "0",
#         vision: bool = False,
#         imgHeight: int = 480,
#         imgWidth: int = 640,
#     ):
#         super().__init__(host, port, sid, sensorAngle, verbose, timeout, delay)

#         self.vision = vision

#         self.epoch = epoch
#         self.steps = steps
#         self.gear = gear

#         self.prevobs = None

#         if not self.CreateConnection():
#             logger.error("unable to create connection")
#             return False

#     def InitStage(self) -> bool:

#         if not self.InitSensors():
#             logger.error("unable to initialize sensors")
#             return False

#         _, ret = self.RecvFromSever()
#         if ret == 0:
#             return True
#         else:
#             logger.error(f"no response from server")
#             return False

#     def Restart(self):
#         pass

#     def FilterObservations(self, observations: Dict):
#         return dict(filter(lambda kv: kv[0] in OBSERVATION_SAMPLE, observations.items()))

#     def Reward(self, observations: Union[Dict, DefaultDict]):
#         pass

#     def step(self, action: OrderedDict) -> Tuple[Union[Dict, DefaultDict], float, bool, Optional[Dict]]:
#         """
#         Args:
#             action (object): an action provided by the agent

#         Returns:
#             observation (object): agent's observation of the current environment
#             reward (float) : amount of reward returned after previous action
#             done (bool): whether the episode has ended, in which case further step() calls will return undefined results
#             info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
#         """

#         self.prevobs, retCode = self.RecvFromSever()

#         if not self.SendToServer(action):
#             logger.warning("unable to send action to server")
#             return (dict(), 0.0, False, None)

#         obs, retCode = self.RecvFromSever()

#         if retCode == 1:
#             return (self.FilterObservations(obs), 1.0, False, None)
#         else:
#             return (self.FilterObservations(obs), 0.0, True, None)

#     def restart(self) -> bool:
#         """
#         restart current stage

#         Returns:
#             bool: True is successful
#         """

#         self.ServerRestart()

#         if self.RecvFromSever()[1] == -3:
#             logger.info(f"restart environment on port {self.port}")
#             return True
#         return False

#     def reset(self) -> bool:
#         return True

#     def render(self):
#         pass

#     def close(self):
#         logger.info(f"teardown environment !")
#         self.ClientShutdown()

#     def seed(self):
#         pass

# terminal_judge_start = 500  # Speed limit is applied after this step
# termination_limit_progress = 5  # [km/h], episode terminates if car is running slower than this limit
# default_speed = 50

# initial_reset = True

# def __init__(self,
#     epochs: int = 100,
#     steps: int = 50000,
#     debug: bool = False,
#     vision: bool = False,
#     throttle=False,
#     gearChange=False,):
#     # trackname: str = 'unknown',
#     # stage: int = 3):

#     self.vision = vision
#     self.throttle = throttle
#     self.gear_change = gear_change
#     self.port = port
#     self.initial_run = True

#     if throttle is False:
#         self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,))
#     else:
#         self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,))

#     if vision is False:
#         high = numpy.array([1., numpy.inf, numpy.inf, numpy.inf, 1., numpy.inf, 1., numpy.inf])
#         low = numpy.array([0., -numpy.inf, -numpy.inf, -numpy.inf, 0., -numpy.inf, 0., -numpy.inf])
#         self.observation_space = spaces.Box(low=low, high=high)
#     else:
#         high = numpy.array([1., numpy.inf, numpy.inf, numpy.inf, 1., numpy.inf, 1., numpy.inf, 255])
#         low = numpy.array([0., -numpy.inf, -numpy.inf, -numpy.inf, 0., -numpy.inf, 0., -numpy.inf, 0])
#         self.observation_space = spaces.Box(low=low, high=high)

# def step(self, u):

#     # convert thisAction to the actual torcs actionstr
#     client = self.client

#     this_action = self.agent_to_torcs(u)

#     action_torcs = client.DriverActionDict

#     action_torcs['steer'] = this_action['steer']  # in [-1, 1]

#     #  Simple Autnmatic Throttle Control by Snakeoil
#     if self.throttle is False:
#         target_speed = self.default_speed
#         if client.ServerStateDict['speedX'] < target_speed - (client.DriverActionDict['steer']*50):
#             client.DriverActionDict['accel'] += .01
#         else:
#             client.DriverActionDict['accel'] -= .01

#         if client.DriverActionDict['accel'] > 0.2:
#             client.DriverActionDict['accel'] = 0.2

#         if client.ServerStateDict['speedX'] < 10:
#             client.DriverActionDict['accel'] += 1/(client.ServerStateDict['speedX']+.1)

#         # Traction Control System
#         if ((client.ServerStateDict['wheelSpinVel'][2]+client.ServerStateDict['wheelSpinVel'][3]) -
#            (client.ServerStateDict['wheelSpinVel'][0]+client.ServerStateDict['wheelSpinVel'][1]) > 5):
#             action_torcs['accel'] -= .2
#     else:
#         action_torcs['accel'] = this_action['accel']

#     #  Automatic Gear Change by Snakeoil
#     if self.gear_change is True:
#         action_torcs['gear'] = this_action['gear']
#     else:
#         #  Automatic Gear Change by Snakeoil is possible
#         action_torcs['gear'] = 1
#         """
#         if client.ServerStateDict['speedX'] > 50:
#             action_torcs['gear'] = 2
#         if client.ServerStateDict['speedX'] > 80:
#             action_torcs['gear'] = 3
#         if client.ServerStateDict['speedX'] > 110:
#             action_torcs['gear'] = 4
#         if client.ServerStateDict['speedX'] > 140:
#             action_torcs['gear'] = 5
#         if client.ServerStateDict['speedX'] > 170:
#             action_torcs['gear'] = 6
#         """

#     # Save the privious full-obs from torcs for the reward calculation
#     obs_pre = copy.deepcopy(client.ServerStateDict)

#     # One-Step Dynamics Update #################################
#     # Apply the Agent's action into torcs
#     client.RespondToServer()
#     # Get the response of TORCS
#     client.GetServerInput()

#     # Get the current full-observation from torcs
#     obs = client.ServerStateDict

#     # Make an obsevation from a raw observation vector from TORCS
#     self.observation = self.make_observaton(obs)

#     # Reward setting Here #######################################
#     # direction-dependent positive reward
#     track = numpy.array(obs['track'])
#     sp = numpy.array(obs['speedX'])
#     progress = sp*numpy.cos(obs['angle'])
#     reward = progress

#     # collision detection
#     if obs['damage'] - obs_pre['damage'] > 0:
#         reward = -1

#     # Termination judgement #########################
#     episode_terminate = False
#     if track.min() < 0:  # Episode is terminated if the car is out of track
#         reward = - 1
#         episode_terminate = True
#         client.DriverActionDict['meta'] = True

#     if self.terminal_judge_start < self.time_step: # Episode terminates if the progress of agent is small
#         if progress < self.termination_limit_progress:
#             episode_terminate = True
#             client.DriverActionDict['meta'] = True

#     # Episode is terminated if the agent runs backward
#     if numpy.cos(obs['angle']) < 0:    #type:ignore
#         episode_terminate = True
#         client.DriverActionDict['meta'] = True

#     if client.DriverActionDict['meta'] is True: # Send a reset signal
#         self.initial_run = False
#         client.RespondToServer()

#     self.time_step += 1

#     return self.get_obs(), reward, client.DriverActionDict['meta'], {}

# def reset(self, relaunch=False):
#     #print("Reset")

#     self.time_step = 0

#     if self.initial_reset is not True:
#         self.client.DriverActionDict['meta'] = True
#         self.client.RespondToServer()

#         ## TENTATIVE. Restarting TORCS every episode suffers the memory leak bug!
#         if relaunch is True:
#             self.reset_torcs()
#             print("### TORCS is RELAUNCHED ###")

#     # Modify here if you use multiple tracks in the environment
#     self.client = Client(port=self.port, vision=self.vision)  # Open new UDP in vtorcs
#     self.client.steps = 100000

#     client = self.client
#     client.GetServerInput()  # Get the initial input from torcs

#     obs = client.ServerStateDict  # Get the current full-observation from torcs
#     self.observation = self.make_observaton(obs)

#     self.last_u = None

#     self.initial_reset = False
#     return self.get_obs()

# def end(self):
#     os.system('pkill torcs')

# def get_obs(self):
#     return self.observation

# def reset_torcs(self):
#    #print("relaunch torcs")
#     # os.system('pkill torcs')
#     # time.sleep(0.5)
#     # if self.vision is True:
#     #     os.system('torcs -nofuel -nodamage -nolaptime -vision &')
#     # else:
#     #     os.system('torcs -nofuel -nodamage -nolaptime &')
#     # time.sleep(0.5)
#     # os.system('sh autostart.sh')
#     # time.sleep(0.5)
#     pass

# def agent_to_torcs(self, u):
#     torcs_action = {'steer': u[0]}

#     if self.throttle is True:  # throttle action is enabled
#         torcs_action.update({'accel': u[1]})

#     if self.gear_change is True: # gear change action is enabled
#         torcs_action.update({'gear': u[2]})

#     return torcs_action

# def obs_vision_to_image_rgb(self, obs_image_vec):
#     print(f"image shape - {shape(obs_image_vec)}")
#     image_vec =  obs_image_vec
#     rgb = []
#     temp = []
#     # convert size 64x64x3 = 12288 to 64x64=4096 2-D list
#     # with rgb values grouped together.
#     # Format similar to the observation in openai gym
#     for i in range(0,12286,3):
#         temp.append(image_vec[i])
#         temp.append(image_vec[i+1])
#         temp.append(image_vec[i+2])
#         rgb.append(temp)
#         temp = []
#     return numpy.array(rgb, dtype=numpy.uint8)

# def make_observaton(self, raw_obs):
#     if self.vision is False:
#         names = ['focus',
#                  'speedX', 'speedY', 'speedZ',
#                  'opponents',
#                  'rpm',
#                  'track',
#                  'wheelSpinVel']
#         Observation = col.namedtuple('Observaion', names)
#         return Observation(focus=numpy.array(raw_obs['focus'], dtype=numpy.float32)/200.,
#                            speedX=numpy.array(raw_obs['speedX'], dtype=numpy.float32)/self.default_speed,
#                            speedY=numpy.array(raw_obs['speedY'], dtype=numpy.float32)/self.default_speed,
#                            speedZ=numpy.array(raw_obs['speedZ'], dtype=numpy.float32)/self.default_speed,
#                            opponents=numpy.array(raw_obs['opponents'], dtype=numpy.float32)/200.,
#                            rpm=numpy.array(raw_obs['rpm'], dtype=numpy.float32),
#                            track=numpy.array(raw_obs['track'], dtype=numpy.float32)/200.,
#                            wheelSpinVel=numpy.array(raw_obs['wheelSpinVel'], dtype=numpy.float32))
#     else:
#         names = ['focus',
#                  'speedX', 'speedY', 'speedZ',
#                  'opponents',
#                  'rpm',
#                  'track',
#                  'wheelSpinVel',
#                  'img']
#         Observation = col.namedtuple('Observaion', names)

#         # Get RGB from observation
#         image_rgb = self.obs_vision_to_image_rgb(raw_obs[names[8]])

#         return Observation(focus=numpy.array(raw_obs['focus'], dtype=numpy.float32)/200.,
#                            speedX=numpy.array(raw_obs['speedX'], dtype=numpy.float32)/self.default_speed,
#                            speedY=numpy.array(raw_obs['speedY'], dtype=numpy.float32)/self.default_speed,
#                            speedZ=numpy.array(raw_obs['speedZ'], dtype=numpy.float32)/self.default_speed,
#                            opponents=numpy.array(raw_obs['opponents'], dtype=numpy.float32)/200.,
#                            rpm=numpy.array(raw_obs['rpm'], dtype=numpy.float32),
#                            track=numpy.array(raw_obs['track'], dtype=numpy.float32)/200.,
#                            wheelSpinVel=numpy.array(raw_obs['wheelSpinVel'], dtype=numpy.float32),
#                            img=image_rgb)

