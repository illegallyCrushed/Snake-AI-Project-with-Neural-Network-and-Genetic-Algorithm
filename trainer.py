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

        alive_batch, old_sensor_batch, new_sensor_batch, action_batch, reward_batch = zip(*memory)

        # for step in memory:
        #     alive, old_sensor, new_sensor, action, reward = step
        #     alive_batch.append(alive)
        #     old_sensor_batch.append(old_sensor)
        #     new_sensor_batch.append(new_sensor)
        #     action_batch.append(action)
        #     reward_batch.append(reward)

        # ts_alive = tensorflow.convert_to_tensor(alive_batch)
        # ts_old_sensor = tensorflow.convert_to_tensor(old_sensor_batch)
        # ts_new_sensor = tensorflow.convert_to_tensor(new_sensor_batch)
        # ts_action = tensorflow.convert_to_tensor(action_batch)
        # ts_reward = tensorflow.convert_to_tensor(reward_batch)

        ts_alive = alive_batch
        ts_old_sensor = tensorflow.convert_to_tensor(old_sensor_batch)
        ts_new_sensor = tensorflow.convert_to_tensor(new_sensor_batch)
        ts_action = tensorflow.convert_to_tensor(action_batch)
        ts_reward = reward_batch
        
        # target = copy.deepcopy(self.brain.neural.predict(ts_old_sensor))
        # new_target = copy.deepcopy(self.brain.neural.predict(ts_new_sensor))

        # for i in range(len(alive_batch)):
        #     max_action = tensorflow.argmax(ts_action[i]).numpy()
        #     if not ts_alive[i].numpy():
        #         target[i][max_action] = ts_reward[i].numpy()
        #     else:
        #         Q_future = max(new_target[i]) - target[i][max_action] 
        #         target[i][max_action] = ts_reward[i].numpy() + Q_future * self.gamma

        result = copy.deepcopy(self.brain.neural.predict(ts_old_sensor))
        target = copy.deepcopy(self.brain.neural.predict(ts_new_sensor))
        ts_target = tensorflow.convert_to_tensor(target)

        for i in range(len(alive_batch)):
            max_action = tensorflow.argmax(ts_action[i]).numpy()
            result[i][max_action] = ts_reward[i] + self.gamma * tensorflow.argmax(ts_target[i]).numpy() * int(ts_alive[i])

        ts_result = tensorflow.convert_to_tensor(result)
        # self.brain.neural.fit(x=ts_old_sensor, y=ts_target, verbose=False, batch_size = BATCH_SIZE, epochs = MAX_EPOCHS,callbacks=[tensorboard_callback])
        self.brain.neural.fit(ts_old_sensor, ts_result, verbose=False, epochs = MAX_EPOCHS)

        


