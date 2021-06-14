import random
import math
import os

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

class SnakeObjects():
    # snake object consts
    BODY = "B"
    EMPTY = " "
    FOOD = "F"
    HEAD = "H"
    WALL = "W"

    def __init__(self, type, pos_x, pos_y):
        self.type = type
        self.pos_x = pos_x
        self.pos_y = pos_y


class SnakeControls():
    # snake control consts
    UP = "U"
    LEFT = "L"
    RIGHT = "R"
    DOWN = "D"
    LAST = "LMS"


class SnakeGame():
    # main snake class

    # init
    def __init__(self, size_x, size_y):
        # if too small, don't create
        if size_x < 10 or size_y < 10:
            print("Board is too small!")
            return

        # extending for walls
        self.size_x = size_x + 2
        self.size_y = size_y + 2

        # max distance
        self.max_distance = math.floor(math.hypot(size_y, size_x))

        # generate board and wall
        self.board = []

        for y in range(self.size_x):
            board_row = []
            for x in range(self.size_y):
                if x == 0 or x == (self.size_x - 1) or y == 0 or y == (self.size_y - 1):
                    base_element = SnakeObjects(SnakeObjects.WALL, x, y)
                else:
                    base_element = SnakeObjects(SnakeObjects.EMPTY, x, y)

                board_row.append(base_element)
            self.board.append(board_row)

        # create snake
        self.snake = []

        # randomize head
        self.snake.append(SnakeObjects(SnakeObjects.HEAD, random.randint(2, self.size_x - 3), random.randint(2, self.size_y - 5)))

        self.board[self.snake[0].pos_y][self.snake[0].pos_x].type = SnakeObjects.HEAD

        # add 2 trailing body
        self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y + 1))
        self.snake.append(SnakeObjects(SnakeObjects.BODY, self.snake[0].pos_x, self.snake[0].pos_y + 2))

        self.board[self.snake[1].pos_y][self.snake[1].pos_x].type = SnakeObjects.BODY
        self.board[self.snake[2].pos_y][self.snake[2].pos_x].type = SnakeObjects.BODY

        # snake direction
        self.dir_x = 0
        self.dir_y = 1
        self.last_move = SnakeControls.UP

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
        self.default_health = self.max_distance * 2
        self.health = self.default_health

        # snake status
        self.alive = True

        # initial calculation
        self.refreshSensor()
        self.calculateFitness()

    # refresh sensors
    def refreshSensor(self):

        # resets sensor
        self.sensor = []
        self.sensor.append([0, 0, 0])  # LB
        self.sensor.append([0, 0, 0])  # LM
        self.sensor.append([0, 0, 0])  # LT
        self.sensor.append([0, 0, 0])  # MT
        self.sensor.append([0, 0, 0])  # RT
        self.sensor.append([0, 0, 0])  # RM
        self.sensor.append([0, 0, 0])  # RB
        self.sensor.append([0, 0, 0])  # MB

        # head position
        head_x = self.snake[0].pos_x
        head_y = self.snake[0].pos_y

        # scan for LB (Left Bottom)
        for i in range(1, self.max_distance):
            cur_x = head_x - i
            cur_y = head_y + i
            dir_type = 0
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
                break

        # scan for LM (Left Middle)
        for i in range(1, self.max_distance):
            cur_x = head_x - i
            cur_y = head_y
            dir_type = 1
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (i / self.max_distance)
                break

        # scan for LT (Left Top)
        for i in range(1, self.max_distance):
            cur_x = head_x - i
            cur_y = head_y - i
            dir_type = 2
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
                break

        # scan for MT (Middle Top)
        for i in range(1, self.max_distance):
            cur_x = head_x
            cur_y = head_y - i
            dir_type = 3
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (i / self.max_distance)
                break

        # scan for RT (Right Top)
        for i in range(1, self.max_distance):
            cur_x = head_x + i
            cur_y = head_y - i
            dir_type = 4
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
                break

        # scan for RM (Right Middle)
        for i in range(1, self.max_distance):
            cur_x = head_x + i
            cur_y = head_y
            dir_type = 5
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (i / self.max_distance)
                break

        # scan for RB (Right Bottom)
        for i in range(1, self.max_distance):
            cur_x = head_x + i
            cur_y = head_y + i
            dir_type = 6
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (math.hypot((head_y - cur_y), (head_x - cur_x)) / self.max_distance)
                break

        # scan for MB (Middle Bottom)
        for i in range(1, self.max_distance):
            cur_x = head_x
            cur_y = head_y + i
            dir_type = 7
            tile_type = self.board[cur_y][cur_x].type

            if self.sensor[dir_type][0] == 0 and tile_type == SnakeObjects.BODY:
                self.sensor[dir_type][0] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.FOOD:
                self.sensor[dir_type][1] = 1 - (i / self.max_distance)
            elif tile_type == SnakeObjects.WALL:
                self.sensor[dir_type][2] = 1 - (i / self.max_distance)
                break

    # calculate snake fitness
    def calculateFitness(self):
        self.fitness = 5 * len(self.snake) + 4 * (self.max_distance - math.hypot((self.snake[0].pos_y - self.food.pos_y), (self.snake[0].pos_x - self.food.pos_x))) + 3 * self.health

    # refresh snake body positions
    def refreshSnakeBody(self, new_x, new_y):

        last_x = self.snake[len(self.snake) - 1].pos_x
        last_y = self.snake[len(self.snake) - 1].pos_y

        ls_x = self.snake[0].pos_x
        ls_y = self.snake[0].pos_y

        for i in range(1, len(self.snake)):
            # refr = esh body
            ln_x = self.snake[i].pos_x
            ln_y = self.snake[i].pos_y
            self.snake[i].pos_x = ls_x
            self.snake[i].pos_y = ls_y
            ls_x = ln_x
            ls_y = ln_y
            # redraw body
            self.board[self.snake[i].pos_y][self.snake[i].pos_x].type = SnakeObjects.BODY

        # set last to empty
        self.board[last_y][last_x].type = SnakeObjects.EMPTY

        # update head
        self.snake[0].pos_x = new_x
        self.snake[0].pos_y = new_y

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
    def updateSnake(self, direction=SnakeControls.LAST):

        # if no input set last
        if direction == SnakeControls.LAST:
            direction = self.last_move

        # process input
        if direction == SnakeControls.UP and self.last_move != SnakeControls.DOWN:
            self.dir_x = 0
            self.dir_y = -1
            self.last_move = SnakeControls.UP
        elif direction == SnakeControls.LEFT and self.last_move != SnakeControls.RIGHT:
            self.dir_x = -1
            self.dir_y = 0
            self.last_move = SnakeControls.LEFT
        elif direction == SnakeControls.RIGHT and self.last_move != SnakeControls.LEFT:
            self.dir_x = 1
            self.dir_y = 0
            self.last_move = SnakeControls.RIGHT
        elif direction == SnakeControls.DOWN and self.last_move != SnakeControls.UP:
            self.dir_x = 0
            self.dir_y = 1
            self.last_move = SnakeControls.DOWN
        else :
            if self.last_move == SnakeControls.UP:
                self.dir_x = 0
                self.dir_y = -1
                self.last_move = SnakeControls.UP
            elif self.last_move == SnakeControls.LEFT:
                self.dir_x = -1
                self.dir_y = 0
                self.last_move = SnakeControls.LEFT
            elif self.last_move == SnakeControls.RIGHT:
                self.dir_x = 1
                self.dir_y = 0
                self.last_move = SnakeControls.RIGHT
            elif self.last_move == SnakeControls.DOWN:
                self.dir_x = 0
                self.dir_y = 1
                self.last_move = SnakeControls.DOWN

        # calculate movement
        target_x = self.snake[0].pos_x + self.dir_x
        target_y = self.snake[0].pos_y + self.dir_y

        # check on target
        target_type = self.board[target_y][target_x].type

        # if target is wall or body, snake dies,  if food eat
        eat_food = False
        if target_type == SnakeObjects.WALL or (target_type == SnakeObjects.BODY and len(self.snake) > 4):
            self.alive = False
        elif target_type == SnakeObjects.FOOD:
            eat_food = True
            last_pos_x = self.snake[len(self.snake) - 1].pos_x
            last_pos_y = self.snake[len(self.snake) - 1].pos_y

        self.refreshSnakeBody(target_x, target_y)

        if eat_food:
            self.snake.append(SnakeObjects(SnakeObjects.BODY, last_pos_x, last_pos_y))
            self.board[self.snake[len(self.snake) - 1].pos_y][self.snake[len(self.snake) - 1].pos_x].type = SnakeObjects.BODY
            self.regenerateFood()
            self.health = self.default_health
        else:
            self.health = self.health - 1

        if self.health <= 0:
            self.alive = False

        self.refreshSensor()
        self.calculateFitness()

        return self.alive, self.sensor, self.fitness

    # draws board to console
    def drawConsole(self):
        for board_row in self.board:
            for tile in board_row:
                print(tile.type, end=" ")
            print()
        print()
        print("Body, Food, Wall")
        print("LB :",self.sensor[0])
        print("LM :",self.sensor[1])
        print("LT :",self.sensor[2])
        print("MT :",self.sensor[3])
        print("RT :",self.sensor[4])
        print("RM :",self.sensor[5])
        print("RB :",self.sensor[6])
        print("MB :",self.sensor[7])
        print("Fitness: ",self.fitness)
        print("Health: ",self.health)
        # print(len(self.snake))

snake_instance = SnakeGame(15, 15)

snake_instance.drawConsole()

while snake_instance.alive:
    inp = str(getch())
    if  inp.find("a") != -1:
        inp = SnakeControls.LEFT
    elif inp.find("s") != -1:
        inp = SnakeControls.DOWN
    elif inp.find("d") != -1:
        inp = SnakeControls.RIGHT
    elif inp.find("w") != -1:
        inp = SnakeControls.UP

    snake_instance.updateSnake(inp)
    os.system("cls")
    snake_instance.drawConsole()

print(snake_instance.fitness)
