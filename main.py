#!/usr/bin/env python

from env import NicoEnv, left_arm
from os.path import dirname, abspath
import numpy as np
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import TD3

config_dir = "configs"
json_config = F"{config_dir}/nico_humanoid_vrep.json"
scene = F"{config_dir}/NICO-seated.ttt"

env = NicoEnv(
    config_file=json_config,
    scene_file=scene,
    joints=['l_shoulder_y', 'l_shoulder_z', 'l_arm_x', 'l_elbow_y', 'l_wrist_z', 'l_wrist_x']
)

model = TD3("MlpPolicy", env=env, verbose=1)
model.learn(total_timesteps=10000, log_interval=10)
