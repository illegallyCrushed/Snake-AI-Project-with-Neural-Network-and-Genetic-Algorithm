import genetic
import agent
from constants import *
import json
import os
import threading


population = []
current_generation = 1

def initialCreation():
    population = []
    for _ in range(INDIVIDUAL_IN_POPULATION):
        population.append(agent.SnakeAgent())
    return population,1

def continueFromData(file):
    return genetic.loadParents(file)

def updateAgentThreadFunc(individual,i):
    individual.updateAgent(i)
    print("Snake {} = {}/{} | Average Fitness = {} |  Average Length = {}".format(i,  individual.num_game, GAME_COUNT_MAX,  individual.highest_fitness,  individual.highest_length))

def loadSingle(file):
    filehandle = open(file, 'r')
    data = json.load(filehandle)
    parent = agent.SnakeAgent()
    parent.num_game = data["game_number"] + 1
    parent.brain.decodeWeight(data["parent_weight"])
    parent.highest_fitness = data["parent_fitness"]
    filehandle.close()
    return parent


print("Enter to start, file location to continue!")
start = input()
if start != "":
    population, current_generation = continueFromData(start)
    # population.append(loadSingle(start))
else:
    population, current_generation = initialCreation()

while True:
    print("Current Gen = {}".format(current_generation))
    print("Total Population = {}".format(len(population)))
    results = []
    threads = []

    for i in range(len(population)):
        updateAgentThreadFunc(population[i],i)

    # for i in range(len(population)):
    #     new_thread = threading.Thread(target=updateAgentThreadFunc, args=(population[i],i))
    #     new_thread.start()
    #     threads.append(new_thread)

    # for i in range(len(threads)):
    #     threads[i].join()

    population = genetic.geneticAlgorithm(population,current_generation)
    current_generation += 1
    # wain = input()
    # os.system("cls")
    
