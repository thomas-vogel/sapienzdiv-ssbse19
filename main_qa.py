# Copyright (c) 2016-present, Ke Mao. All rights reserved.
from __future__ import division

import random
import sys
import time
import os
from math import log

import networkx as nx
import numpy
from deap import creator, base, tools

import settings
from metrics import connectedness_metrics as cm
from metrics import non_dominated_metrics as ndm

# generate individual by running motifcore
from plot import two_d_line


def get_obj(individual, obj):
    result = 0
    for i, val in enumerate(individual):
        result += first_obj_matrix.item(i, val) + obj_matrices[obj].item(i, val)

    return result


# generate individual by running motifcore
def generate_individual():
    ind = random.sample(range(0, settings.SEQUENCE_LENGTH_MAX), settings.SEQUENCE_LENGTH_MAX)
    return creator.Individual(ind)


# the suite coverage is accumulated
def evaluate_suite(individual):
    fitness = []
    for obj in range(0, 3):
        fitness.append(get_obj(individual, obj))

    return fitness


def cross_over(ind1, ind2):
    ind = toolbox.clone(ind1)
    cp1 = random.randint(0, settings.SEQUENCE_LENGTH_MAX / 2 - 1)
    cp2 = random.randint(settings.SEQUENCE_LENGTH_MAX / 2, settings.SEQUENCE_LENGTH_MAX - 1)
    for i in range(cp1, cp2):
        ind[i] = -1

    diff = [item for item in ind2 if item not in ind]

    j = 0
    for i in range(cp1, cp2):
        ind[i] = diff[j]
        j += 1

    return ind


def mutate(ind):
    i = random.randint(0, len(ind) - 1)
    j = random.randint(0, len(ind) - 1)
    ind[i], ind[j] = ind[j], ind[i]
    return ind


def double_cross_over(ind1, ind2):
    return cross_over(ind1, ind2), cross_over(ind2, ind1)


### deap framework setup
creator.create("FitnessMulti", base.Fitness, weights=(0.01, 0.01, 0.01))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

toolbox.register("individual", generate_individual)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate_suite)
# mate crossover two suites
toolbox.register("mate", double_cross_over)
# mutate should change seq order in the suite as well
toolbox.register("mutate", mutate)
# toolbox.register("select", tools.selTournament, tournsize=5)
toolbox.register("select", tools.selNSGA2)

toolbox.register("pareto_front", tools.sortNondominated)

first_obj_matrix = None
obj_matrices = []


def parse_matrices(file_name, size, objectives):
    global first_obj_matrix
    global obj_matrices
    matrices = []
    with open(file_name) as fp:
        # ignore first line
        next(fp)
        for i in range(0, objectives + 1):
            arrays = []
            while len(arrays) < size:
                line = filter(None, next(fp).strip().split(' '))
                if len(line) > 0:
                    array = map(int, line)
                    arrays.append(array)

            matrices.append(numpy.matrix(arrays))
    first_obj_matrix = matrices.pop(0)
    obj_matrices = matrices


def main(folder_name, instrumented_app_dir, seed=None):
    random.seed(seed)


    # generate initial population
    print "### Initialising population ...."

    population = toolbox.population(n=settings.POPULATION_SIZE)
    hof = tools.ParetoFront()

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    population, logbook = evolve(population, toolbox, settings.POPULATION_SIZE, settings.OFFSPRING_SIZE,
                                 cxpb=settings.CXPB, mutpb=settings.MUTPB,
                                 ngen=settings.GENERATION, stats=stats, halloffame=hof, verbose=True)

    # draw graphs
    two_d_line.plot(logbook, 0, instrumented_app_dir)
    two_d_line.plot(logbook, 1, instrumented_app_dir)
    two_d_line.plot(logbook, 2, instrumented_app_dir)
    two_d_line.plotProportionParetoOptimal(logbook, instrumented_app_dir)
    two_d_line.plotPopulationDiameter(logbook, instrumented_app_dir)
    two_d_line.plotRelativeDiameter(logbook, instrumented_app_dir)
    two_d_line.plotPopulationDiversity(logbook, instrumented_app_dir)
    two_d_line.plotStats(logbook, instrumented_app_dir, 'kconnec', 'kconnec', 'weight')
    two_d_line.plotHypervolume(logbook, instrumented_app_dir)
    time.sleep(5)
    os.system('cd ' + instrumented_app_dir + '/intermediate && mkdir ' + folder_name)
    os.system('cd ' + instrumented_app_dir + '/intermediate && mv *.pdf ' + folder_name + '/')
    os.system('cd ' + instrumented_app_dir + '/intermediate/ ' + folder_name + ' && pdfunite obj_0.pdf obj_1.pdf obj_2.pdf hv_standard.pdf '
                                             'proportion_pareto_optimal.pdf population_diameter.pdf rel_diameter.pdf '
                                             'population_diversity.pdf kconnec.pdf summary.pdf')


