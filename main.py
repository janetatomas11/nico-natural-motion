#!/usr/bin/env python

from env import NicoEnv, left_arm
from os.path import dirname, abspath
import numpy as np
from stable_baselines3.common.env_checker import check_env

nico_root = dirname(abspath(__file__)) + "/NICO-software"
config = F"{nico_root}/json/nico_humanoid_vrep.json"
scene = F"{nico_root}/v-rep/NICO-seated.ttt"

env = NicoEnv(
    config_file=config,
    scene_file=scene,
    goal=1,
    joints=['l_shoulder_y', 'l_shoulder_z', 'l_arm_x', 'l_elbow_y', 'l_wrist_z', 'l_wrist_x']
)

env._robot.startSimulation()

# check_env(env)