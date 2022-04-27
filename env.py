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

TARGET_POS_MIN = [0.3, -0.5, 0.5]
TARGET_POS_MAX = [1, 0.5, 1.5]

FRACTION_MAX_SPEED = 1


class NicoEnv(Env):
    def __init__(self, config_file, scene_file, episode_length=10, joints=None, headless=False):
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
        self.threshold = 2.7

        self._low = np.array([-180 for _ in self._joints])
        self._high = np.array([180 for _ in self._joints])

        self.observation_space = Box(low=np.array(POS_MIN + TARGET_POS_MIN), high=np.array(POS_MAX + TARGET_POS_MAX))
        self.action_space = Box(low=self._low, high=self._high)
        self.target = self.observation_space.sample()[self._n-1:]

        self.episode_lenth = episode_length
        self.steps = 0

        self.invalid_movement_threshold = 0.2
        self._initial_legs_position = self._legs_position()

    def _execute_action(self, action):
        for angle, joint in zip(action, self._joints):
            self._robot.setAngle(jointName=joint, angle=angle, fractionMaxSpeed=FRACTION_MAX_SPEED)
        for i in range(2):
            self.io.pyrep.step()

    def _get_state(self):
        return np.concatenate([self.handle.get_position(), self.target])

    def _check_fall(self):
        return self.io.get_object_position('head_z')[2] <= self.invalid_movement_threshold

    def _legs_position(self):
        return np.concatenate([self.io.get_object_position('r_ankle_y'),
                               self.io.get_object_position('l_ankle_y'),
                               self.io.get_object_position('r_knee_y'),
                               self.io.get_object_position('l_knee_y')])

    def _check_invalid_move(self):
        current = self._legs_position()
        diff = self._initial_legs_position - current
        return np.linalg.norm(diff) >= self.invalid_movement_threshold

    def _distance(self):
        current = self.handle.get_position()
        goal = self.target
        diff = goal - current
        return np.linalg.norm(diff)

    def step(self, action):
        self._execute_action(action)

        info = {}
        current = self.handle.get_position()
        distance = np.linalg.norm(self.target - current)

        # handle fall of the robot
        if self._check_fall():
            observation, reward, done = self._get_state(), -1000, True
        # handle invalid movement of the legs
        elif self._check_invalid_move():
            observation = self._get_state()
            reward = -100
            done = True
        elif self.steps >= self.episode_lenth:
            observation = self._get_state()
            reward = -100
            done = True
        elif distance <= self.threshold:
            observation = self._get_state()
            reward = 100
            done = True
        else:
            self.steps += 1
            self.handle.get_position()
            observation = self._get_state()
            reward = -distance**2
            done = False

        print(reward, distance, self._get_state())

        return observation, reward, done, info

    def reset(self):
        self._robot.resetSimulation()
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
