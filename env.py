from gym import Env
from nicomotion.Motion import Motion
from gym.spaces import Box
import numpy as np
from pypot.pyrep import PyRepIO, PyRep

available_joints = [
    'head_z', 'head_y', 'r_hip_x', 'r_hip_z', 'r_hip_y', 'r_knee_y', 'r_ankle_y', 'r_ankle_x', 'l_hip_x', 'l_hip_z',
    'l_hip_y', 'l_knee_y', 'l_ankle_y', 'l_ankle_x', 'r_shoulder_y', 'r_shoulder_z', 'r_arm_x', 'r_elbow_y',
    'l_shoulder_y', 'l_shoulder_z', 'l_arm_x', 'l_elbow_y', 'l_wrist_z', 'l_wrist_x', 'l_indexfingers_x', 'l_thumb_x',
    'r_wrist_z', 'r_wrist_x', 'r_indexfingers_x', 'r_thumb_x'
]

right_arm = ['r_shoulder_y', 'r_shoulder_z', 'r_arm_x', 'r_elbow_y', 'r_wrist_z', 'r_wrist_x', 'r_indexfingers_x',
             'r_thumb_x']
left_arm = ['l_shoulder_y', 'l_shoulder_z', 'l_arm_x', 'l_elbow_y', 'l_wrist_z', 'l_wrist_x', 'l_indexfingers_x',
            'l_thumb_x']

POS_MIN = [-3., -3., -3.]
POS_MAX = [3.0, 3.0, 3.0]

TARGET_POS_MIN = [1, -0.5, 0.5]
TARGET_POS_MAX = [3, 0.5, 1.5]

FRACTION_MAX_SPEED = 1


class NicoEnv(Env):
    def __init__(self, config_file, scene_file, episode_length=50, joints=None, headless=False):
        super(NicoEnv, self).__init__()
        self.io = PyRepIO(scene=scene_file, start=True, blocking=False, headless=headless)
        self._scene = scene_file
        self._config = Motion.pyrepConfig()
        self._config['shared_vrep_io'] = self.io
        self._config['vrep_scene'] = self._scene
        self._config['use_pyrep'] = True
        self._config['headless'] = True

        self._robot = Motion(motorConfig=config_file, vrep=True, vrepConfig=self._config)
        self.io.pyrep.step()

        self._joints = joints if joints is not None else self._robot.getJointNames()
        self.handle = self.io.get_object('l_thumb_x')

        self._n = len(self._joints)
        self.threshold = 1

        self._low = np.array([-180 for _ in self._joints])
        self._high = np.array([180 for _ in self._joints])

        self.observation_space = Box(low=np.array(POS_MIN + TARGET_POS_MIN), high=np.array(POS_MAX + TARGET_POS_MAX))
        self.action_space = Box(low=self._low, high=self._high)
        self.target = self.observation_space.sample()[self._n-1:]

        self.episode_lenth = episode_length
        self.steps = 0

    def _execute_action(self, action):
        for angle, joint in zip(action, self._joints):
            self._robot.setAngle(jointName=joint, angle=angle, fractionMaxSpeed=FRACTION_MAX_SPEED)
        for i in range(2):
            self.io.pyrep.step()

    def _get_state(self):
        return np.concatenate([self.handle.get_position(), self.target])

    def step(self, action):
        self._execute_action(action)
        observation = self._get_state()
        a = self.handle.get_position()
        diff = np.subtract(a, self.target)
        distance = np.matmul(diff, diff.transpose())
        close = distance <= self.threshold
        done = close or self.steps >= self.episode_lenth
        reward = -distance
        if close:
            reward += 3
        if done and not close:
            reward -= 3
        print(self.steps, reward, self._get_state())
        self.steps += 1
        return observation, reward, done, {}

    def reset(self):
        observation = self.observation_space.sample()
        self.handle.set_position(observation[0:3])
        self.target = observation[3:]
        self.io.pyrep.step()
        self.steps = 0
        return self._get_state()

    def render(self, mode='human'):
        pass

    def close(self):
        self._robot.stopSimulation()
        self._robot.cleanup()
