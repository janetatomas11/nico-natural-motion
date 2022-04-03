from gym import Env
from gym.spaces import Box
from pyrep.robots.arms.panda import Panda
from pyrep import PyRep
from pyrep.objects.shape import Shape
import numpy as np

POS_MIN, POS_MAX = [0.8, -0.2, 1.0], [1.0, 0.2, 1.4]


class PandaReacher(Env):
    def __init__(self, scene_file):
        self.pr = PyRep()
        self.pr.launch(scene_file, headless=False)
        self.pr.start()
        self.agent = Panda()

        _, intervals = self.agent.get_joint_intervals()
        self.low = [j[0] for j in intervals]
        self.high = [j[1] for j in intervals]

        self.observation_space = Box(low=np.array(self.low + POS_MIN), high=np.array(self.high + POS_MAX))
        self.action_space = Box(low=np.array(self.low), high=np.array(self.high))

        self.target = Shape('target')

        self._threshold = 0.05

    def _execute_action(self, action):
        self.agent.set_joint_positions(action)
        self.pr.step()

    def _get_state(self):
        return np.concatenate([self.agent.get_joint_positions(), self.target.get_position()])

    def _reward(self):
        a = self.agent.get_tip().get_position()
        b = self.target.get_position()
        diff = a - b
        return -np.matmul(diff, diff.transpose())

    def step(self, action):
        self._execute_action(action)
        observation = self._get_state()
        reward = self._reward()
        done = abs(reward) <= self._threshold
        info = {}
        print(reward)
        return observation, reward, done, info

    def reset(self):
        self._execute_action(self.action_space.sample())
        self.target.set_position(np.random.uniform(POS_MIN, POS_MAX))
        self.pr.step()

    def render(self, mode="human"):
        pass

    def close(self):
        pass
