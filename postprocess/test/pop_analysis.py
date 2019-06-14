# author: Thomas Vogel

import pickle

from deap import creator, base

'''
Show the latest? population
'''

creator.create("FitnessCovLen", base.Fitness, weights=(10.0, -0.5, 1000.0))
creator.create("Individual", list, fitness=creator.FitnessCovLen)

def show_pop():
    file_path = "../apks/repeated_results/1/a2dp.Vol_93_src/intermediate/"
    pop_file = open(file_path + "pop.pickle")

    pop = pickle.load(pop_file)

    print pop
    print len(pop)


if __name__ == "__main__":
    show_pop()
