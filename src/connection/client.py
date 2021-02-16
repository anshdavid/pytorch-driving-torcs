import socket
from typing import DefaultDict, Dict, List, Optional, Tuple, Union
import time

import logging

from src.logger import logger
logger = logging.getLogger(__name__)

PI= 3.14159265359

def Destringify(s: Union[int, str, List]):

    if not s:
        return s

    if type(s) is str:
        try:
            return float(s)
        except ValueError:
            print("Could not find a value in %s" % s)
            return s

    elif type(s) is list:
        if len(s) < 2:
            return Destringify(s[0])
        else:
            return [Destringify(i) for i in s]


class Client():

    DataSize = 2**17

    def __init__(self,
        sensorAngle: str,
        host: str = 'localhost',
        port: int = 3001,
        sid: str = 'SCR',
        timeout: int = 5,
        delay: float = 0.5,
        retry: int = 3,
        debug: bool = False,):

        self.sensorAngles = sensorAngle
        self.host = host
        self.port = port
        self.sid = sid
        self.debug = debug
        self.timeout = timeout
        self.delay = delay
        self.retry = retry
        self.socket = None

        self.CreateConnection()


    def _Serialize(self, actionDict: Dict) -> str:

        out= str()
        for key, value in actionDict.items():
            out+=f"({key} {'%.3f' % value if not type(value) is list else ' '.join([str(x) for x in value])})"
        return out


    def _Deserialize(self, serverString: str) -> DefaultDict:

        out = DefaultDict()

        inString = serverString.strip()[:-1]
        tokenzied = inString.strip().lstrip('(').rstrip(')').split(')(')

        for field in tokenzied:
            ob, *val = field.split(' ')
            out[ob] = Destringify(val)
        return out


    def IsInitialized(self) -> bool:
        if self.socket is not None:
            return True
        return False


    def CreateConnection(self) -> bool:

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            logger.exception(f"{e}")
            logger.error(f"could not create socket")
            return False
        else:
            logger.info(f"connection established")
            return True


    def InitSensors(self) -> bool:

        if not self.IsInitialized():
            logger.error("socket not initialzed !")
            return False

        initmsg = f"{self.sid}(init {self.sensorAngles})"

        try:
            self.socket.sendto(initmsg.encode(), (self.host, self.port))
        except Exception as e:
            logger.exception(f"{e}")
            logger.error(f"error sending message")
            return False
        else:
            logger.info(f"init message sent with sensors {self.sensorAngles}")

        logger.info(f"waiting for response \'InitSensors\' to on port: {self.port}")
        return True


    def RecvFromSever(self) -> Tuple[Optional[DefaultDict], int]:

        sockdata: str = ''
        self.socket.settimeout(self.timeout)

        try:
            sockdata = self.socket.recvfrom(self.DataSize)[0].decode('utf-8')
            if self.debug: print("\nrecv", sockdata)
        except Exception as e:
            logger.exception(f"{e}")
            return None, -4

        if '***restart***' in sockdata:
            logger.warning(f"server restarted on port: {self.port}")
            return None, -3

        elif '***shutdown***' in sockdata:
            logger.error(f"server shutdown on port: {self.port}.")
            return None, -2

        elif not sockdata:
            logger.error(f"server no response on port: {self.port}")
            return None, -1

        elif '***identified***' in sockdata:
            logger.info(f"client identified connected on port: {self.port}")
            # * always delay few secs after starting round maybe ??
            # * helps with stuff !!
            time.sleep(self.delay)
            return None, 0

        else:
            if self.debug:
                logger.info(f"recv: {sockdata}")
            return self._Deserialize(sockdata), 1


    def SendToServer(self, action: Dict) -> bool:

        if self.socket is None:
            logger.error(f"!! connection closed abrubtly on port: {self.port}")
            return False

        message: str = ''
        try:
            message = self._Serialize(action)
            self.socket.sendto(message.encode(), (self.host, self.port))
        except Exception as e:
            logger.exception(f"{e}")
            logger.error(f"error sending to server on port {self.port}")
            if self.debug:
                logger.debug(f"{message}")
            return False
        return True


    def ClientShutdown(self):
        if not self.socket:
            logger.warning(f"unable to close gracefully on port: {self.port}")
            return False


        # * always gracefully try to reset before close
        self.ClientReset()

        logger.info(f"closing connection ...")
        self.socket.close()
        self.socket = None
        logger.info(f"server connection closed on port: {self.port}")
        return True


    def ClientReset(self):
        logger.info(f"reset connection on port {self.port}")
        action = dict()
        action['meta'] = True
        self.SendToServer(action)


def RandomDrive(actionDict: Dict) -> Dict:

    response ={
        'accel':0.2,
        'brake':0,
        'clutch':0,
        'gear':1,
        'steer':0,
        # 'focus':[-90,-45,0,45,90],
        'meta':0
    }

    target_speed=100

    # Steer To Corner
    response['steer']= actionDict['angle']*10 / PI

    # Steer To Center
    response['steer']-= actionDict['trackPos']*.10

    # Throttle Control
    if actionDict['speedX'] < target_speed:
        response['accel'] = 2
    else:
        response['accel'] = 0

    # Traction Control System
    if ((actionDict['wheelSpinVel'][2]+actionDict['wheelSpinVel'][3]) -
       (actionDict['wheelSpinVel'][0]+actionDict['wheelSpinVel'][1]) > 5):
       response['accel']-= .2

    # Automatic Transmission
    response['gear']=1
    if actionDict['speedX']>50:
        response['gear']=2
    if actionDict['speedX']>80:
        response['gear']=3
    if actionDict['speedX']>110:
        response['gear']=4
    if actionDict['speedX']>140:
        response['gear']=5
    if actionDict['speedX']>170:
        response['gear']=6

    return response