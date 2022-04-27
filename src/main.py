#!/usr/bin/env python

from env import NicoEnv, left_arm
from stable_baselines3 import TD3
from pathlib import Path

root = Path(__file__).resolve().parent.parent

configs = Path(root, "config")
json= Path(configs, "nico_humanoid_vrep.json")
scene = Path(configs, "NICO-standing.ttt")
save = Path(root, "save")

joints = ['l_shoulder_y']

env = NicoEnv(
    config_file=json,
    scene_file=scene,
    joints=joints,
    headless=False,
)

model = TD3("MlpPolicy", env=env, verbose=1, learning_rate=0.1)
model.learn(total_timesteps=300, log_interval=100)
model.save(Path(save, "nico.pickle"))
