import logging
from typing import DefaultDict, Dict, Optional, Set, Tuple, Union

import numpy as np
import math
from src.connection.client import Client
from src.logger import logger

from gym import spaces
from collections import OrderedDict

logger = logging.getLogger(__name__)


class TorcsEnv(Client):

    sensorAngle_: str = (
        "-45 -19 -12 -7 -4 -2.5 -1.7 -1 -.5 0 .5 1 1.7 2.5 4 7 12 19 45"
    )

    observation_dict_: Dict[str, spaces.Box] = {
        "angle": spaces.Box(
            low=-math.pi, high=math.pi, shape=(1,), dtype=np.float16
        ),
        "damage": spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.float16),
        # "distFromStart": spaces.Box(
        #     low=0, high=np.inf, shape=(1,), dtype=np.float16
        # ),
        "distRaced": spaces.Box(
            low=0, high=np.inf, shape=(1,), dtype=np.float16
        ),
        "gear": spaces.Box(low=-1, high=6, shape=(1,), dtype=np.int),
        "rpm": spaces.Box(low=0, high=math.inf, shape=(1,), dtype=np.float16),
        # "fuel": spaces.Box(low=0, high=math.inf, shape=(1,), dtype=np.float16),
        "speedX": spaces.Box(
            low=math.inf, high=math.inf, shape=(1,), dtype=np.float16
        ),
        "speedY": spaces.Box(
            low=math.inf, high=math.inf, shape=(1,), dtype=np.float16
        ),
        "track": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float16),
        "trackPos": spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float16),
        "wheelSpinVel": spaces.Box(
            low=0, high=math.inf, shape=(4,), dtype=np.float16
        ),
    }

    action_dict_: Dict[str, spaces.Box] = {
        "accel": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float16),
        "brake": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float16),
        "steer": spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float16),
    }

    def __init__(
        self,
        sensorAngle=sensorAngle_,
        host: str = "localhost",
        port: int = 3001,
        sid: str = "SCR",
        timeout: int = 5,
        delay: int = 2,
        retry: int = 3,
        epoch=20,
        steps=1000,
        debug: bool = False,
        vision: bool = False,
        gear: bool = True,
    ):

        self.epoch = epoch
        self.steps = steps
        self.debug = debug

        self.vision = vision
        self.gear = gear
        self.prevobs = None

        super().__init__(
            sensorAngle=sensorAngle,
            host=host,
            port=port,
            sid=sid,
            timeout=timeout,
            delay=delay,
            retry=retry,
            debug=debug,
        )

        if not self.CreateConnection():
            logger.error(f"unable to create connection")
            return False

    def InitStage(self) -> bool:

        if not self.InitSensors():
            logger.error(f"unable to initialize sensors")
            return False

        _, ret = self.RecvFromSever()
        if ret == 0:
            return True
        else:
            logger.error(f"no response from server")
            return False

    def Restart(self):
        pass

    def FilterObservations(self, observations: Dict):
        return dict(
            filter(
                lambda kv: kv[0] in self.observation_dict_, observations.items()
            )
        )

    def Reward(self, observations: Union[Dict, DefaultDict]):
        pass

    def step(
        self, action: OrderedDict
    ) -> Tuple[Union[Dict, DefaultDict], float, bool, Optional[Dict]]:
        """
        Args:
            action (object): an action provided by the agent

        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (bool): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """

        self.prevobs, retCode = self.RecvFromSever()

        if not self.SendToServer(action):
            logger.warning(f"unable to send action to server")
            return (dict(), 0.0, False, None)

        obs, retCode = self.RecvFromSever()

        if retCode == 1:
            return (self.FilterObservations(obs), 1.0, False, None)
        else:
            return (self.FilterObservations(obs), 0.0, True, None)

    def restart(self) -> bool:
        """
        restart current stage

        Returns:
            bool: True is successful
        """

        self.ServerRestart()

        if self.RecvFromSever()[1] == -3:
            logger.info(f"restart environment on port {self.port}")
            return True
        return False

    def reset(self) -> bool:
        return True

    def render(self):
        pass

    def close(self):
        logger.info(f"teardown environment !")
        self.ClientShutdown()

    def seed(self):
        pass

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
    #         high = np.array([1., np.inf, np.inf, np.inf, 1., np.inf, 1., np.inf])
    #         low = np.array([0., -np.inf, -np.inf, -np.inf, 0., -np.inf, 0., -np.inf])
    #         self.observation_space = spaces.Box(low=low, high=high)
    #     else:
    #         high = np.array([1., np.inf, np.inf, np.inf, 1., np.inf, 1., np.inf, 255])
    #         low = np.array([0., -np.inf, -np.inf, -np.inf, 0., -np.inf, 0., -np.inf, 0])
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
    #     track = np.array(obs['track'])
    #     sp = np.array(obs['speedX'])
    #     progress = sp*np.cos(obs['angle'])
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
    #     if np.cos(obs['angle']) < 0:    #type:ignore
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
    #     return np.array(rgb, dtype=np.uint8)

    # def make_observaton(self, raw_obs):
    #     if self.vision is False:
    #         names = ['focus',
    #                  'speedX', 'speedY', 'speedZ',
    #                  'opponents',
    #                  'rpm',
    #                  'track',
    #                  'wheelSpinVel']
    #         Observation = col.namedtuple('Observaion', names)
    #         return Observation(focus=np.array(raw_obs['focus'], dtype=np.float32)/200.,
    #                            speedX=np.array(raw_obs['speedX'], dtype=np.float32)/self.default_speed,
    #                            speedY=np.array(raw_obs['speedY'], dtype=np.float32)/self.default_speed,
    #                            speedZ=np.array(raw_obs['speedZ'], dtype=np.float32)/self.default_speed,
    #                            opponents=np.array(raw_obs['opponents'], dtype=np.float32)/200.,
    #                            rpm=np.array(raw_obs['rpm'], dtype=np.float32),
    #                            track=np.array(raw_obs['track'], dtype=np.float32)/200.,
    #                            wheelSpinVel=np.array(raw_obs['wheelSpinVel'], dtype=np.float32))
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

    #         return Observation(focus=np.array(raw_obs['focus'], dtype=np.float32)/200.,
    #                            speedX=np.array(raw_obs['speedX'], dtype=np.float32)/self.default_speed,
    #                            speedY=np.array(raw_obs['speedY'], dtype=np.float32)/self.default_speed,
    #                            speedZ=np.array(raw_obs['speedZ'], dtype=np.float32)/self.default_speed,
    #                            opponents=np.array(raw_obs['opponents'], dtype=np.float32)/200.,
    #                            rpm=np.array(raw_obs['rpm'], dtype=np.float32),
    #                            track=np.array(raw_obs['track'], dtype=np.float32)/200.,
    #                            wheelSpinVel=np.array(raw_obs['wheelSpinVel'], dtype=np.float32),
    #                            img=image_rgb)