def evolve(population, toolbox, mu, lambda_, cxpb, mutpb, ngen,
           stats=None, halloffame=None, verbose=__debug__):
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (
        stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    population = toolbox.select(population, len(population))
    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats is not None else {}

    record = calc_metrics(toolbox, population, record)

    logbook.record(gen=0, nevals=len(invalid_ind), **record)

    for gen in range(1, ngen + 1):
        offspring = varOr(population, toolbox, lambda_, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        print "### Updating Hall of Fame ..."
        if halloffame is not None:
            halloffame.update(offspring)

        # Select the next generation population
        population = toolbox.select(population + offspring, mu)

        # Update the statistics with the new population
        record = stats.compile(population) if stats is not None else {}

        # run metric algorithms
        record = calc_metrics(toolbox, population, record)

        logbook.record(gen=gen, nevals=len(invalid_ind), **record)

    return population, logbook


def calc_metrics(toolbox, population, record):
    pareto_front = toolbox.pareto_front(population, settings.POPULATION_SIZE, True)[0]

    front_proportion = proportion_pareto_optimal(pareto_front, population)
    record['proportion_pareto_optimal'] = front_proportion

    diameter_records = population_diameter(population)
    record.update(diameter_records)

    diversity = population_diversity(population)
    record['population_diversity'] = diversity

    # hypervolume
    hv_standard = ndm.hypervolume(pareto_front)
    record['hv_standard'] = hv_standard

    graph_records = analyze_graph(pareto_front)
    for gr in graph_records:
        record.update(gr)

    return record


def population_diameter(population):
    stats = tools.Statistics()
    stats.register("avg_diameter", numpy.mean)
    stats.register("max_diameter", numpy.max)
    stats.register("min_diameter", numpy.min)
    distances = []
    for i in range(len(population)):
        for j in range(i + 1, len(population)):
            distance = distance_between_individuals(population[i], population[j])
            distances.append(distance)

    records = stats.compile(distances)

    # calculate relative diameter (search space = population size)
    rel_diameter = relative_diameter(records["avg_diameter"])
    records["rel_diameter"] = rel_diameter

    print "Average diameter: " + str(records["avg_diameter"])
    print "Max diameter: " + str(records["max_diameter"])
    print "Relative diameter: " + str(rel_diameter)
    return records


def distance_between_individuals(ind1, ind2):
    distance = abs(len(ind1) - len(ind2))
    for i, event in enumerate(ind1):
        if i < len(ind2):
            if event != ind2[i]:
                distance += 1

    return distance


def relative_diameter(avg_diameter):
    return avg_diameter / settings.SEQUENCE_LENGTH_MAX


def proportion_pareto_optimal(pareto_front, population):
    return len(pareto_front) / len(population)


def varOr(population, toolbox, lambda_, cxpb, mutpb):
    assert (cxpb + mutpb) <= 1.0, ("The sum of the crossover and mutation "
                                   "probabilities must be smaller or equal to 1.0.")

    offspring = []
    for _ in xrange(lambda_):
        op_choice = random.random()
        if op_choice < cxpb:  # Apply crossover
            ind1, ind2 = map(toolbox.clone, random.sample(population, 2))
            ind1, ind2 = toolbox.mate(ind1, ind2)
            del ind1.fitness.values
            offspring.append(ind1)
        elif op_choice < cxpb + mutpb:  # Apply mutation
            ind = toolbox.clone(random.choice(population))
            ind = toolbox.mutate(ind)
            del ind.fitness.values
            offspring.append(ind)
        else:  # Apply reproduction
            offspring.append(random.choice(population))

    return offspring


def population_diversity(population):
    all_values = []
    for ind in population:
        all_values += ind
    all_values = list(set(all_values))

    diversity = 0
    population_size = len(population)
    for val in all_values:
        for i in range(0, settings.SEQUENCE_LENGTH_MAX):
            k = 0
            for ind in population:
                if i < len(ind) and ind[i] == val:
                    k += 1
            if k > 0:
                # print "# same allocation k: " + str(k)
                diversity += (k / population_size * log(k / population_size))

    diversity = averaging_factor(settings.SEQUENCE_LENGTH_MAX) * diversity

    print "Population diversity: " + str(diversity)

    return diversity


def averaging_factor(avg_seq_len):
    res = -1.0 / (avg_seq_len * log(avg_seq_len))
    print "averaging factor: " + str(res)
    return res


def analyze_graph(pareto_front):
    results = []

    G = build_graph(pareto_front, settings.SEQUENCE_LENGTH_MAX)
    kconnec = cm.minimal_connection_distance(G)
    result = {"kconnec": kconnec}
    results.append(result)
    print "Minimum distance necessary for a connected graph: " + str(kconnec)

    return results


def build_graph(pareto_front, max_edge_weight):
    G = nx.Graph()
    if len(pareto_front) == 1:
        G.add_node(0)
        G.node[0]['ind'] = pareto_front[0]
        return G

    for i in range(len(pareto_front)):
        for j in range(i + 1, len(pareto_front)):
            first_ind = pareto_front[i]
            second_ind = pareto_front[j]
            G.add_node(i)
            G.add_node(j)
            G.node[i]['ind'] = first_ind
            G.node[j]['ind'] = second_ind
            distance = distance_between_individuals(first_ind, second_ind)
            if distance <= max_edge_weight:
                G.add_edge(i, j, weight=distance)
    return G


if __name__ == "__main__":
    dir = '/Users/ctran/Development/BA-Chinh-Tran-Hong/Software/sapienz/qap_test/qap_3obj_750fac_corr'
    file_endings = ['-1', '-05', '0', '05', '1']
    for f in file_endings:
        file_name = dir + f
        parse_matrices(file_name, 750, 3)
        app_dir = sys.argv[2]
        folder_name = file_name.split('/')[-1].split('_')[-1]
        main(folder_name, app_dir)
