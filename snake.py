from constants import DEFAULT_VISION, DIED_REWARD, EAT_REWARD, GAME_HEIGHT, GAME_WIDTH, STARVE_REWARD, USE_BINARY, WALKING_REWARD
import random
import math
import os
import copy


class SnakeObjects():
    # snake object consts
    BODY = "B"
    EMPTY = " "
    FOOD = "F"
    HEAD = "H"

    def __init__(self, type, pos_x, pos_y, dir = [0,0,0,0]):
        self.type = type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dir = dir


class SnakeDirections():
    # snake control consts
    UP = [1,0,0,0]
    DOWN = [0,1,0,0]
    LEFT = [0,0,1,0]
    RIGHT = [0,0,0,1]
    LAST = "LMS"

class SnakeControls():
    # snake control consts
    FORWARD = [1,0,0]
    LEFT = [0,1,0]
    RIGHT = [0,0,1]

class SnakeGame():
    # main snake class

    # init
    def __init__(self, size_x, size_y):
        # if too small, don't create
        if size_x < 5 or size_y < 5:
            print("Board is too small!")
            return

        # generate board and wall
        self.size_x = size_x
        self.size_y = size_y
        self.board = []

        # max distance
        self.max_distance = math.floor(math.hypot(size_y, size_x))+1

        for y in range(self.size_x):
            board_row = []
            for x in range(self.size_y):
                base_element = SnakeObjects(SnakeObjects.EMPTY, x, y)
                board_row.append(base_element)
            self.board.append(board_row)

        # snake direction
        self.last_move = random.sample([SnakeDirections.UP,SnakeDirections.LEFT,SnakeDirections.RIGHT,SnakeDirections.DOWN],1)[0]
        self.dir_x = 0
        self.dir_y = 0

        # create snake
        self.snake = []

        # randomize head
        self.snake.append(SnakeObjects(SnakeObjects.HEAD, random.randint(4, self.size_x - 5), random.randint(4, self.size_y - 5), self.last_move))

        self.board[self.snake[0].pos_y][self.snake[0].pos_x].type = SnakeObjects.HEAD

        # add 2 trailing body
        if self.last_move == SnakeDirections.UP:
            self.dir_x = 0
            self.dir_y = -1
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y + 1, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y + 2, self.last_move))

        elif self.last_move == SnakeDirections.LEFT:
            self.dir_x = -1
            self.dir_y = 0
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x + 1, self.snake[0].pos_y, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x + 2, self.snake[0].pos_y, self.last_move))
            
        elif self.last_move == SnakeDirections.RIGHT:
            self.dir_x = 1
            self.dir_y = 0
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x - 1, self.snake[0].pos_y, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x - 2, self.snake[0].pos_y, self.last_move))
        
        elif self.last_move == SnakeDirections.DOWN:
            self.dir_x = 0
            self.dir_y = 1
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y - 1, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y - 2, self.last_move))

        self.board[self.snake[1].pos_y][self.snake[1].pos_x].type = SnakeObjects.BODY
        self.board[self.snake[2].pos_y][self.snake[2].pos_x].type = SnakeObjects.BODY
        
        # randomize first food
        self.food = SnakeObjects(SnakeObjects.FOOD,0,0)
        self.regenerateFood()

        # sensor data matrix
        self.sensor = []

        # fitness
        self.fitness = 0

        # health
        self.default_health = (self.max_distance * 4) + (8 * len(self.snake))
        self.health = self.default_health

        # tile on snake head
        self.on_head = SnakeObjects.EMPTY

        # snake status
        self.alive = True

        # initial calculation
        self.getSensor(self.snake[0].pos_x,self.snake[0].pos_y)
        self.calculateFitness()

    # test if hits wall or out of bound
    def testWall(self,pos_x,pos_y):
        return pos_x < 0 or pos_x >= self.size_x or pos_y < 0 or pos_y >= self.size_y

    # refresh and return sensors
    def getSensor(self, target_x , target_y):

        # resets sensor
        self.sensor = []
        self.sensor.append([0,0,0,0,0,0,0,0]) # closest food  
        # self.sensor.append([math.inf,math.inf,math.inf,math.inf,math.inf,math.inf,math.inf,math.inf]) # closest food 
        self.sensor.append([math.inf,math.inf,math.inf,math.inf,math.inf,math.inf,math.inf,math.inf]) # closest body 
        self.sensor.append([0,0,0,0,0,0,0,0]) # closest wall 
        self.sensor.append(copy.deepcopy(self.snake[0].dir)) # head direction
        self.sensor.append(copy.deepcopy(self.snake[len(self.snake)-1].dir)) # tail direction

        head_x = target_x
        head_y = target_y

        dif_x = head_x - self.food.pos_x
        dif_y = head_y - self.food.pos_y
        # left
        if(dif_x > 0):
            # up
            if(dif_y > 0):
                self.sensor[0] = [1,0,0,0,0,0,1,1]
            # bottom
            elif(dif_y < 0):
                self.sensor[0] = [1,1,1,0,0,0,0,0]
            else:
                self.sensor[0] = [1,0,0,0,0,0,0,0]
        # right
        elif(dif_x < 0):
            # up
            if(dif_y > 0):
                self.sensor[0] = [0,0,0,0,1,1,1,0]
            # bottom
            elif(dif_y < 0):
                self.sensor[0] = [0,0,1,1,1,0,0,0]
            # middle
            else:
                self.sensor[0] = [0,0,0,0,1,0,0,0]
        # middle
        else:
            # up
            if(dif_y > 0):
                self.sensor[0] = [0,0,0,0,0,0,1,0]
            # bottom
            elif(dif_y < 0):
                self.sensor[0] = [0,0,1,0,0,0,0,0]
            # middle
            else:
                self.sensor[0] = [0,0,0,0,1,0,0,0]


        # scan surroundings
        for dir_type in range(len(DEFAULT_VISION)):
            body_found = False
            # food_found = False
            for i in range(1, self.max_distance):
                cur_x = head_x + DEFAULT_VISION[dir_type][0] * i
                cur_y = head_y + DEFAULT_VISION[dir_type][1] * i

                if self.testWall(cur_x,cur_y):
                    if self.sensor[2][dir_type] == 0:
                        self.sensor[2][dir_type] = i
                    break

                tile_type = self.board[cur_y][cur_x].type

                # if not food_found and tile_type == SnakeObjects.FOOD:
                #     food_found = True
                #     self.sensor[0][dir_type] = i
                # el
                if not body_found and tile_type == SnakeObjects.BODY:
                    body_found = True
                    self.sensor[1][dir_type] = i

            if USE_BINARY:
                # self.sensor[0][dir_type] = 1 if self.sensor[0][dir_type] != math.inf else 0
                self.sensor[1][dir_type] = 1 if self.sensor[1][dir_type] != math.inf else 0
                self.sensor[2][dir_type] = 1 if self.sensor[2][dir_type] == 1 else 0
            else:
                # self.sensor[0][dir_type] = 1.0 / self.sensor[0][dir_type]
                self.sensor[1][dir_type] = 1.0 / self.sensor[1][dir_type]
                self.sensor[2][dir_type] = 1.0 / self.sensor[2][dir_type]
                

        single_array = []
        for type in self.sensor:
            for data in type:
                single_array.append(data)

        return single_array

    # calculate snake fitness
    def calculateFitness(self):
        self.fitness = 1000 * len(self.snake) + 10 * self.health
        return self.fitness

    # refresh snake body positions
    def refreshSnakeBody(self, new_x, new_y, new_dir):

        last_x = self.snake[len(self.snake) - 1].pos_x
        last_y = self.snake[len(self.snake) - 1].pos_y

        ls_x = self.snake[0].pos_x
        ls_y = self.snake[0].pos_y
        ls_dir = self.snake[0].dir

        for i in range(1, len(self.snake)):
            # refresh body
            ln_x = self.snake[i].pos_x
            ln_y = self.snake[i].pos_y
            ln_dir = self.snake[i].dir
            self.snake[i].pos_x = ls_x
            self.snake[i].pos_y = ls_y
            self.snake[i].dir = ls_dir
            ls_x = ln_x
            ls_y = ln_y
            ls_dir = ln_dir
            # redraw body
            self.board[self.snake[i].pos_y][self.snake[i].pos_x].type = SnakeObjects.BODY

        # set last to empty
        self.board[last_y][last_x].type = SnakeObjects.EMPTY

        # update head
        self.snake[0].pos_x = new_x
        self.snake[0].pos_y = new_y
        self.snake[0].dir = new_dir

        # redraw head
        self.board[self.snake[0].pos_y][self.snake[0].pos_x].type = SnakeObjects.HEAD

    # generate new food
    def regenerateFood(self):
        # test for empty areas
        test_pos_x = random.randint(0, self.size_x - 1)
        test_pos_y = random.randint(0, self.size_y - 1)
        while True:
            if self.board[test_pos_y][test_pos_x].type == SnakeObjects.EMPTY:
                break
            test_pos_x = random.randint(0, self.size_x - 1)
            test_pos_y = random.randint(0, self.size_y - 1)

        # set empty area to food
        self.food = SnakeObjects(SnakeObjects.FOOD, test_pos_x, test_pos_y)
        self.board[self.food.pos_y][self.food.pos_x].type = SnakeObjects.FOOD

    # control snake
    # def updateSnake(self, direction=SnakeDirections.LAST):
    def updateSnake(self, direction):
        winner = False
        old_sensor = copy.deepcopy(self.getSensor(self.snake[0].pos_x,self.snake[0].pos_y))
        prev_food_dist = math.hypot(self.snake[0].pos_x-self.food.pos_x, self.snake[0].pos_y-self.food.pos_y)
        reward = WALKING_REWARD
        
        # if input f,l,r mode
        if len(direction) == 3:
            dir_wheel = [SnakeDirections.UP,SnakeDirections.RIGHT,SnakeDirections.DOWN,SnakeDirections.LEFT]
            idx = dir_wheel.index(self.last_move)
            if direction == SnakeControls.LEFT:
                idx = (idx + 4 - 1) % 4
            elif direction == SnakeControls.RIGHT:
                idx = (idx + 4 + 1) % 4

            direction = dir_wheel[idx]

        # if no input set last
        if direction == SnakeDirections.LAST:
            direction = self.last_move

        # process input
        if direction == SnakeDirections.UP and self.last_move != SnakeDirections.DOWN:
            self.dir_x = 0
            self.dir_y = -1
            self.last_move = SnakeDirections.UP
        elif direction == SnakeDirections.LEFT and self.last_move != SnakeDirections.RIGHT:
            self.dir_x = -1
            self.dir_y = 0
            self.last_move = SnakeDirections.LEFT
        elif direction == SnakeDirections.RIGHT and self.last_move != SnakeDirections.LEFT:
            self.dir_x = 1
            self.dir_y = 0
            self.last_move = SnakeDirections.RIGHT
        elif direction == SnakeDirections.DOWN and self.last_move != SnakeDirections.UP:
            self.dir_x = 0
            self.dir_y = 1
            self.last_move = SnakeDirections.DOWN
        # if direction == SnakeDirections.UP:
        #     self.dir_x = 0
        #     self.dir_y = -1
        #     self.last_move = SnakeDirections.UP
        # elif direction == SnakeDirections.LEFT:
        #     self.dir_x = -1
        #     self.dir_y = 0
        #     self.last_move = SnakeDirections.LEFT
        # elif direction == SnakeDirections.RIGHT:
        #     self.dir_x = 1
        #     self.dir_y = 0
        #     self.last_move = SnakeDirections.RIGHT
        # elif direction == SnakeDirections.DOWN:
        #     self.dir_x = 0
        #     self.dir_y = 1
        #     self.last_move = SnakeDirections.DOWN
        else:
            if self.last_move == SnakeDirections.UP:
                self.dir_x = 0
                self.dir_y = -1
                self.last_move = SnakeDirections.UP
            elif self.last_move == SnakeDirections.LEFT:
                self.dir_x = -1
                self.dir_y = 0
                self.last_move = SnakeDirections.LEFT
            elif self.last_move == SnakeDirections.RIGHT:
                self.dir_x = 1
                self.dir_y = 0
                self.last_move = SnakeDirections.RIGHT
            elif self.last_move == SnakeDirections.DOWN:
                self.dir_x = 0
                self.dir_y = 1
                self.last_move = SnakeDirections.DOWN

        # calculate movement
        target_x = self.snake[0].pos_x + self.dir_x
        target_y = self.snake[0].pos_y + self.dir_y
        eat_food = False

        # check on target, if target is wall, snake dies
        if self.testWall(target_x,target_y):
            self.alive = False
            reward = DIED_REWARD
        else:
            target_type = self.board[target_y][target_x].type
            self.on_head = target_type

            # if target is body, snake dies, if food eaten save last body pos for extending length
            if target_type == SnakeObjects.BODY and not (self.snake[len(self.snake)-1].pos_x == target_x and self.snake[len(self.snake)-1].pos_y == target_y):
                self.alive = False
                reward = DIED_REWARD
            elif target_type == SnakeObjects.FOOD:
                eat_food = True
                last_pos_x = self.snake[len(self.snake) - 1].pos_x
                last_pos_y = self.snake[len(self.snake) - 1].pos_y
                last_dir = self.snake[len(self.snake) - 1].dir
                reward = EAT_REWARD

        # if target not wall aka dead
        if not self.testWall(target_x,target_y):
            # refresh all snake's body
            self.refreshSnakeBody(target_x, target_y, self.last_move)

            # if foot eat increase body length and create more food and reset health, else decrease health by 1
            if eat_food:
                self.snake.append(SnakeObjects(SnakeObjects.BODY, last_pos_x, last_pos_y, last_dir))
                self.board[self.snake[len(self.snake) - 1].pos_y][self.snake[len(self.snake) - 1].pos_x].type = SnakeObjects.BODY
                if len(self.snake) == self.size_x * self.size_y:
                    # max size, winner!
                    winner = True
                    self.alive = False
                else:
                    self.regenerateFood()
                self.default_health = (self.max_distance * 4) + (8 * len(self.snake))
                self.health = self.default_health
            else:
                # recalculate walking reward
                aft_food_dist = math.hypot(target_x-self.food.pos_x, target_y-self.food.pos_y)
                # if walking away from food (dist increased)
                if aft_food_dist >= prev_food_dist:
                    # negative
                    reward = -WALKING_REWARD
                else:
                    reward = WALKING_REWARD
                self.health = self.health - 1

            # if runs out of health snake dies
            if self.health <= 0:
                reward = STARVE_REWARD
                self.alive = False

        # get new snake sensor and recalculate fitness
        new_sensor = self.getSensor(target_x,target_y)
        fitness = self.calculateFitness()

        return copy.deepcopy(self.alive), copy.deepcopy(old_sensor), copy.deepcopy(new_sensor), copy.deepcopy(fitness), copy.deepcopy(reward) , copy.deepcopy(winner)

    # get whole snake state
    def getCurrentState(self):
        snake = copy.deepcopy(self.snake)
        board = copy.deepcopy(self.board)
        dir_x = copy.deepcopy(self.dir_x)
        dir_y = copy.deepcopy(self.dir_y)
        last_move = copy.deepcopy(self.last_move)
        sensor = copy.deepcopy(self.sensor)
        default_health = copy.deepcopy(self.default_health)
        health = copy.deepcopy(self.health)
        alive = copy.deepcopy(self.alive)
        on_head = copy.deepcopy(self.on_head)

        return snake, board, dir_x, dir_y, last_move, sensor, default_health, health, alive, on_head

    # set whole snake state
    def setCurrentState(self, snake, board, dir_x, dir_y, last_move, sensor, default_health, health, alive, on_head):
        self.snake = snake
        self.board = board
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.last_move = last_move
        self.sensor = sensor
        self.default_health = default_health
        self.health = health
        self.alive = alive
        self.on_head = on_head

    # test input for snake WITHOUT UPDATING SNAKE
    def testSnake(self, direction=SnakeDirections.LAST):
        old_state = self.getCurrentState()
        data_return = self.updateSnake(direction)
        self.setCurrentState(old_state[0], old_state[1], old_state[2], old_state[3], old_state[4], old_state[5], old_state[6], old_state[7], old_state[8], old_state[9])
        return data_return

    # draws board to console
    def drawConsole(self):
        for _ in range(self.size_x+2):
            print("#", end=" ")
        print()

        for board_row in self.board:
            print("#", end=" ")
            for tile in board_row:
                print(tile.type, end=" ")
            print("#", end=" ")
            print()

        for _ in range(self.size_x+2):
            print("#", end=" ")
        print()

        print("Food", self.sensor[0])
        print("Body", self.sensor[1])
        print("Wall", self.sensor[2])
        print("Head Direction", self.sensor[3])
        print("Tail Direction", self.sensor[4])
        print("Fitness: ", self.fitness)
        print("Health: ", self.health)

    # reset the snake
    def resetSnake(self):
        # generate board and wall
        self.board = []

        for y in range(self.size_x):
            board_row = []
            for x in range(self.size_y):
                base_element = SnakeObjects(SnakeObjects.EMPTY, x, y)
                board_row.append(base_element)
            self.board.append(board_row)

        # snake direction
        self.last_move = random.sample([SnakeDirections.UP,SnakeDirections.LEFT,SnakeDirections.RIGHT,SnakeDirections.DOWN],1)[0]
        self.dir_x = 0
        self.dir_y = 0

        # create snake
        self.snake = []

        # randomize head
        self.snake.append(SnakeObjects(SnakeObjects.HEAD, random.randint(4, self.size_x - 5), random.randint(4, self.size_y - 5), self.last_move))

        self.board[self.snake[0].pos_y][self.snake[0].pos_x].type = SnakeObjects.HEAD

        # add 2 trailing body
        if self.last_move == SnakeDirections.UP:
            self.dir_x = 0
            self.dir_y = -1
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y + 1, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y + 2, self.last_move))

        elif self.last_move == SnakeDirections.LEFT:
            self.dir_x = -1
            self.dir_y = 0
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x + 1, self.snake[0].pos_y, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x + 2, self.snake[0].pos_y, self.last_move))
            
        elif self.last_move == SnakeDirections.RIGHT:
            self.dir_x = 1
            self.dir_y = 0
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x - 1, self.snake[0].pos_y, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x - 2, self.snake[0].pos_y, self.last_move))
        
        elif self.last_move == SnakeDirections.DOWN:
            self.dir_x = 0
            self.dir_y = 1
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y - 1, self.last_move))
            self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y - 2, self.last_move))

        self.board[self.snake[1].pos_y][self.snake[1].pos_x].type = SnakeObjects.BODY
        self.board[self.snake[2].pos_y][self.snake[2].pos_x].type = SnakeObjects.BODY
       
        # randomize first food
        self.regenerateFood()

        # sensor data matrix -> [body, food, wall]
        self.sensor = []
        self.sensor.append([0, 0, 0])  # LB
        self.sensor.append([0, 0, 0])  # LM
        self.sensor.append([0, 0, 0])  # LT
        self.sensor.append([0, 0, 0])  # MT
        self.sensor.append([0, 0, 0])  # RT
        self.sensor.append([0, 0, 0])  # RM
        self.sensor.append([0, 0, 0])  # RB
        self.sensor.append([0, 0, 0])  # MB

        # fitness
        self.fitness = 0

        # health
        self.default_health = (self.max_distance * 4) + (8 * len(self.snake))
        self.health = self.default_health

        # snake status
        self.alive = True

        # initial calculation
        self.getSensor(self.snake[0].pos_x,self.snake[0].pos_y)
        self.calculateFitness()


# snake_instance = SnakeGame(GAME_WIDTH,GAME_HEIGHT)

# snake_instance.drawConsole()

# while snake_instance.alive:
#     inp = input()
#     if inp.find("a") != -1:
#         inp = SnakeDirections.LEFT
#     elif inp.find("s") != -1:
#         inp = SnakeDirections.DOWN
#     elif inp.find("d") != -1:
#         inp = SnakeDirections.RIGHT
#     elif inp.find("w") != -1:
#         inp = SnakeDirections.UP
#     else:
#         inp = SnakeDirections.LAST
#
#     alive, old_sensor, new_sensor, fitness, reward = snake_instance.updateSnake(inp)
#     # os.system("cls")
#     snake_instance.drawConsole()
#     print("snek: ")
#     for body in snake_instance.snake:
#         print(body.dir)

# print(snake_instance.fitness)
