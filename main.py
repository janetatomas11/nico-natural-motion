#!/usr/bin/env python

from env import NicoEnv, left_arm
from os.path import dirname, abspath
import numpy as np
from stable_baselines3 import TD3

config_dir = "configs"
json_config = F"{config_dir}/nico_humanoid_vrep.json"
scene = F"{config_dir}/NICO-standing.ttt"

joints = ['l_shoulder_y']

env = NicoEnv(
    config_file=json_config,
    scene_file=scene,
    joints=joints,
    headless=True,
)

model = TD3("MlpPolicy", env=env, verbose=1, learning_rate=0.1)
model.learn(total_timesteps=300, log_interval=100)
model.save(':'.join(joints))