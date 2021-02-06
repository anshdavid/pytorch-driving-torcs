import socket
import sys
from src.PyAgent.connection.server import ServerState
from src.PyAgent.connection.action import DriverAction
from src.PyAgent.connection.utils import DataSize
from src.PyAgent.connection.utils import PI

import logging

from src.logger import logger
logger = logging.getLogger(__name__)


class Client():
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 3001,
        sid: str = 'SCR',
        epochs: int = 100,
        steps: int = 50000,  # 50steps/second
        trackname: str = 'unknown',
        stage: int = 3,
        debug: bool = False,
        vision: bool = False):


        self.host = host
        self.port = port
        self.sid = sid
        self.maxEpisodes = epochs
        self.steps = steps
        self.trackname = trackname
        self.stage = stage # 0=Warm-up, 1=Qualifying 2=Race, 3=unknown <Default=3>
        self.debug = False
        self.vision = vision

        self.instanceServerState = ServerState()
        self.instanceDriverAction = DriverAction()
        self.socket = None

        self._SetupConnection()


    @property
    def ServerStateDict(self):
        return self.instanceServerState.stateDict

    @property
    def DriverActionDict(self):
        return self.instanceDriverAction.actionDict


    def _SetupConnection(self) -> bool:

        try:
            self.socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            logger.exception(f"{e}")
            logger.error(f"could not create socket")
            return False

        self.socket.settimeout(1)
        retryCount = 5

        while True:
            # This string establishes track sensor angles! You can customize them.
            #a= "-90 -75 -60 -45 -30 -20 -15 -10 -5 0 5 10 15 20 30 45 60 75 90"
            # xed- Going to try something a bit more aggressive...
            sensorAngles = "-45 -19 -12 -7 -4 -2.5 -1.7 -1 -.5 0 .5 1 1.7 2.5 4 7 12 19 45"

            initmsg = f"{self.sid}(init {sensorAngles})"

            try:
                self.socket.sendto(initmsg.encode(), (self.host, self.port))
            except Exception as e:
                logger.exception(f"{e}")
                logger.error(f"error sending message")
                if self.debug:
                    logger.debug(f"{initmsg}")
                return False


            sockdata: str = ''

            try:
                sockdata_, addr= self.socket.recvfrom(DataSize)
                sockdata = sockdata_.decode('utf-8')
            except Exception as e:
                logger.exception(f"{e}")
                logger.warning(f"waiting for server on port: {self.port}, countdown {retryCount}")

                retryCount -= 1
                if retryCount < 0:
                    # print("relaunch torcs")
                    # os.system('pkill torcs')
                    # time.sleep(1.0)
                    # if self.vision is False:
                    #     os.system('torcs -nofuel -nodamage -nolaptime &')
                    # else:
                    #     os.system('torcs -nofuel -nodamage -nolaptime -vision &')

                    # time.sleep(1.0)
                    # os.system('sh autostart.sh')
                    retryCount = 5

            if '***identified***' in sockdata:
                logger.info(f"client identified connected on port: {self.port}")
                return True


    def GetServerInput(self):
        # Server input is stored in a ServerState object

        if not self.socket:
            logger.error(f"server connection not establised {self.port}")
            exit()
            return

        sockdata: str = ''

        while True:
            try:
                sockdata_,addr= self.socket.recvfrom(DataSize)
                sockdata = sockdata_.decode('utf-8')
            except Exception as e:
                logger.exception(f"{e}")
                logger.error(f"unable to recieve/decode data from torcs server")

            if '***identified***' in sockdata:
                logger.info(f"Client connected on port: {self.port}")
                continue

            elif '***shutdown***' in sockdata:
                logger.error(f"server has stopped the race on port {self.port}.")
                logger.info(f"you were in {self.instanceServerState.stateDict['racePos']} place.")
                logger.info(f"client shutting down...")
                self.Shutdown()

            elif '***restart***' in sockdata:
                logger.warning(f"server has restarted the race on port {self.port}")
                logger.error(f"client shutting down...")
                self.Shutdown()

            elif not sockdata:
                logger.error(f"no data recieved from server on port: {self.port}")

            else:
                self.instanceServerState.ParseServerStr(sockdata)
                if self.debug:
                    logger.debug(f"{self.instanceServerState}")
                break


    def RespondToServer(self):

        if not self.socket:
            logger.error(f"server connection not establised {self.port}")
            exit()
            return

        message: str = ''
        try:
            message = repr(self.instanceDriverAction)
            # print("responce", message)
            self.socket.sendto(message.encode(), (self.host, self.port))
        except Exception as e:
            logger.exception(f"{e}")
            logger.exception(f"error sending to server on port {self.port}")
            if self.debug:
                logger.debug(self.instanceDriverAction.FancyOut())
            logger.error(f"closing connection")
            sys.exit(-1)


    def Shutdown(self):

        if not self.socket:
            logger.error(f"server connection not establised {self.port}")
            logger.info(f"retrying to connect ... of port: {self.port}")
            flag = self._SetupConnection()
            if not flag:
                logger.error(f"server shutting down reconnecting to {self.port} failed")
                return


        logger.info(f"race terminated or {self.steps} steps elapsed.")
        logger.info(f"shutting down client connection on port {self.port}")

        self.socket.close()
        self.socket = None


def DriveExample(client: Client):
    '''This is only an example. It will get around the track but the
    correct thing to do is write your own `drive()` function.'''

    S = client.instanceServerState.stateDict
    R= client.instanceDriverAction.actionDict

    target_speed=100

    # Steer To Corner
    R['steer']= S['angle']*10 / PI
    # Steer To Center
    R['steer']-= S['trackPos']*.10

    # Throttle Control
    if S['speedX'] < target_speed - (R['steer']*50):
        R['accel']+= .01
    else:
        R['accel']-= .01
    if S['speedX']<10:
       R['accel']+= 1/(S['speedX']+.1)

    # Traction Control System
    if ((S['wheelSpinVel'][2]+S['wheelSpinVel'][3]) -
       (S['wheelSpinVel'][0]+S['wheelSpinVel'][1]) > 5):
       R['accel']-= .2

    # Automatic Transmission
    R['gear']=1
    if S['speedX']>50:
        R['gear']=2
    if S['speedX']>80:
        R['gear']=3
    if S['speedX']>110:
        R['gear']=4
    if S['speedX']>140:
        R['gear']=5
    if S['speedX']>170:
        R['gear']=6
    return