# PYTORCH-DRIVING-TORCS

```shell
WORK IN PROGRESS
```

<!-- Version of [TORCS 1.3.7](https://github.com/fmirus/torcs-1.3.7) with [SCR patch](https://github.com/barisdemirdelen/scr-torcs-1.3.7) and an additional patch to send the current game image to another application via shared memory. -->
<!-- http://xed.ch/p/snakeoil/ -->


## Directory Structure

    .
    ├── config
    │   ├── default.xml
    │   ├── log.conf
    │   ├── practice.xml
    │   └── raceconfig.xml
    ├── docs
    │   ├── lxd.md
    │   └── torcs.md
    ├── logs
    │   └── logger.log
    ├── models
    ├── reports
    │   └── architecture.csv
    ├── resources
    │   ├── figures
    │   └── torcs
    │       ├── fmirus-torcs.zip
    │       └── SCR2015-Snakeoil_entry.tar.gz
    ├── src
    │   ├── architecture
    │   │   └── agent.py
    │   ├── connection
    │   │   ├── client.py
    │   │   └── README.md
    │   ├── gym
    │   │   └── env.py
    │   ├── logger.py
    │   ├── torcs
    │   │   └── README.md
    │   └── vision
    │       └── screengrab.py
    ├── test
    │   ├── testclient.py
    │   ├── testenv.py
    │   └── testgrab.py
    ├── CHANGELOG
    ├── license
    ├── README.md
    ├── test.py
    └── train.py


<!-- tree . -l 10 -I '.vscode|omnet|samples|__pycache__|__init__.py|*.pyc|Torcs' -->


    Action          Range           (unit)      Datatype

    accel           [0,+1]                  Double
    brake           [0,+1]                  Double
    steer           [-1,+1]                 Double

    Observations     Range          (unit)      Datatype

    angle           [-PI,+PI]   rad         Double
    damage          [0, +inf]               Double
    distFromStart   [0, +inf]               Double
    distRaced       [0, +inf]               Double
    gear            {-1..0..+6}             Integer
    rpm             [0, +inf]               Double
    speedX          [-inf,+inf]             Double
    speedY          [-inf,+inf]             Double
    track           19*[0,200]              Double
    trackPos        [-1,+1]                 Double
    wheelSpinVel    4*[0,+inf]  (rad/s)     Double


<!-- 
accel           [0,+1]                  Double
brake           [0,+1]                  Double
steer           [-1,+1]                 Double
gear            {-1..0..+6}             Integer
clutch          [-1,+1]                 Double -->

<!-- { SAMPLE
"angle": 0.000920947,
"curLapTime": 41.026,
"damage": 0.0,
"distFromStart": 1662.0,
"distRaced": 1.05664,
"fuel": 94.0,
"gear": 1.0,
"lastLapTime": 0.0,
"opponents": [
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0,
    200.0
],
"racePos": 1.0,
"rpm": 942.478,
"speedX": 0.771931,
"speedY": -0.0193664,
"speedZ": -0.00287922,
"track": [
    7.07843,
    15.4008,
    24.1562,
    41.3426,
    72.6431,
    129.035,
    126.461,
    124.001,
    122.099,
    120.048,
    117.814,
    115.34,
    111.27,
    104.713,
    70.7378,
    40.7174,
    23.9421,
    15.315,
    7.06373
],
"trackPos": -0.00011816,
"wheelSpinVel": [
    1.22379,
    -0.445772,
    -0.258325,
    3.88605
],
"z": 0.350954,
"focus": [
    -1.0,
    -1.0,
    -1.0,
    -1.0,
    -1.0
],
"x": 251.057,
"y": 19.9995,
"roll": 4.97566e-06,
"pitch": 0.00846777,
"yaw": -0.000921725,
"speedGlobalX": 0.21442,
"speedGlobalY": -0.00557927
} -->