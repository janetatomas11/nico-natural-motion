from gym import Env
from nicomotion.Motion import Motion
from gym.spaces import Dict, Box
import numpy as np
from pyrep.objects import Shape
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
POS_MIN, POS_MAX = [-3., -3., -3.], [3.0, 3.0, 3.0]
FRACTION_MAX_SPEED = 0.05


class NicoEnv(Env):
    def __init__(self, config_file, scene_file, joints=None):
        super(NicoEnv, self).__init__()
        self.io = PyRepIO(scene=scene_file, start=True, blocking=False)
        self._scene = scene_file
        self._config = Motion.pyrepConfig()
        self._config['shared_vrep_io'] = self.io
        self._config['vrep_scene'] = self._scene
        self._config['use_pyrep'] = True
        self._config['headless'] = True

        self._robot = Motion(motorConfig=config_file, vrep=True, vrepConfig=self._config)
        self._joints = joints if joints is not None else self._robot.getJointNames()
        self.handle = self.io.get_object('r_thumb_x')
        self.target = self.io.get_object('target')
        self._n = len(self._joints)
        self.initial_position = self._get_state()[0:self._n]
        self.threshold = 0.2

        self._low = np.array([angle if angle <= 0 else angle - 360 for angle in
                              [self._robot.getAngleLowerLimit(joint) for joint in self._joints]])
        self._high = np.array([angle if angle >= 0 else 360 + angle for angle in
                               [self._robot.getAngleUpperLimit(joint) for joint in self._joints]])

        self.observation_space = Box(low=np.array(2 * POS_MIN), high=np.array(2 * POS_MAX))
        self.action_space = Box(low=self._low, high=self._high)

    def _execute_action(self, action):
        for angle, joint in zip(action, self._joints):
            self._robot.setAngle(jointName=joint, angle=angle, fractionMaxSpeed=FRACTION_MAX_SPEED)
        for i in range(self._n):
            self.io.pyrep.step()

    def _get_state(self):
        return np.concatenate([self.handle.get_position(), self.target.get_position()])

    def step(self, action):
        self._execute_action(action)
        observation = self._get_state()
        distance = np.linalg.norm(self.handle.get_position(self.target))
        reward = -distance
        done = distance <= self.threshold
        return observation, reward, done, {}

    def reset(self):
        observation = self.observation_space.sample()
        self.handle.set_position(observation[0:self._n])
        self.io.pyrep.step()
        # self.target.set_position(observation[1])
        return self._get_state()

    def render(self, mode='human'):
        pass

    def close(self):
        self._robot.stopSimulation()
        self._robot.cleanup()
