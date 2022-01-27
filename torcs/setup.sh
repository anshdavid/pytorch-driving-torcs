#!/bin/bash

CFLAGS="-fPIC -ansi"
CPPFLAGS=$CFLAGS
CXXFLAGS=$CFLAGS

./configure --prefix=$(pwd)/BUILD

make clean
make
make install
make datainstall


# cp -R /usr/local/share/games/torcs /usr/local/share/games/torcs_backup
# rm -rf /usr/local/share/games/torcs/config
# rm -rf /usr/local/share/games/torcs/drivers
# mkdir -p /root/.torcs/
# cp -R configs/* /usr/local/share/games/torcs
# cp -R configs/* /root/.torcs