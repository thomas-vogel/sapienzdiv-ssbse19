# author: Thomas Vogel

import pickle
import numpy as np

DEBUG = False


def get_gen_and_max_coverage(app_folder_path):
    logbook = get_logbook(app_folder_path)
    if logbook is not None:
        # get number of generations
        # print logbook.select("gen")
        gen = np.max(logbook.select("gen"))
        if DEBUG:
            print("Generations: " + str(gen))
            # print logbook

        # get max coverage
        max_coverage = 0
        for gen_pop in logbook.select("pop_fitness"):
            for pop_ind_fitness in gen_pop:
                coverage = pop_ind_fitness[0]
                if coverage > max_coverage:
                    max_coverage = coverage
        if DEBUG:
            print("Max coverage: " + str(max_coverage))
    else:
        print("--There is no logbbook.")
        gen = 0
        max_coverage = 0
    return gen, max_coverage


def get_logbook(app_folder_path):
    try:
        logbook_file = open(app_folder_path + "/intermediate/logbook.pickle")
        logbook = pickle.load(logbook_file)
        return logbook
    except:
        return None
