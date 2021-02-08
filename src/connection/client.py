import socket
from typing import DefaultDict, Dict, List, Tuple, Union
import time

import logging

from src.logger import logger
logger = logging.getLogger(__name__)

PI= 3.14159265359

def Destringify(s: Union[str, List]):

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
    # sensorAngles = "-45 -19 -12 -7 -4 -2.5 -1.7 -1 -.5 0 .5 1 1.7 2.5 4 7 12 19 45"
    sensorAngles = "-90 -75 -60 -45 -30 -20 -15 -10 -5 0 5 10 15 20 30 45 60 75 90"

    def __init__(self,
        host: str = 'localhost',
        port: int = 3001,
        sid: str = 'SCR',
        timeout=1,
        debug: bool = False):

        self.host = host
        self.port = port
        self.sid = sid
        self.debug = debug
        self.timeout = timeout
        self.socket = None

        self.CreateConnection()


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
            logger.error("socket no initialzed !")
            return False

        while True:

            initmsg = f"{self.sid}(init {self.sensorAngles})"

            try:
                self.socket.sendto(initmsg.encode(), (self.host, self.port))
            except Exception as e:
                logger.exception(f"{e}")
                logger.error(f"error sending message")
                return False
            else:
                logger.info(f"init message sent with sensors {self.sensorAngles}")


            self.socket.settimeout(self.timeout)
            sockdata: str = ''

            logger.warning(f"waiting for response \'InitSensors\' to on port: {self.port}")
            try:
                sockdata = self.socket.recvfrom(self.DataSize)[0].decode('utf-8')
                if self.debug: print("\ninit", sockdata)
            except Exception as e:
                logger.exception(f"{e}")
            else:
                if '***identified***' in sockdata:
                    logger.info(f"client identified connected on port: {self.port}")
                    break
        
        # * always delay few secs after entring round maybe ??
        # * helps with stuff !!
        time.sleep(5)
        return True


    def _Serialize(self, actionDict: Dict) -> str:

        out= str()
        for k in actionDict:
            out+= '('+k+' '
            v= actionDict[k]
            if not type(v) is list:
                out+= '%.3f' % v
            else:
                out+= ' '.join([str(x) for x in v])
            out+= ')'
        return out


    def _Deserialize(self, serverString: str) -> DefaultDict:

        temp = DefaultDict()

        servstr = serverString.strip()[:-1]
        sslisted = servstr.strip().lstrip('(').rstrip(')').split(')(')

        for i in sslisted:
            w= i.split(' ')
            temp[w[0]] = Destringify(w[1:])

        return temp


    def RecvFromSever(self) -> Tuple[DefaultDict, bool]:

        if self.socket is None:
            logger.error(f"!! connection closed abrubtly on port: {self.port}")
            return DefaultDict(), False

        sockdata: str = ''
        self.socket.settimeout(self.timeout)


        while True:
            try:
                sockdata = self.socket.recvfrom(self.DataSize)[0].decode('utf-8')
                if self.debug: print("\nrecv", sockdata)
            except Exception as e:
                logger.exception(f"{e}")

            if '***shutdown***' in sockdata:
                logger.error(f"server has stopped the race on port {self.port}.")
                logger.info(f"closing connection . . .")
                return DefaultDict(), False

            elif '***restart***' in sockdata:
                logger.warning(f"server has restarted the race on port {self.port}")
                logger.error(f"client shutting down...")
                return DefaultDict(), False

            elif not sockdata:
                logger.error(f"waiting for data on port: {self.port}")

            else:
                if self.debug:
                    logger.info(f"recv: {sockdata}")
                return self._Deserialize(sockdata), True


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


    def Shutdown(self):
        if not self.socket:
            logger.error(f"server connection not establised / closed abrutly on port: {self.port}")
            logger.warning(f"unable to close gracefully on port: {self.port}")
            return

        self.socket.close()
        self.socket = None
        logger.info(f"server connection closed on port: {self.port}")


def RandomDrive(actionDict: Dict) -> Dict:

    response ={
        'accel':0.2,
        'brake':0,
        'clutch':0,
        'gear':1,
        'steer':0,
        'focus':[-90,-45,0,45,90],
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