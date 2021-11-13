
set -e

THESIS_ROOT=$(pwd)

COPPELIASIM_TAR=CoppeliaSim_Edu_V4_2_0_Ubuntu20_04.tar.xz
COPPELIASIM_LINK=https://www.coppeliarobotics.com/files/${COPPELIASIM_TAR}
COPPELIASIM_DIR=CoppeliaSim_Edu_V4_2_0_Ubuntu20_04
COPPELIASIM_ROOT=${THESIS_ROOT}/${COPPELIASIM_DIR}


NICO_LINK=https://github.com/janetatomas11/NICO-software.git
NICO_DIR=NICO-software
NICO_ROOT=${THESIS_ROOT}/${NICO_DIR}
NICO_API_SRC=${NICO_DIR}/api/src
NICO_INSTALL_SH=${NICO_DIR}/api/NICO-python3.bash


ROS_SETUP_BASH=/opt/ros/noetic/setup.bash


export DEBIAN_FRONTEND=noninteractive
export COPPELIASIM_ROOT=${COPPELIASIM_ROOT} >> ${HOME}/.bashrc

function install_ros() {
	sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
	curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
	sudo apt update
	sudo apt install ros-noetic-desktop-full -y
	source ${ROS_SETUP_BASH}
}


function install_deps() {
	sudo apt update && sudo apt install -y vim wget curl git libportaudio2 python3 python3-pip \
	portaudio19-dev python3-pyaudio libasound-dev lsb-release sudo \
	portaudio19-dev libportaudio2 libportaudiocpp0
	pip3 install virtualenv
	install_ros
}


function download_sources() {
	if [ ! -d ${COPPELIASIM_ROOT} ]
	then
		wget ${COPPELIASIM_LINK}
		tar -xvf ${COPPELIASIM_TAR}
	fi

	if [ ! -d ${NICO_ROOT} ]
	then
		git clone ${NICO_LINK}
	fi
}


function install() {
	echo export COPPELIASIM_ROOT=${COPPELIASIM_ROOT} >> ${HOME}/.bashrc
	source ~/.bashrc
	bash ${NICO_INSTALL_SH}
}


install_deps
download_sources
install
