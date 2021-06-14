import numpy
from tensorflow import keras

class SnakeBrain:
    # neural network class for brain controlling the snake

    # init
    def __init__(self):
        self.model = keras.models.Sequential()
        self.model.add(keras.layers.Dense(16, input_dim=24, activation='sigmoid', use_bias=False))
        self.model.add(keras.layers.Dense(16, activation='sigmoid', use_bias=False))
        self.model.add(keras.layers.Dense(4, activation='sigmoid', use_bias=False))

    def think(self, input_array):
        # check input requirements
        if len(input_array) != 24:
            print("Input Length Missmatch! -> Required 24 | Found ",len(input_array))
            return
        input_array = numpy.array(input_array)
        input_array = input_array.reshape(1, 24)
        return self.model.predict(input_array)[0]

    # encodes weight to 1D array
    def encodeWeight(self):
        weights = []
        # layer I -> H1
        for i in range(24):
            for j in range(16):
                weights.append(self.model.get_weights()[0][i][j])
        # layer H1 -> H2
        for i in range(16):
            for j in range(16):
                weights.append(self.model.get_weights()[1][i][j])
        # layer H2 -> O
        for i in range(16):
            for j in range(4):
                weights.append(self.model.get_weights()[2][i][j])

        return weights
    
    # decodes and applied 1D array of weights
    def decodeWeight(self,weights):
        # check weight requirements
        if len(weights) != 704:
            print("Weight Length Missmatch! -> Required 704 | Found ",len(weights))
            return

        # splits into weight arrays
        layer1=[]
        layer2=[]
        layer3=[]
        pointer = 0
        
         # layer I -> H1
        for _ in range(24):
            temp = []
            for _ in range(16):
                temp.append(weights[pointer])
                pointer = pointer + 1
            layer1.append(temp)
        # layer H1 -> H2
        for _ in range(16):
            temp = []
            for _ in range(16):
                temp.append(weights[pointer])
                pointer = pointer + 1
            layer2.append(temp)
        # layer H2 -> O
        for _ in range(16):
            temp = []
            for _ in range(4):
                temp.append(weights[pointer])
                pointer = pointer + 1
            layer3.append(temp)
        
        # form numpy array
        all_weights = []
        all_weights.append(numpy.array(layer1))
        all_weights.append(numpy.array(layer2))
        all_weights.append(numpy.array(layer3))

        # set model weights
        self.model.set_weights(all_weights)
