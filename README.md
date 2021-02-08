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