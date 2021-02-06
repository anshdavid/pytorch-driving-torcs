# Dependencies

- build-essential
- cmake
- freeglut3
- freeglut3-dev
- libalut-dev
- libalut0
- libgl1-mesa-dev
- libglib2.0-dev
- libglu1-mesa
- libglu1-mesa-dev
- libopenal-data
- libopenal-dev
- libopenal1
- libplib-dev
- libplib1
- libpng-dev
- libportaudio2
- libsndio7.0
- libvorbis-dev
- libxi-dev
- libxi6
- libxmu-dev
- libxmu6
- libxrandr-dev
- libxrandr2
- libxrender-dev
- libxrender1
- libxxf86vm-dev
- mesa-common-dev
- mesa-utils
- sndiod
- zlib1g-dev


# locations

    prefix=/usr
    BINDIR=${prefix}/games
    LIBDIR=${prefix}/lib/x86_64-linux-gnu/torcs
    DATAROOTDIR=${prefix}/share
    DATADIR=$DATAROOTDIR/games/torcs
    VARDIR=/var/games/torcs
    LOCAL_CONF=$HOME/.torcs


# build from source

    export CFLAGS="-fPIC"
    export CPPFLAGS=$CFLAGS
    export CXXFLAGS=$CFLAGS
    ./configure --prefix="/home/ubuntu/torcs"
    make
    make install
    make datainstall

