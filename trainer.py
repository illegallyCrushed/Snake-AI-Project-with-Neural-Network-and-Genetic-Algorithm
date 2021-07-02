from constants import *
import copy
import tensorflow

tensorboard_callback = tensorflow.keras.callbacks.TensorBoard(log_dir="./log_data", histogram_freq=1)

class SnakeTrainer:
    # trainer class for snake brain using reinforced learning (QNet)

    # init
    def __init__(self, brain, lr, gamma):
        # learning rate
        self.lr = lr
        # gamma aka discount rate
        self.gamma = gamma
        # brain to be trained
        self.brain = brain

    def train(self, memory):
        alive_batch = []
        old_sensor_batch = []
        new_sensor_batch = []
        action_batch = []
        reward_batch = []

        #splits data into their categories
        alive_batch, old_sensor_batch, new_sensor_batch, action_batch, reward_batch = zip(*memory)

        # convert data to tensors, speeds up process
        ts_alive = alive_batch
        ts_old_sensor = tensorflow.convert_to_tensor(old_sensor_batch)
        ts_new_sensor = tensorflow.convert_to_tensor(new_sensor_batch)
        ts_action = tensorflow.convert_to_tensor(action_batch)
        ts_reward = reward_batch
        
        # calculate result and next step's result
        result = copy.deepcopy(self.brain.neural.predict(ts_old_sensor))
        target = copy.deepcopy(self.brain.neural.predict(ts_new_sensor))
        ts_target = tensorflow.convert_to_tensor(target)

        # calculate next best possible step with bellman's q equation
        for i in range(len(alive_batch)):
            max_action = tensorflow.argmax(ts_action[i]).numpy()
            result[i][max_action] = ts_reward[i] + self.gamma * tensorflow.argmax(ts_target[i]).numpy() * int(ts_alive[i])

        ts_result = tensorflow.convert_to_tensor(result)
        # backpropagate to the neural
        self.brain.neural.fit(ts_old_sensor, ts_result, verbose=False, epochs = MAX_EPOCHS)

        


