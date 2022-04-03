#!/usr/bin/env python

from stable_baselines3 import TD3
from simple_reacher import PandaReacher

env = PandaReacher(scene_file='../scene_reinforcement_learning_env.ttt')
model = TD3("MlpPolicy", env=env, verbose=1, learning_rate=0.01)
model.learn(total_timesteps=10000, log_interval=1000)
