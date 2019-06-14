# author: Thomas Vogel

import pickle
import settings
import matplotlib.pyplot as plt
from deap.benchmarks.tools import hv
from deap import creator, base, tools
import postprocess.logbook_analysis

creator.create("FitnessCovLen", base.Fitness, weights=(10.0, -0.5, 1000.0))
creator.create("Individual", list, fitness=creator.FitnessCovLen)


def show_hof():
    file_path = "../subjects/a2dp.Vol_93_src/intermediate/"
    hof_file = open(file_path + "hof.pickle")

    hof = pickle.load(hof_file)

    print hof
    print len(hof)

    for individual in hof:
        print
        print type(individual)
        print individual
        print individual.fitness.values


def print_pop_fitness(app_folder_path):
    logbook = postprocess.logbook_analysis.get_logbook(app_folder_path)
    print logbook
    print ""

    hof = tools.ParetoFront()

    iteration = 0
    pop = []
    for gen_pop in logbook.select("pop_fitness"):
        print("Iteration " + str(iteration))
        print("Population: " + str(gen_pop))
        for pop_ind_fitness in gen_pop:
            ind =  creator.Individual([])
            ind.fitness.values = pop_ind_fitness
            pop.append(ind)
        iteration = iteration + 1

        hof.update(pop)
        print "HoF"
        for hof_member in hof:
            print(hof_member.fitness)


def draw_pop_fitness(app_folder_path):
    coverages = []
    lengths = []
    colors = []  # color stands for the ith gen

    logbook = postprocess.logbook_analysis.get_logbook(app_folder_path)

    gen_size = len(logbook.select("pop_fitness"))
    for gen, gen_pop in enumerate(logbook.select("pop_fitness")):
        for indi in gen_pop:
            coverages.append(indi[0])
            lengths.append(indi[1])
            colors.append(int(gen + 1))

    # print coverages, lengths, colors

    fig, ax = plt.subplots()
    ax.set_xlabel("Length")
    ax.set_ylabel("Coverage")

    # ax.scatter(lengths, coverages, color="red", marker="^")
    im = ax.scatter(lengths, coverages, c=colors, cmap=plt.cm.jet, marker=".", s=100)

    fig.colorbar(im, ax=ax, ticks=range(1, gen_size + 1))
    im.set_clim(1, gen_size)

    fig.savefig(app_folder_path + "logbook_pop_fitness.png")
    plt.show()


if __name__ == "__main__":
    show_hof()




# testing ##################################################
def test_hv():
    ref = [0.0, float(settings.SEQUENCE_LENGTH_MAX), 0.0]

    ind_1 = 10, 100, 5
    es = hv.hypervolume([get_point(ind_1)], ref)
    print es

    ind_2 = 10, 100, 5
    es = hv.hypervolume([get_point(ind_2)], ref)
    print es


def get_point(fitness):
    return (fitness[0] + 1) * -1, fitness[1] + 1, (fitness[2] + 1) * -1


def test_print_pop_fitness(file_folder_path):
    data = [ [ [11, 100, 50], [10, 90, 50], [8, 90, 50] ],
             [ [12, 100, 50], [10, 120, 50], [8, 90, 50] ],
             [ [13, 100, 50], [11, 85, 50], [8, 90, 50] ]
             ]

    hof = tools.ParetoFront()

    iteration = 0
    pop = []
    for gen_pop in data:
        print("Iteration " + str(iteration))
        print("Population: " + str(gen_pop))
        for pop_ind_fitness in gen_pop:
            ind =  creator.Individual([])
            ind.fitness.values = pop_ind_fitness
            pop.append(ind)
        iteration = iteration + 1

        hof.update(pop)
        print "HoF"
        for hof_member in hof:
            print(hof_member.fitness)
