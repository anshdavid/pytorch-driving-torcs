# server ret code

import os
import re
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy

from gym import spaces
from src.logger import logger

SERVERCODE_TIMEOUT: int = -4  # -> timeout / unhandled exception
SERVERCODE_RESTART: int = -3  # -> server restart
SERVERCODE_SHUTDOWN: int = -2  # -> server shutdown
SERVERCODE_NORESPONSE: int = -1  # -> no response from server
SERVERCODE_IDENTIFIED: int = 0  # -> client identified
SERVERCODE_OBSERVATION: int = 1  # -> return observation

DEFAULT_SENSOR_ANGLES: str = "-45 -19 -12 -7 -4 -2.5 -1.7 -1 -.5 0 .5 1 1.7 2.5 4 7 12 19 45"

UDP_MSGLEN = 2 ** 11

SHARED_MEM_KEY = 1234

OBSERVATION_KEYS: List[str] = [
    "angle",
    "curLapTime",
    "damage",
    "distFromStart",
    "distRaced",
    "totalTime",
    "trackLen",
    "fuel",
    "gear",
    "lastLapTime",
    "opponents",
    "racePos",
    "rpm",
    "speedX",
    "speedY",
    "speedZ",
    "track",
    "trackPos",
    "wheelSpinVel",
    "z",
    "focus",
    "x",
    "y",
    "roll",
    "pitch",
    "yaw",
    "speedGlobalX",
    "speedGlobalY",
]

OBSERVATION_SAMPLE: List[str] = [
    "angle",
    "damage",
    "distRaced",
    "rpm",
    "speedX",
    "speedY",
    "speedZ",
    "wheelSpinVel",
    "z",
    "x",
    "y",
    "roll",
    "pitch",
    "yaw",
    "speedGlobalX",
    "speedGlobalY",
]

ACTION_SPACE: Dict[str, spaces.Box] = {
    "accel": spaces.Box(low=0, high=1, shape=(1,), dtype=numpy.float16),
    "brake": spaces.Box(low=0, high=1, shape=(1,), dtype=numpy.float16),
    "steer": spaces.Box(low=-1, high=1, shape=(1,), dtype=numpy.float16),
}

TRACKS: Dict[str, List[str]] = {
    "dirt": ["dirt-1", "dirt-2", "dirt-3", "dirt-4", "dirt-5", "dirt-6", "mixed-1", "mixed-2"],
    "road": [
        "alpine-1",
        "corkscrew",
        "e-track-3",
        "g-track-2",
        "ole-road-1",
        "street-1",
        "alpine-2",
        "e-track-6",
        "g-track-3",
        "ruudskogen",
        "wheel-1",
        "brondehach",
        "e-track-2",
        "forza",
        "spring",
        "wheel-2",
        "aalborg",
        "e-track-1",
        "e-track-5",
        "e-track-1",
        "e-track-5",
        "eroad",
        "e-track-4",
        "g-track-1",
    ],
    "oval": [
        "a-speedway",
        "b-speedway",
        "e-speedway",
        "g-speedway",
        "michigan",
        "c-speedway",
        "d-speedway",
        "f-speedway",
    ],
}

# docker run -e DISPLAY=unix$DISPLAY -p 3001:3001/udp -v /tmp/.X11-unix:/tmp/.X11-unix:ro -e QT_X11_NO_MITSHM=1 --gpus=0 --shm-size=4g --ipc=host
# -it --rm -d gerkone/torcs torcs


def StartContainer(image: str = r"gerkone/torcs", port: int = 3001, timeoutInSecs: int = 15) -> Optional[str]:
    timer = timedelta(seconds=timeoutInSecs)
    nPeriod = timer + datetime.now()
    break_: bool = False

    containerID = subprocess.check_output(["docker", "ps", "-q", "--filter", "ancestor=" + image]).decode(
        "utf-8"
    )

    dockerCMD: List[str] = []
    pathRaceXML = os.environ["TORCSPROJECT"] + "/configs/config/raceman/practice.xml"

    if len(containerID) == 0:
        dockerCMD.extend(
            [
                "docker",
                "run",
                "-e",
                "DISPLAY=" + "unix" + os.environ["DISPLAY"],
                "-p",
                f"{port}:{port}/udp",
                "-v",
                "/tmp/.X11-unix:/tmp/.X11-unix:ro",
                "-v",
                f"{pathRaceXML}:/usr/local/share/games/torcs/config/raceman/practice.xml:ro",
                "-e",
                "QT_X11_NO_MITSHM=1",
                "--gpus=0",
                "--shm-size=4g",
                "--ipc=host",
            ]
        )

        dockerCMD.extend(["--rm", "-it", "-d", image])

        subprocess.Popen(dockerCMD, stdout=subprocess.DEVNULL)
        time.sleep(0.5)

        while len(containerID) == 0:
            time.sleep(0.5)
            if datetime.now() > nPeriod:
                break_ = True
                break
            containerID = subprocess.check_output(
                ["docker", "ps", "-q", "--filter", "ancestor=" + image]
            ).decode("utf-8")

        if break_:
            logger.info("unable to start torcs container")
            return None

        containerID = re.sub("[^a-zA-Z0-9 -]", "", containerID)

    logger.info(f"torcs container running with ID: {containerID}")

    return containerID


