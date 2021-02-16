# PYTORCH-DRIVING-TORCS

```shell
WORK IN PROGRESS
```

Version of [TORCS 1.3.7](https://github.com/fmirus/torcs-1.3.7) with [SCR patch](https://github.com/barisdemirdelen/scr-torcs-1.3.7) and an additional patch to send the current game image to another application via shared memory.
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
    │   │   ├── backupenv.py
    │   │   └── env.py
    │   ├── logger.py
    │   ├── screengrabtest.py
    │   └── torcs
    │       └── README.md
    ├── test
    │   ├── testconnection.py
    │   └── testexampleagent.py
    ├── license
    ├── README.md
    ├── test.py
    └── train.py

<!-- tree . -l 10 -I '.vscode|omnet|samples|__pycache__|__init__.py|*.pyc|Torcs' -->



# Changelog

## [0.1] - 2021-02-07

### Added

- new client server connection
- new Gym environment TorcsEnv

### Changed

- gym_torcs env

### Removed

- Snakeoil client implementation

### TODO

- complete TorcsEnv implementaion
- implement PPO / TRPO / DDPG

## [0.2] - 2021-02-15

### Added

- new Torcs_Env
- new Screengrab using python-mss

### Changed

- Agent

### Fixed

- client connection states

### Removed

- snakeoit client, agent and env


<!-- ```shell
Action          Range       (unit)      Datatype
Acceleration    [0,+1]                  Double
Brake           [0,+1]                  Double
Gear            {-1..0..+6}             Double
Steer           [-1,+1]                 Double
Clutch          [-1,+1]                 Double
```

Availabel sensor observations
- angle         [-PI,+PI]   rad
- damage        [0, +inf]
- distFromStart [0, +inf]
- distRaced     [0, +inf]
- rpm           [0, +inf]
- speedX        [-inf,+inf]
- speedY        [-inf,+inf]
- track         19*[0,200]
- trackPos      [-1,+1]
- wheelSpinVel  4*[0,+inf] -->

<!-- - curLapTime    [0, +inf]   secs
- fuel          [0, +inf]
- gear          {-1,0 - 6}
- lastLapTime   [0, +inf]
- racePos       {1 - N}
- speedZ        [-inf,+inf]
- opponents
- z
- focus
- x
- y
- roll
- pitch
- yaw
- speedGlobalX
- speedGlobalY. -->