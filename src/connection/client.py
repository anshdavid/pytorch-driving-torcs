# snakeoil extended with vision through shared memory
# Chris X Edwards <snakeoil@xed.ch>
# Gianluca Galletti


import time
from socket import AF_INET, SO_RCVBUF, SOCK_DGRAM, SOL_SOCKET
from socket import socket as Socket
from typing import Dict, List, Optional, Tuple, Union

from src.logger import logger
from src.utils import (
    DEFAULT_SENSOR_ANGLES,
    SERVERCODE_IDENTIFIED,
    SERVERCODE_NORESPONSE,
    SERVERCODE_OBSERVATION,
    SERVERCODE_RESTART,
    SERVERCODE_SHUTDOWN,
    SERVERCODE_TIMEOUT,
    UDP_MSGLEN,
)


class ServerState:
    def __init__(self) -> None:
        pass

    @staticmethod
    def Destringify(s: Union[int, str, List]):
        if not s:
            return s
        elif type(s) is str:
            try:
                return float(s)
            except ValueError:
                print(f"Could not find a value in {s}")
                return s
        elif type(s) is list:
            return ServerState.Destringify(s[0]) if len(s) < 2 else [ServerState.Destringify(i) for i in s]

    @staticmethod
    def Serialize(actionDict: Dict) -> str:
        out = str()
        for key, value in actionDict.items():
            out += (
                f'({key} {"%.3f" % value if type(value) is not list else " ".join([str(x) for x in value])})'
            )
        return out

    @staticmethod
    def Deserialize(serverString: str) -> Dict:
        out: Dict = {}
        inString = serverString.strip()[:-1]
        tokenzied = inString.strip().lstrip("(").rstrip(")").split(")(")
        for field in tokenzied:
            ob, *val = field.split(" ")
            out[ob] = ServerState.Destringify(val)
        return out


class Client:
    def __init__(
        self,
        host="localhost",
        port=3001,
        sid="SCR",
        sensorAngle: str = DEFAULT_SENSOR_ANGLES,
        verbose=False,
        timeout: int = 15,
        delay: float = 0,
    ):

        self.host = host
        self.port = port
        self.sid = sid

        self.sensorAngles = sensorAngle

        self.verbose = verbose

        self.timeout = timeout
        self.delay = delay

        self._socket: Optional[Socket] = None

    @property
    def socket(self) -> Socket:
        assert self._socket
        return self._socket

    @socket.setter
    def socket(self, value: Socket) -> None:
        self._socket = value

    def CreateConnection(self) -> bool:
        try:
            self.socket = Socket(AF_INET, SOCK_DGRAM)
        except Exception as e:
            logger.error(f"could not create socket\n{e}")
            return False
        else:
            logger.info("binding socket")
        finally:
            # set socket receive buffer to 1 packet to avoid buffer bloat and packet accumulation
            self.socket.setsockopt(SOL_SOCKET, SO_RCVBUF, UDP_MSGLEN)
            self.socket.settimeout(self.timeout)
        return True

    def InitSensors(self) -> bool:
        try:
            self.socket.sendto(f"{self.sid}(init {self.sensorAngles})".encode(), (self.host, self.port))
        except Exception as e:
            logger.error(f"error sending message\n{e}")
            return False
        else:
            logger.info(f"init message sent with sensors {self.sensorAngles}")
        finally:
            logger.info(f"waiting for response 'InitSensors' to on port: {self.port}")
        return True

    def RecvFromSever(self) -> Tuple[Dict, int]:

        sockdata: str = ""

        try:
            sockdata = self.socket.recvfrom(UDP_MSGLEN)[0].decode("utf-8")
            if self.verbose:
                print("\nrecv", sockdata)
        except Exception as e:
            logger.exception(f"{e}")
            return dict(), SERVERCODE_TIMEOUT

        if "***restart***" in sockdata:
            logger.info(f"server restarted on port: {self.port}")
            return dict(), SERVERCODE_RESTART

        elif "***shutdown***" in sockdata:
            logger.info(f"server shutdown on port: {self.port}.")
            return dict(), SERVERCODE_SHUTDOWN

        elif not sockdata:
            logger.warning(f"server no response on port: {self.port}")
            return dict(), SERVERCODE_NORESPONSE

        elif "***identified***" in sockdata:
            logger.info(f"client identified connected on port: {self.port}")
            # * always delay few secs after starting round maybe ??
            time.sleep(self.delay)
            return dict(), SERVERCODE_IDENTIFIED
        else:
            if self.verbose:
                logger.info(f"recv: {sockdata}")
            return ServerState.Deserialize(sockdata), SERVERCODE_OBSERVATION
        return True

    def SendToServer(self, action: Dict) -> bool:
        if self.socket is None:
            logger.error(f"connection closed abrubtly on port: {self.port}")
            return False

        message: str = ""

        try:
            message = ServerState.Serialize(action)
            self.socket.sendto(message.encode(), (self.host, self.port))
        except Exception as e:
            logger.error(f"error sending to server on port {self.port}\n{e}")
            if self.verbose:
                logger.debug(f"{message}")
            return False
        return True

    def ServerRestart(self):
        logger.info(f"restart connection on port {self.port}")
        self.SendToServer({"meta": True})

    def ClientShutdown(self):
        self.ServerRestart()

        logger.info("closing connection ...")
        self.socket.close()

        logger.info(f"server connection closed on port: {self.port}")

