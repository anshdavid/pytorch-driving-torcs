#!/bin/sh

# catch to Trap error code before exit
set -e
trap 'catch $?' EXIT
catch() {
    if [ "$1" != "0" ]; then
        echo ""
        echo "using exsisting container..."
        # run_existing
        docker start sonoshee
        docker attach sonoshee
    fi
}

run_build (){

    echo "creating docker container..."

    docker run -it -u user -v "$(pwd)/torcs:/home/user/torcs" -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" -v $XAUTH:$XAUTH -e DISPLAY=$DISPLAY -e QT_X11_NO_MITSHM=1 -e XAUTHORITY=$XAUTH -p 3001:3001/udp --gpus 0 --ipc=host --shm-size=4g --name sonoshee rltorcs:0.1
}

XAUTH=/tmp/.docker.xauth

touch $XAUTH

if [ ! -f $XAUTH ]
then
    xauth_list=$(xauth nlist :0 | sed -e 's/^..../ffff/')
    if [ ! -z "$xauth_list" ]
    then
        echo $xauth_list | xauth -f $XAUTH nmerge -
    else
        touch $XAUTH
    fi
    chmod a+r $XAUTH
fi

run_build


# ### for the lazy and reckless
#     xhost +local:root
#     xhost -local:root

# ###  opening up xhost for specific system
#     export containerId=$(docker ps -l -q)
#     xhost +local:`docker inspect --format='{{ .Config.Hostname }}' $containerId`


# running raw
# docker run --gpus 0 -e QT_X11_NO_MITSHM=1 --shm-size=4g --ipc=host -v /tmp/.X11-unix:/tmp/.X11-unix:ro -e DISPLAY=unix$DISPLAY -p 3001:3001/udp -it --rm -d gerkone/torcs

# running with racexml
#docker run --gpus=0 -e QT_X11_NO_MITSHM=1 --shm-size=4g --ipc=host -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v /home/wolf/codebase/python/pytorch-driving-torcs/torcs/configs/config/raceman/practice.xml:/usr/local/share/games/torcs/config/raceman/practice.xml:ro -e DISPLAY=unix$DISPLAY -p 3001:3001/udp -it --rm -d gerkone/torcs torcs