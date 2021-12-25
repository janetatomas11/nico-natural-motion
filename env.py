
from gym import Env
from nicomotion.Motion import Motion
from nicotouch import optoforcesensors
from gym.spaces import Dict, Box
import numpy as np

available_joints = [
    'head_z', 'head_y', 'r_hip_x', 'r_hip_z', 'r_hip_y', 'r_knee_y', 'r_ankle_y', 'r_ankle_x', 'l_hip_x', 'l_hip_z',
    'l_hip_y', 'l_knee_y', 'l_ankle_y', 'l_ankle_x', 'r_shoulder_y', 'r_shoulder_z', 'r_arm_x', 'r_elbow_y',
    'l_shoulder_y', 'l_shoulder_z', 'l_arm_x', 'l_elbow_y', 'l_wrist_z', 'l_wrist_x', 'l_indexfingers_x', 'l_thumb_x',
    'r_wrist_z', 'r_wrist_x', 'r_indexfingers_x', 'r_thumb_x'
]

right_arm = ['r_shoulder_y', 'r_shoulder_z', 'r_arm_x', 'r_elbow_y', 'r_wrist_z', 'r_wrist_x', 'r_indexfingers_x', 'r_thumb_x']
left_arm = ['l_shoulder_y', 'l_shoulder_z', 'l_arm_x', 'l_elbow_y', 'l_wrist_z', 'l_wrist_x', 'l_indexfingers_x', 'l_thumb_x']

FRACTION_MAX_SPEED = 0.02


class NicoEnv(Env):
    def __init__(self, config_file, scene_file, goal, joints=None):
        super(NicoEnv, self).__init__()
        self._scene = scene_file
        self._config = Motion.pyrepConfig()
        self._config['vrep_scene'] = self._scene
        self._config['headless'] = True
        self._robot = Motion(motorConfig=config_file, vrep=True, vrepConfig=self._config)
        self._joints = joints if joints is not None else self._robot.getJointNames()
        self._initial_state = self._get_state()
        self._robot.startSimulation()
        self.observation_space = Dict({
            joint: Box(low=self._robot.getAngleLowerLimit(joint),
                       high=self._robot.getAngleUpperLimit(joint),
                       shape=(1,)) for joint in self._joints
        })
        self.action_space = Dict({
            joint: Box(low=self._robot.getAngleLowerLimit(joint),
                       high=self._robot.getAngleUpperLimit(joint),
                       shape=(1,)) for joint in self._joints
        })
        self._goal_state = self.observation_space.sample()


    def _get_state(self):
        state = {}
        for joint in self._joints:
            state[joint] = self._robot.getAngle(joint)
        return state

    def _set_state(self, state):
        for joint in state.keys():
            self._robot.setAngle(joint, state[joint], 0.02)
        i = 0
        while True:
            self._robot.nextSimulationStep()
            i += 1
            if i % 10 == 0:
                if self._check_state(state):
                    break

    def _check_state(self, state):
        current_state = self._get_state()
        return current_state == state

    def compute_reward(self):
        current = self._get_state()
        return -np.linalg.norm(np.array([current[joint] for joint in self._joints]) -
                              np.array([self._goal_state[joint] for joint in self._joints]))

    def step(self, action):
        observation = self._set_state(action)
        reward = self.compute_reward()
        done = abs(reward) < 0.1
        return observation, reward, done, {}

    def reset(self):
        self._robot.toSafePosition()
        return self._initial_state

    def render(self, mode="human"):
        pass

    def close(self):
        self._robot.stopSimulation()
        self._robot.cleanup()


