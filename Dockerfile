FROM ubuntu:20.04

WORKDIR thesis

RUN apt update && apt install sudo

RUN useradd nicouser

RUN echo 'nicouser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER nicouser

RUN sudo apt update && DEBIAN_FRONTEND=noninteractive sudo apt install -y tzdata keyboard-configuration

RUN	sudo apt update && sudo apt install -y vim wget curl git python3 python3-pip python3-venv lsb-release \
	portaudio19-dev python3-pyaudio libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg python3-empy

RUN sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list' && \
	curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add - && \
	sudo apt update && \
	sudo apt install ros-noetic-desktop-full -y && \
	bash /opt/ros/noetic/setup.bash && \
	sudo apt install ros-noetic-moveit -y

WORKDIR /home/nicouser/thesis

RUN sudo chown -R nicouser:nicouser /home/nicouser
RUN sudo chmod 777 /home/nicouser

RUN wget https://www.coppeliarobotics.com/files/CoppeliaSim_Edu_V4_2_0_Ubuntu20_04.tar.xz

RUN tar -xvf CoppeliaSim_Edu_V4_2_0_Ubuntu20_04.tar.xz

RUN pip install virtualenv

RUN git clone https://github.com/janetatomas11/NICO-software.git

ADD install.sh .
