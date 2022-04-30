
from pyrep import PyRep
from pyrep.robots.mobiles.turtlebot import TurtleBot
from gym.spaces import Box
from gym import Env
import numpy as np
from pyrep.objects.shape import Shape

position_min = [-2, -2]
position_max = [2, 2]


class TurtleEnv(Env):
    def __init__(self, scene):
        self.scene = scene

        self.pr = PyRep()
        self.pr.launch(scene_file=self.scene, headless=False)
        self.pr.start()

        self.robot = TurtleBot()

        self.step_size = 0.25
        self.action_space = Box(low=np.array([-self.step_size, -self.step_size]), high=np.array([self.step_size, self.step_size]))
        self.observation_space = Box(low=np.array(position_min * 2), high=np.array(position_max * 2))

        self.target = Shape('target')

        self.punishment = -100
        self.reward = 20

        self.threshold = 1

        self.episode_length = 50
        self.steps = 0

    def _get_position(self):
        return np.array(self.robot.get_position()[:2])

    def _get_target_position(self):
        return np.array(self.target.get_position()[:2])

    def _get_state(self):
        return np.concatenate([self._get_position(), self._get_target_position()])

    def _get_distance(self, pos):
        return np.linalg.norm(pos - self._get_target_position())

    def _set_position(self, pos):
        self.robot.set_position(list(pos))
        self.pr.step()

    def step(self, action):
        current = self._get_position()
        new = current + action

        old_distance = self._get_distance(current)
        new_distance = self._get_distance(new)
        diff = old_distance - new_distance
        observation = self._get_state()
        done = False
        info = {}

        if np.isnan(new[0]) or np.isnan(current[1]):
            return observation, -old_distance, done, info

        if self.steps >= self.episode_length:
            done = True
            reward = -self.reward
        elif not self.observation_space.contains(np.concatenate([new, self._get_target_position()])):
            reward = self.punishment
        elif old_distance >= self.threshold:
            self._set_position(new)
            observation = self._get_state()
            reward = diff * np.sign(diff)
        else:
            observation = self._get_state()
            reward = self.reward
            done = True

        self.steps += 1
        print(observation, new_distance)
        return observation, reward, done, info

    def reset(self):
        observation = self.observation_space.sample()
        self._set_position(observation[:2])
        self.target.set_position(observation[2:])
        self.steps = 0
        return self._get_state()

    def render(self, mode="human"):
        pass

    def close(self):
        pass

