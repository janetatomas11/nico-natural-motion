FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN rm /var/lib/apt/lists/* -rf

RUN apt update && apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update && apt install -y ssh virtualenv sudo tzdata python3.7-dev cmake
RUN apt update && apt install -y wget vim git portaudio19-dev ffmpeg python3.7-distutils

RUN rm -f /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/python3.7 /usr/bin/python3 && \
    ln -s /usr/bin/python3.7 /usr/bin/python

RUN apt update && apt install pip -y

ADD scripts/source /user/bin/source

RUN useradd -ms /bin/bash nicomotion

RUN adduser nicomotion sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /opt

USER nicomotion

RUN pip install --upgrade pip

RUN sudo chown -R nicomotion:nicomotion /opt/

RUN wget https://www.coppeliarobotics.com/files/CoppeliaSim_Edu_V4_3_0_rev10_Ubuntu20_04.tar.xz

RUN tar -xf CoppeliaSim_Edu_V4_3_0_rev10_Ubuntu20_04.tar.xz

ENV COPPELIASIM_ROOT=/opt/CoppeliaSim_Edu_V4_3_0_rev10_Ubuntu20_04/
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$COPPELIASIM_ROOT
ENV QT_QPA_PLATFORM_PLUGIN_PATH=$COPPELIASIM_ROOT

RUN git clone https://github.com/knowledgetechnologyuhh/NICO-software.git

WORKDIR /home/nicomotion/

RUN virtualenv ~/.NICO-python3/ --python=/usr/bin/python3.7

WORKDIR /opt/NICO-software

RUN bash api/NICO-python3.bash
