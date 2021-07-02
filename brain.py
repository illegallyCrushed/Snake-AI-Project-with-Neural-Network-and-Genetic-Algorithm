import numpy
from tensorflow import keras
from constants import *

class SnakeBrain:
    # neural class from snake's brain using reinforced learning (QNet)

    def __init__(self,learning_rate):
        # create neural model
        self.neural = keras.models.Sequential()
        for i in range(len(HIDDEN_LAYER)):
            if i == 0:
                self.neural.add(keras.layers.Dense(HIDDEN_LAYER[i], input_dim=INPUT_LAYER, activation='relu', use_bias=USE_BIAS))
            else:
                self.neural.add(keras.layers.Dense(HIDDEN_LAYER[i], activation='relu', use_bias=USE_BIAS))
        self.neural.add(keras.layers.Dense(OUTPUT_LAYER, activation='softmax', use_bias=USE_BIAS))
        # setup optimizer and loss
        self.neural.compile(optimizer=keras.optimizers.Adam(learning_rate=learning_rate), loss=keras.losses.MSE)

    # encodes weight to 1D array
    def encodeWeight(self):
        weights = []

        if not USE_BIAS:
            # no bias

            for ly in range(len(HIDDEN_LAYER) - 1):
                if ly == 0:
                # layer I -> H1
                    for i in range(INPUT_LAYER):
                        for j in range(HIDDEN_LAYER[ly]):
                            weights.append(float(self.neural.get_weights()[ly][i][j]))
                # layer Hn -> Hn+1
                for i in range(HIDDEN_LAYER[ly]):
                    for j in range(HIDDEN_LAYER[ly+1]):
                        weights.append(float(self.neural.get_weights()[ly+1][i][j]))
            # layer Hnl -> O
            for i in range(HIDDEN_LAYER[len(HIDDEN_LAYER)-1]):
                for j in range(OUTPUT_LAYER):
                    weights.append(float(self.neural.get_weights()[len(HIDDEN_LAYER) - 1][i][j]))

        else:

            # layer I -> H1
            for i in range(INPUT_LAYER):
                for j in range(HIDDEN_LAYER[0]):
                    weights.append(float(self.neural.get_weights()[0][i][j]))
            # layer I -> H1 BIAS
            for i in range(HIDDEN_LAYER[0]):
                weights.append(float(self.neural.get_weights()[1][i]))
            
            for ly in range(len(HIDDEN_LAYER) - 1):
                # layer Hn -> Hn+1
                for i in range(HIDDEN_LAYER[ly]):
                    for j in range(HIDDEN_LAYER[ly+1]):
                        weights.append(float(self.neural.get_weights()[2*(ly+1)][i][j]))
                # layer Hn -> Hn+1 BIAS
                for i in range(HIDDEN_LAYER[ly+1]):
                    weights.append(float(self.neural.get_weights()[1+(2*(ly+1))][i]))

            # layer Hnl -> O
            for i in range(HIDDEN_LAYER[len(HIDDEN_LAYER)-1]):
                for j in range(OUTPUT_LAYER):
                    weights.append(float(self.neural.get_weights()[len(self.neural.get_weights())-2][i][j]))
            # layer Hnl -> O BIAS
            for i in range(OUTPUT_LAYER):
                weights.append(float(self.neural.get_weights()[len(self.neural.get_weights())-1][i]))

        return weights

    # decodes and applied 1D array of weights
    def decodeWeight(self, weights):
        layers = []
        layers_bias = []

        # initiate layer containers
        for ly in range(len(HIDDEN_LAYER) - 1):
            if ly == 0:
                # layer I -> H1
                layers.append([])
                # layer I -> H1 BIAS
                layers_bias.append([])
            # layer Hn -> Hn+1
            layers.append([])
            # layer Hn -> Hn+1 BIAS
            layers_bias.append([])
        # layer Hnl -> O
        layers.append([])
        # layer Hnl -> O BIAS
        layers_bias.append([])
        
        pointer = 0
        if not USE_BIAS:
            # no bias

            for ly in range(len(HIDDEN_LAYER) - 1):
                if ly == 0:
                # layer I -> H1
                    for _ in range(INPUT_LAYER):
                        temp = []
                        for _ in range(HIDDEN_LAYER[ly]):
                            temp.append(weights[pointer])
                            pointer = pointer + 1
                        layers[ly].append(temp)
                # layer Hn -> Hn+1
                for _ in range(HIDDEN_LAYER[ly]):
                    temp = []
                    for _ in range(HIDDEN_LAYER[ly+1]):
                        temp.append(weights[pointer])
                        pointer = pointer + 1
                    layers[ly+1].append(temp)
            # layer Hnl -> O
            for _ in range(HIDDEN_LAYER[len(HIDDEN_LAYER)-1]):
                temp = []
                for _ in range(OUTPUT_LAYER):
                    temp.append(weights[pointer])
                    pointer = pointer + 1
                layers[len(layers)-1].append(temp)
                        

            # form numpy array
            all_weights = []
            for layer in layers:
                all_weights.append(numpy.array(layer)) 
                     
        else:

            for ly in range(len(HIDDEN_LAYER) - 1):
                if ly == 0:
                    # layer I -> H1
                    for _ in range(INPUT_LAYER):
                        temp = []
                        for _ in range(HIDDEN_LAYER[ly]):
                            temp.append(weights[pointer])
                            pointer = pointer + 1
                        layers[ly].append(temp)
                    # layer I -> H1 BIAS
                    for _ in range(HIDDEN_LAYER[ly]):
                        layers_bias[ly].append(weights[pointer])
                        pointer = pointer + 1
                # layer Hn -> Hn+1
                for _ in range(HIDDEN_LAYER[ly]):
                    temp = []
                    for _ in range(HIDDEN_LAYER[ly+1]):
                        temp.append(weights[pointer])
                        pointer = pointer + 1
                    layers[ly+1].append(temp)
                # layer Hn -> Hn+1 BIAS
                for _ in range(HIDDEN_LAYER[ly+1]):
                    layers_bias[ly+1].append(weights[pointer])
                    pointer = pointer + 1
            # layer Hnl -> O
            for _ in range(HIDDEN_LAYER[len(HIDDEN_LAYER)-1]):
                temp = []
                for _ in range(OUTPUT_LAYER):
                    temp.append(weights[pointer])
                    pointer = pointer + 1
                layers[len(layers)-1].append(temp)
            # layer Hnl -> O BIAS
            for _ in range(OUTPUT_LAYER):
                layers_bias[len(layers_bias)-1].append(weights[pointer])
                pointer = pointer + 1

            # form numpy array
            all_weights = []
            for i in range(len(layers)):
                all_weights.append(numpy.array(layers[i]))
                all_weights.append(numpy.array(layers_bias[i]))

        # set model weights
        self.neural.set_weights(all_weights)