def StopContainer(containerID: str):
    logger.info(f"stopping torcs container {containerID}")
    subprocess.Popen(["docker", "kill", containerID], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def StartTorcs(containerID: str, params: List[str] = ["-nofuel"], vision: bool = False):
    # sourcery skip: merge-list-extend, move-assign, simplify-boolean-comparison
    # "-nodamage", "-nolaptime"
    command: List[str] = []
    command.extend(["docker", "exec", containerID, "torcs"])
    command.extend(params)
    if vision is True:
        command.append("-vision")

    logger.info(f"staring torcs on container {containerID}, with params {params} and vision: {vision}")
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def StopTorcs(containerID: str):  # sourcery skip: merge-list-extend
    logger.info(f"stopping torcs process on container {containerID}")
    subprocess.Popen(
        ["docker", "exec", containerID, "pkill", "torcs"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# def agent_from_module(mod_name, run_path):
#     spec = importlib.util.spec_from_file_location(mod_name, run_path)
#     mod = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(mod)
#     return getattr(mod, mod_name)


# def change_track(race_type, track, tracks_categories):
#     from lxml import etree

#     filename = race_type + ".xml"
#     torcs_race_xml = os.path.join(os.getcwd(), "torcs/configs/config/raceman", filename)
#     config = etree.parse(torcs_race_xml)
#     for section in config.iter("section"):
#         if section.get("name") == "Tracks":
#             for attr in section.iter("attstr"):
#                 if attr.get("name") == "name":
#                     attr.set("val", track)
#                 if attr.get("name") == "category":
#                     cat = ""
#                     for c in tracks_categories.keys():
#                         if track in tracks_categories[c]:
#                             cat = c
#                     attr.set("val", cat)

#     with open(torcs_race_xml, "wb") as doc:
#         doc.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
#         doc.write(etree.tostring(config, pretty_print=True))


# def get_track(race_type):
#     from lxml import etree

#     track = ""
#     filename = race_type + ".xml"
#     torcs_race_xml = os.path.join(os.getcwd(), "torcs/configs/config/raceman", filename)
#     config = etree.parse(torcs_race_xml)
#     for section in config.iter("section"):
#         if section.get("name") == "Tracks":
#             for attr in section.iter("attstr"):
#                 if attr.get("name") == "name":
#                     track = attr.get("val")

#     return track


# def change_car(race_type, car):
#     from lxml import etree

#     scr_xml = os.path.join(os.getcwd(), "torcs/configs/drivers/scr_server/scr_server.xml")
#     config = etree.parse(scr_xml)
#     for section in config.iter("section"):
#         if section.get("name") == "0":
#             for attr in section.iter("attstr"):
#                 if attr.get("name") == "car name":
#                     attr.set("val", car)

#     with open(scr_xml, "wb") as doc:
#         doc.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
#         doc.write(etree.tostring(config, pretty_print=True))


# def change_driver(race_type, driver_id, driver_module):
#     from lxml import etree

#     filename = race_type + ".xml"
#     torcs_race_xml = os.path.join(os.getcwd(), "torcs/configs/config/raceman", filename)
#     config = etree.parse(torcs_race_xml)
#     for section in config.iter("section"):
#         if section.get("name") == "Drivers":
#             for subsection in section.iter("section"):
#                 if subsection.get("name") != "Drivers":
#                     for attr in subsection.iter("attnum"):
#                         if attr.get("name") == "idx":
#                             attr.set("val", driver_id)
#                     for attr in subsection.iter("attstr"):
#                         if attr.get("name") == "module":
#                             attr.set("val", driver_module)

#     with open(torcs_race_xml, "wb") as doc:
#         doc.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
#         doc.write(etree.tostring(config, pretty_print=True))

