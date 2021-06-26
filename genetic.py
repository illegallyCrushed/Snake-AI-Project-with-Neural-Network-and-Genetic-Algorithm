import random
import agent
from constants import *
import threading
import json
import heapq

# roulette wheel function, returns 1 selected individual + popped array


def rouletteWheel(population):
    cumulative = sum(population)
    increment = 0
    hit = random.random()
    for i in range(len(population)):
        increment += population[i].highest_fitness/cumulative
        if(increment > hit):
            selected = population.pop(i)
            return selected, population

# crossover function, returns offspring weights
def crossover(parent_a_weight, parent_b_weight):
    crossovers = random.randint(0, MAX_CROSSOVERS)
    swaps = random.sample(range(len(parent_a_weight)), crossovers)
    for i in swaps:
        parent_a_weight[i], parent_b_weight[i] = parent_b_weight[i], parent_a_weight[i]
    if random.random() < 0.5:
        return parent_a_weight
    return parent_b_weight

def mutation(offspring_weight):
    mutations = random.randint(0, MAX_MUTATION)
    mutates = random.sample(range(len(offspring_weight)), mutations)
    max_weight = max(offspring_weight)
    min_weight = min(offspring_weight)
    for i in mutates:
        offspring_weight[i] = min_weight + (max_weight-min_weight) * random.random()
    return offspring_weight

def generateOffspring(new_population, parent_a_weight, parent_b_weight):
    offspring_weight = crossover(parent_a_weight, parent_b_weight)
    if random.random() < MUTATION_CHANCE:
        offspring_weight = mutation(offspring_weight)
    offspring = agent.SnakeAgent()
    offspring.brain.decodeWeight(offspring_weight)
    new_population.append(offspring)

def cleanseParent(parent):
    new_parent = agent.SnakeAgent()
    new_parent.brain.decodeWeight(parent.brain.encodeWeight())
    new_parent.highest_fitness = parent.highest_fitness
    return new_parent

def singleThreadFillPopulation(new_population, parent_candidates, gen_num, max_ind):
    # get 2 highest parent
    parent_highest = heapq.nlargest(2, parent_candidates)
    parent_w_a = parent_highest[0].brain.encodeWeight()
    parent_w_b = parent_highest[1].brain.encodeWeight()

    i = 0
    while len(parent_candidates) > 1:
        # select 2 random parent from parent candidates
        parent_a, parent_candidates = rouletteWheel(parent_candidates)
        parent_b, parent_candidates = rouletteWheel(parent_candidates)
        parent_a_weight = parent_a.brain.encodeWeight()
        parent_b_weight = parent_b.brain.encodeWeight()
        # push both parents into new population
        new_population.append(cleanseParent(parent_a))
        print("Generation {} Generated Offspring: {}/{}".format(gen_num, (i+1), max_ind))
        i+=1
        new_population.append(cleanseParent(parent_b))
        print("Generation {} Generated Offspring: {}/{}".format(gen_num, (i+1), max_ind))
        i+=1
        # generate 2 offsprings
        generateOffspring(new_population, parent_a_weight, parent_b_weight)
        print("Generation {} Generated Offspring: {}/{}".format(gen_num, (i+1), max_ind))
        i+=1
        generateOffspring(new_population, parent_a_weight, parent_b_weight)
        print("Generation {} Generated Offspring: {}/{}".format(gen_num, (i+1), max_ind))
        i+=1


    while len(new_population) != max_ind:
        generateOffspring(new_population, parent_w_a, parent_w_b)
        print("Generation {} Generated Over Offspring: {}/{}".format(gen_num, (i+1), max_ind))
        i+=1

def multiThreadFillPopulation(new_population, parent_candidates, gen_num, max_ind):
    # get 2 highest parent
    parent_highest = heapq.nlargest(2, parent_candidates)
    parent_w_a = parent_highest[0].brain.encodeWeight()
    parent_w_b = parent_highest[1].brain.encodeWeight()

    threads = []
    pcount = 0
    while len(parent_candidates) > 1:
        # select 2 random parent from parent candidates
        parent_a, parent_candidates = rouletteWheel(parent_candidates)
        parent_b, parent_candidates = rouletteWheel(parent_candidates)
        parent_a_weight = parent_a.brain.encodeWeight()
        parent_b_weight = parent_b.brain.encodeWeight()
        # push both parents into new population
        new_population.append(cleanseParent(parent_a))
        print("Generation {} Generated Offspring: {}/{}".format(gen_num, (pcount+1), max_ind))
        pcount += 1
        new_population.append(cleanseParent(parent_b))
        print("Generation {} Generated Offspring: {}/{}".format(gen_num, (pcount+1), max_ind))
        pcount += 1
        # generate 2 offsprings
        new_thread = threading.Thread(target=generateOffspring, args=(new_population, parent_a_weight, parent_b_weight,))
        new_thread.start()
        threads.append(new_thread)
        new_thread = threading.Thread(target=generateOffspring, args=(new_population, parent_a_weight, parent_b_weight,))
        new_thread.start()
        threads.append(new_thread)


    for i in range(len(threads)):
        threads[i].join()
        print("Generation {} Generated Offspring: {}/{}".format(gen_num, (i+1+pcount), max_ind))

    while len(new_population) != max_ind:
        i+=1
        generateOffspring(new_population, parent_w_a, parent_w_b)
        print("Generation {} Generated Over Offspring: {}/{}".format(gen_num, (i+1+pcount), max_ind))

def saveParents(parent_candidates, gen_num):
    filehandle = open("./train_data/gendata_{}.json".format(gen_num), 'w')
    parent_weights = []
    parent_fitnesses = []
    for parent in parent_candidates:
        parent_weights.append(parent.brain.encodeWeight())
        parent_fitnesses.append(parent.highest_fitness)
    jsondata = {
        "generation_number": gen_num,
        "parent_count": len(parent_candidates),
        "population_size": INDIVIDUAL_IN_POPULATION,
        "parent_weights": parent_weights,
        "parent_fitnesses": parent_fitnesses,
    }
    filehandle.write(json.dumps(jsondata, indent=2))
    filehandle.close()

def loadParents(file):
    new_population = []
    parent_candidates = []
    filehandle = open(file, 'r')
    data = json.load(filehandle)
    gen_num = data["generation_number"] + 1
    for i in range(data["parent_count"]):
        parent = agent.SnakeAgent()
        parent.brain.decodeWeight(data["parent_weights"][i])
        parent.highest_fitness = data["parent_fitnesses"][i]
        parent_candidates.append(parent)
    filehandle.close()
    # singleThreadFillPopulation(new_population, parent_candidates, gen_num, data["population_size"])
    multiThreadFillPopulation(new_population, parent_candidates, gen_num, data["population_size"])
    return new_population, gen_num

def geneticAlgorithm(population, gen_num):
    # select parent candidates
    parent_candidates = []
    pop_count = len(population)
    for _ in range(len(population)//2):
        selected_parent, population = rouletteWheel(population)
        parent_candidates.append(selected_parent)
    
    saveParents(parent_candidates,gen_num)
    # creates new population
    new_population = []

    # single threading
    # singleThreadFillPopulation(new_population, parent_candidates, gen_num, pop_count)

    # multi threading
    multiThreadFillPopulation(new_population, parent_candidates, gen_num, pop_count)

    return new_population
