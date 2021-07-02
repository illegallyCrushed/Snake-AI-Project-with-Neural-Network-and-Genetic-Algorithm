SCREEN_RESOLUTION_WIDTH = 800
SCREEN_RESOLUTION_HEIGHT = SCREEN_RESOLUTION_WIDTH
SCREEN_RESOLUTION = SCREEN_RESOLUTION_WIDTH, SCREEN_RESOLUTION_HEIGHT

GAME_WIDTH = 10
GAME_HEIGHT = GAME_WIDTH

COLOR_BLACK = 0, 0, 0
COLOR_WHITE = 255, 255, 255

MAX_MEMORY = 4096
MAX_EPOCHS = 1
BATCH_SIZE = 32
MAX_BATCH = 64
LEARNING_RATE = 0.001
MOMENTUM_RATE = 0.9
GAMMA_VAR = 0.95
# GAME_COUNT_MAX = 100000
GAME_COUNT_MAX = 64
EPSILON = 1
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.01
EAT_REWARD = 10
DIED_REWARD = -100
STARVE_REWARD = -100
WALKING_REWARD = 1

MUTATION_CHANCE = 0.01
# INDIVIDUAL_IN_POPULATION = 1
INDIVIDUAL_IN_POPULATION = 20

INPUT_LAYER = 32
HIDDEN_LAYER = [64,64]
OUTPUT_LAYER = 4
USE_BIAS = True

VISION_16 = [
#   LM                 LD          
    [-1, 0], [-2, 1],  [-1, 1],  [-1, 2],
#   MD                 RD              
    [0, 1],  [1, 2],   [1, 1],   [2, 1],
#   RM                 RU         
    [1, 0],  [2, -1],  [1, -1],  [1, -2],
#   MU                 LU         
    [0, -1], [-1, -2], [-1, -1], [-2, -1]
]
VISION_8 = [VISION_16[i] for i in range(len(VISION_16)) if i%2==0]
VISION_4 = [VISION_16[i] for i in range(len(VISION_16)) if i%4==0]
DEFAULT_VISION = VISION_8
USE_BINARY = False

#18 +1 64
#32 +1 32