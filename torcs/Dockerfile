FROM nvidia/cudagl:11.4.0-base


ENV DEBIAN_FRONTEND=noninteractive

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES \
    ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
    ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

LABEL maintainer="ansh1990@gmail.com"
LABEL version="0.1.0"
LABEL description="torcs"

# basic
RUN apt-get update && apt-get -y install \
    sudo \
    apt-utils \
    gnupg2 \
    wget \
    curl \
    lsb-release \
    software-properties-common \
    build-essential \
    make \
    gdb \
    openssh-server \
    gdbserver \
    libnss3-dev \
    valgrind \
    libssl-dev \
    cmake \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*


# torcs requierments + `c++` + multimedia
RUN apt-get update && apt-get -y install \
    autotools-dev \
    bison \
    cmake \
    freeglut3-dev \
    g++ \
    g++-multilib \
    gcc \
    gcc-multilib \
    git \
    lib32z1 \
    libalut-dev \
    libboost-all-dev \
    libbz2-dev \
    libgl1-mesa-dev \
    libglib2.0-dev \
    libglm-dev \
    libglu1-mesa-dev \
    libicu-dev \
    liblz4-dev \
    libmirclient-dev \
    libopenal-dev \
    libpciaccess0 \
    libplib-dev \
    libpng-dev \
    libvorbis-dev \
    libwayland-dev \
    libx11-dev \
    libx11-xcb-dev \
    libxcb-dri3-0 \
    libxcb-dri3-dev \
    libxcb-ewmh-dev \
    libxcb-keysyms1-dev \
    libxcb-present0 \
    libxcb-randr0-dev \
    libxdamage1 \
    libxi-dev \
    libxmu-dev \
    libxrandr-dev \
    libxrender-dev \
    libxxf86vm-dev \
    libzstd-dev \
    mesa-common-dev \
    python3 \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ARG USER_ID
ARG GROUP_ID

RUN touch ~/.Xauthority

RUN addgroup --gid $GROUP_ID user \
    && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user \
    && adduser user sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER user

WORKDIR /home/user/torcs