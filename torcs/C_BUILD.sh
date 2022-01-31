#!/bin/bash

TARGETDIR=$(pwd)/BUILD
./configure --prefix=$TARGETDIR
CFLAGS="-fPIC -ansi"
CPPFLAGS=$CFLAGS
CXXFLAGS=$CFLAGS
make clean
make
make install
make datainstall

rm -rf /usr/local/share/games/torcs/*
mkdir -p /root/.torcs/
cp -R configs/* /usr/local/share/games/torcs/
cp -R configs/* /root/.torcs/