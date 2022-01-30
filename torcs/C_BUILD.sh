#!/bin/bash

CFLAGS="-fPIC -ansi"
CPPFLAGS=$CFLAGS
CXXFLAGS=$CFLAGS

TARGETDIR=$(pwd)/BUILD
./configure --prefix=$TARGETDIR

make clean
make
make install
make datainstall

# rm -rf /usr/local/share/games/torcs/config
# rm -rf /usr/local/share/games/torcs/drivers
# mkdir -p /root/.torcs/
# cp -R configs/* /usr/local/share/games/torcs
# cp -R configs/* /root/.torcs