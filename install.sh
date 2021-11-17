
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


PY_REP_LINK=https://github.com/stepjam/PyRep.git
PY_REP_DIR=PyRep
PY_REP_ROOT=${THESIS_ROOT}/${PY_REP_DIR}


VENV=${HOME}/.NICO-python3
VENV_ACTIVATE=${VENV}/bin/activate


export COPPELIASIM_ROOT=${COPPELIASIM_ROOT}
echo export COPPELIASIM_ROOT=${COPPELIASIM_ROOT} >> ${HOME}/.bashrc
echo export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$COPPELIASIM_ROOT >> ${HOME}/.bashrc
echo export QT_QPA_PLATFORM_PLUGIN_PATH=$COPPELIASIM_ROOT >> ${HOME}/.bashrc


function install_ros() {
	sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
	curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
	sudo apt update
	sudo apt install ros-noetic-desktop-full -y
	source ${ROS_SETUP_BASH}
	sudo apt install ros-noetic-moveit -y
}


function install_pyrep() {
	if [ ! -d ${PY_REP_ROOT} ]
	then
		git clone ${PY_REP_LINK}
	fi
	cd ${PY_REP_ROOT}
	pip install -r requirements.txt
	pip install .
	cd -
}

function install_deps() {
	sudo apt update && DEBIAN_FRONTEND=noninteractive  sudo apt install -y tzdata keyboard-configuration
	sudo apt update && sudo apt install -y vim wget curl git python3 python3-pip python3-venv lsb-release \
	portaudio19-dev python3-pyaudio libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg python3-empy
	sudo pip install virtualenv
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
	source ~/.bashrc
	bash ${NICO_INSTALL_SH}
}


function build_html_docs() {
	cd ${NICO_ROOT}
	source ${HOME}/.bashrc
	source api/activate.bash
    source api/pyrep_env.bash
	cd api-doc/
	make html
	cd -
}


install_deps
download_sources
install
source ${VENV_ACTIVATE}
pip install eigenpy defusedxml pyserial pypot
install_pyrep
build_html_docs
