import time

from pyrep import PyRep
from pyrep.robots.arms.panda import Panda
from pyrep.objects.shape import Shape

import numpy as np

SCENE_FILE = 'scene_reinforcement_learning_env.ttt'
POS_MIN, POS_MAX = [0.8, -0.2, 1.0], [1.0, 0.2, 1.4]

pr = PyRep()
pr.launch(SCENE_FILE, headless=False)
pr.start()
agent = Panda()
agent.set_control_loop_enabled(False)
agent.set_motor_locked_at_zero_velocity(True)
target = Shape('target')

_, intervals = agent.get_joint_intervals()
low = [j[0] for j in intervals]
high = [j[1] for j in intervals]

while True:
	action = list(np.random.uniform(low=-1, high=1, size=(7,)))
	agent.set_joint_target_velocities(action)
	# time.sleep(1)
	pr.step()