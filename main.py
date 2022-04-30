import numpy as np

from turtle import TurtleEnv
from stable_baselines3 import TD3
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise

n_actions = 2
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

scene = 'configs/pyrep/scene_turtlebot_free.ttt'
env = TurtleEnv(scene)

model = TD3.load('saved/turtle-free.pickle')



# model = TD3("MlpPolicy", env, action_noise=action_noise, verbose=1, learning_rate=0.01)
# model.learn(total_timesteps=10000, log_interval=10)
# model.save('saved/turtle-free.pickle')