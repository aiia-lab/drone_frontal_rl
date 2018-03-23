import cv2
import numpy as np
import gym
from gym import spaces
import pickle
from os.path import join


class CameraControlEnv(gym.Env):

    def __init__(self, dataset_pickle_path='data/dataset.pickle', testing=False, interactive=False):
        """
        Initializes the camera control environment
        :param dataset_pickle_path: the dataset pickle
        :param testing: True -> evaluation on test set, False -> evaluation on train set
        :param interactive: if set to True, then waits for user input before proceeding to the next action
        """

        self.metadata = {'render.modes': ['human'], }

        # Load data
        with open(dataset_pickle_path, 'rb') as f:
            self.persons = pickle.load(f)

        # List of possible tilts and pans
        self.tilts = [-60, -30, -15, 0, +15, +30, +60]
        self.pans = [-90, -75, -60, -45, -30, -15, 0, +15, +30, +45, +60, +75, +90]

        self.testing = testing

        # Create state
        self.current_tilt = 0
        self.current_pan = 0

        if self.testing:
            self.current_person = np.random.randint(20, 30)
        else:
            self.current_person = np.random.randint(0, 20)

        # Keep some statistics
        self.error_memory = []

        # Mean RGB vector for normalizing input frames
        self.mean_vector = np.asarray([109, 114, 131])

        # Create environment state
        self.observation = np.zeros((64, 64, 3,))
        self.render_observation = np.zeros((256, 256, 3,))
        self.action_space = spaces.Discrete(5)  # no action, left, right, up, down
        self.observation_space = spaces.Box(-127 * np.ones(self.observation.shape),
                                            127 * np.ones(self.observation.shape), dtype='float32')

        # Statistics for testing
        self.epoch_counter = -1
        self.iteration_counter = 0
        self.init_pan_error = []
        self.init_tilt_error = []
        self.final_pan_error = []
        self.final_tilt_error = []

        self.current_state_text = str(self.tilts[self.current_tilt]) + '/' + str(self.pans[self.current_pan])
        self.action_text = 'None'
        self.interactive = interactive


    def reset(self):
        
        # Select a random person
        if self.testing:
            self.current_person = np.random.randint(20, 30)
        else:
            self.current_person = np.random.randint(0, 20)

        # Reset statistics
        self.error_memory = []

        # Select a random tilt and pan to init the enviroment
        self.current_tilt = np.random.randint(0, len(self.tilts))
        self.current_pan = np.random.randint(0, len(self.pans))

        # Retrieve observation
        tilt, pan = self.tilts[self.current_tilt], self.pans[self.current_pan]

        self.observation, self.render_observation = self.persons[self.current_person][(tilt, pan)]
        self.observation = self.observation - self.mean_vector

        # Update statistics
        self.epoch_counter += 1
        self.iteration_counter = 0

        # Keep the initial and the final errors for each episode
        self.init_pan_error.append(pan)
        self.init_tilt_error.append(tilt)
        self.final_pan_error.append(pan)
        self.final_tilt_error.append(tilt)

        # Reset text
        self.current_state_text = str(self.tilts[self.current_tilt]) + '/' + str(self.pans[self.current_pan])
        self.action_text = 'None'

        return self.observation

    def seed(self, seed):
        np.random.seed(seed)

    def step(self, action):

        # Perform an action
        if action == 0:
            pass
        elif action == 1:  # down
            self.current_tilt = max(0, self.current_tilt - 1)
        elif action == 2:  # up
            self.current_tilt = min(len(self.tilts) - 1, self.current_tilt + 1)
        elif action == 3:  # right
            self.current_pan = max(0, self.current_pan - 1)
        elif action == 4:  # left
            self.current_pan = min(len(self.pans) - 1, self.current_pan + 1)
        else:
            assert False

        # Retrieve observation
        tilt, pan = self.tilts[self.current_tilt], self.pans[self.current_pan]

        # Prepare the text for the observation
        if action == 0:
            action_text = 'Stay'
        elif action == 1:
            action_text = 'Up'
        elif action == 2:
            action_text = 'Down'
        elif action == 3:
            action_text = 'Left'
        elif action == 4:
            action_text = 'Right'

        self.current_state_text = str(self.tilts[self.current_tilt]) + '/' + str(self.pans[self.current_pan])
        self.action_text = action_text

        # Update statistics for the current episode
        self.final_pan_error[-1] = pan
        self.final_tilt_error[-1] = tilt

        self.observation, self.render_observation = self.persons[self.current_person][(tilt, pan)]
        self.observation = self.observation - self.mean_vector

        # Calculate error
        error = (float(tilt) / np.max(np.abs(self.tilts))) ** 2 + (float(pan) / np.max(np.abs(self.pans))) ** 2
        self.error_memory.append(error)

        # Calculate reward
        reward = (2 - error) / 2.0
        if reward < 0.95:
            reward = 0
        else:
            reward = (reward - 0.95) / 0.05

        # Add reward/punishment for correct/wrong movements
        if len(self.error_memory) > 2 and self.error_memory[-2] > self.error_memory[-1]:
            reward += 0.1
        elif len(self.error_memory) > 2 and self.error_memory[-2] < self.error_memory[-1]:
            reward += -0.15

        self.iteration_counter += 1
        done = False
        return self.observation, reward, done, {}

    def render(self, mode='human', close=False):

        img = self.render_observation.copy()
        cv2.putText(img, "Tilt/Pan: " + self.current_state_text, (10, 25), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (255,0,0), 1)
        cv2.putText(img, "Sel. Action: " + self.action_text, (10, 50), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (255,0,0), 1)

        cv2.imshow('View', img)
        cv2.imshow('CNN Input', np.uint8(self.observation + self.mean_vector))

        if self.interactive:
            print("Press any key to proceed")
            cv2.waitKey(0)
        else:
            cv2.waitKey(1)

    def __str__(self):
        return 'CameraControlEnviroment'


