from collections import deque
import snake
import random
import brain
import trainer
import tensorflow
import copy
import os
import json
from constants import *


class SnakeAgent:
    # agent class for brain controlling the snake

    # init
    def __init__(self):
        self.num_game = 0
        self.highest_length = 0
        self.current_length = 0
        self.highest_fitness = 0
        self.current_fitness = 0

        self.epsilon = 0

        self.snake = snake.SnakeGame(GAME_WIDTH, GAME_HEIGHT)
        self.brain = brain.SnakeBrain(LEARNING_RATE)
        self.trainer = trainer.SnakeTrainer(self.brain, LEARNING_RATE, GAMMA_VAR)

        # each brain has memory
        self.memory = deque(maxlen=MAX_MEMORY)

    # compare function for genetic algorithm
    def __lt__(self, other):
        return (self.highest_fitness < other.highest_fitness)

    # add function for sum genetic algorithm
    def __add__(self, other):
        return (self.highest_fitness + other)

    def __radd__(self, other):
        if other == 0:
            return self.highest_fitness
        else:
            return self.__add__(other)

    # generate move from brain for given sensor
    def think(self, state):
        # epsilon, tradeoff exploration / exploitation
        final_action = [0] * OUTPUT_LAYER
        if random.random() <= self.epsilon:
            action = random.randint(0, 2)
            final_action[action] = 1
        else:
            ts_state = tensorflow.convert_to_tensor([state])
            result = self.brain.neural.predict(ts_state)
            action = tensorflow.argmax(result[0]).numpy()
            final_action[action] = 1

        return final_action

    # memorize moves
    def memorize(self, alive, old_sensor, new_sensor, action, reward):
        self.memory.append((alive, old_sensor, new_sensor, action, reward))

    # train last step
    def trainLast(self):
        # print("last")
        memory_sample = []
        memory_sample.append(copy.deepcopy(self.memory[len(self.memory)-1]))
        self.trainer.train(memory_sample)

    # train batch of steps
    def trainBatch(self):
        # print("batch")
        memory_sample = []
        if len(self.memory) > MAX_BATCH:
            memory_sample = copy.deepcopy(random.sample(self.memory, MAX_BATCH))
        else:
            return
        self.trainer.train(memory_sample)
        if self.epsilon > EPSILON_MIN:
            self.epsilon *= EPSILON_DECAY

    def saveAgent(self , addon = ""):
        filehandle = open("./train_data/agentdata_{}_{}.json".format(self.num_game,addon), 'w')
        jsondata = {
            "game_number": self.num_game,
            "parent_weight": self.brain.encodeWeight(),
            "parent_fitness": self.current_fitness,
        }
        filehandle.write(json.dumps(jsondata, indent=2))
        filehandle.close()

    def updateAgent(self,order):
        while self.num_game < GAME_COUNT_MAX:
            # reset game
            # yeet = input()
            self.snake.resetSnake()
            # until snake dies
            while self.snake.alive:
                # save old state
                old_sensor = copy.deepcopy(self.snake.getSensor(self.snake.snake[0].pos_x,self.snake.snake[0].pos_y))
                # get action
                calculated_action = self.think(old_sensor)
                # print("Move: {}".format(calculated_action))
                # update snake & get new state
                alive, _, new_sensor, fitness, reward, winner = copy.deepcopy(self.snake.updateSnake(calculated_action))
                # memorize
                self.memorize(alive, old_sensor, new_sensor, calculated_action, reward)
                # train_batches
                self.trainBatch()
                # set current fitness, for logging
                self.current_fitness = fitness
                self.current_length = len(self.snake.snake)
                # os.system("cls")
                # self.snake.drawConsole()
                # print("Reward {}".format(reward))
                print("Snake {} = {}/{} | Current Fitness = {} | Current Length = {}".format(order, self.num_game, GAME_COUNT_MAX, self.current_fitness, self.current_length))
                if not alive:
                    # if snake dies
                    # increase number of game
                    self.num_game += 1
                    # set highest fitness, actually avg fitness
                    self.highest_fitness = (self.highest_fitness * (self.num_game-1) + fitness) / self.num_game
                    # if fitness > self.highest_fitness:
                    #     self.highest_fitness = fitness
                    # set highest length, actually avg length
                    if winner:
                        print("Snake {} is Winning!".format(order))
                        self.saveAgent("perfect")
                    elif self.current_length > self.highest_length and self.current_length > self.snake.size_x:
                        self.saveAgent()
                    self.highest_length = (self.highest_length * (self.num_game-1) + self.current_length) / self.num_game
                    # if self.current_length > self.highest_length:
                    #     self.highest_length = self.current_length
            
        # num of game == max game,clear memory and return true as done
        self.memory.clear()
        return True, self.num_game

    def agentDone(self):
        if self.num_game < GAME_COUNT_MAX:
            return False
        else:
            return True
