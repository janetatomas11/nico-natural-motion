#!/usr/bin/env python

from env import NicoEnv
from stable_baselines3 import TD3
from simple_reacher import PandaReacher
config_dir = "configs"
json_config = F"{config_dir}/nico_humanoid_vrep.json"
scene = F"{config_dir}/NICO-standing.ttt"

env = NicoEnv(
    config_file=json_config,
    scene_file=scene,
    joints=['l_shoulder_z', 'l_arm_x', 'l_elbow_y', 'l_wrist_z'],
)

# env = PandaReacher(scene_file='../scene_reinforcement_learning_env.ttt')
model = TD3("MlpPolicy", env=env, verbose=1, learning_rate=0.01)
model.learn(total_timesteps=10000, log_interval=1000)
