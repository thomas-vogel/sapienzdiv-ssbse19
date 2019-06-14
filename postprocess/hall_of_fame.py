# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import pickle

from deap import creator, base

import settings

creator.create("FitnessCovLen", base.Fitness, weights=(10.0, -0.5, 1000.0))
creator.create("Individual", list, fitness=creator.FitnessCovLen)


def show_hof():
    hof_file = open(settings.WORKING_DIR + "intermediate/hof.pickle")

    hof = pickle.load(hof_file)

    print len(hof)

    for individual in hof:
        print type(individual)
        print individual.fitness.values


if __name__ == "__main__":
    show_hof()
