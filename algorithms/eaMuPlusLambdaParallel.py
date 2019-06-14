from __future__ import division

import random
import time
import pickle
import multiprocessing as mp
import psutil
import sys

from metrics import connectedness_metrics as cm
from metrics import non_dominated_metrics as ndm
from metrics import population_metrics as pm

from devices import emulator, real_device
import settings

# global results for mp callback
results = []
idle_devices = []


def process_results(data):
    indi_index, fitness, device = data
    results.append((indi_index, fitness))
    idle_devices.append(device)


def evaluate_in_parallel(eval_suite_parallel, individuals, apk_dir, package_name, gen):
    """ Evaluate the individuals fitnesses and assign them to each individual
	:param eval_fitness: The fitness evaluation fucntion
	:param individuals: The individuals under evaluation
	:param pool_size:
	:return: When all individuals have been evaluated
	"""

    # init global states
    while len(results) > 0:
        results.pop()
    while len(idle_devices) > 0:
        idle_devices.pop()

    # 1. get idle devices
    if settings.USE_REAL_DEVICE:
        idle_devices.extend(real_device.get_devices())
    else:
        idle_devices.extend(emulator.get_devices())

    # 2. assign tasks to devices
    pool = mp.Pool(processes=len(idle_devices))
    for i in range(0, len(individuals)):
        while len(idle_devices) == 0:
            time.sleep(0.5)
        pool.apply_async(eval_suite_parallel, args=(individuals[i], idle_devices.pop(0), apk_dir, package_name, gen, i),
                         callback=process_results)

    print "### evaluate_in_parallel is waiting for all processes to finish ... "
    # should wait for all processes to finish
    pool.close()
    pool.join()

    print "### ... evaluate_in_parallel finished"
    # assign results
    while len(results) > 0:
        i, fitness = results.pop(0)
        individuals[i].fitness.values = fitness


def hv_stagnating(logbook):
    hypervolumes = logbook.select('hv_standard')
    if len(hypervolumes) >= 3:
        hypervolumes = hypervolumes[len(hypervolumes) - 3: len(hypervolumes)]
        if len(list(set(hypervolumes))) == 3:
            print "Hypervolume is stagnating"
            return True
    return False


def low_diversity(logbook):
    avg_diameters = logbook.select('avg_diameter')
    if avg_diameters[-1] / avg_diameters[0] <= settings.DIVERSITY_THRESHOLD:
        return True
    return False


def evolve(logbook, population, toolbox, mu, lambda_, cxpb, mutpb, ngen, apk_dir, package_name,
           stats=None, halloffame=None, verbose=__debug__, resume=False):

    start_gen = 0
    if not resume:
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        # fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        # for ind, fit in zip(invalid_ind, fitnesses):
        # 	ind.fitness.values = fit
        evaluate_in_parallel(toolbox.evaluate, invalid_ind, apk_dir, package_name, 0)

        # discard invalid population individual
        for i in range(len(population) - 1, -1, -1):
            if not population[i].fitness.valid:
                del population[i]

        record = stats.compile(population) if stats is not None else {}

        if halloffame is not None:
            halloffame.update(population)
            record['hof_size'] = len(halloffame)

        # run metric algorithms
        record = calc_metrics(toolbox, population, record)

        logbook.record(gen=0, nevals=len(invalid_ind), **record)

        if verbose:
            print logbook.stream

        save_files(logbook, population, halloffame, apk_dir)
    else:
        start_gen = logbook.select('gen')[-1]
        print 'Resuming at generation ' + str(start_gen + 1)

    # Begin the generational process
    for gen in range(start_gen + 1, ngen + 1):
        apply_diversity_action = settings.RE_RANDOMIZE and low_diversity(logbook)
        if apply_diversity_action:
            offspring = toolbox.population(n=settings.OFFSPRING_SIZE, apk_dir=apk_dir, package_name=package_name)
        else:
            offspring = varOr(population, toolbox, lambda_, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

        # check memory usage, reboot if needed
        if psutil.virtual_memory().percent > 90:
            emulator.destroy_devices()
            time.sleep(2)
            emulator.boot_devices()

        # this function will eval and match each invalid_ind to its fitness
        # fitness is invalid if it contains no values
        evaluate_in_parallel(toolbox.evaluate, invalid_ind, apk_dir, package_name, gen)

        if settings.DEBUG:
            for indi in invalid_ind:
                print indi.fitness.values

        # discard invalid offspring individual
        for i in range(len(offspring) - 1, -1, -1):
            if not offspring[i].fitness.valid:
                print "### Warning: Invalid Fitness"
                del offspring[i]

        # Update the hall of fame with the generated individuals
        print "### Updating Hall of Fame ..."
        if halloffame is not None:
            halloffame.update(offspring)
            len(halloffame)

        # assert fitness
        invalid_ind_post = [ind for ind in population + offspring if not ind.fitness.valid]
        print "### assert len(invalid_ind) == 0, len = ", len(invalid_ind_post)
        assert len(invalid_ind_post) == 0

        # Select the next generation population
        if apply_diversity_action:
            population[:] = toolbox.select_most_diverse(population + offspring, mu)
        elif settings.INCLUDE_MOST_DIVERSE:
            pareto_front = toolbox.select(population + offspring, mu)
            most_diverse = toolbox.select_most_diverse(population + offspring, mu)
            diff = []
            selected = []
            diff.extend(x for x in most_diverse if x not in pareto_front)

            for i, ind in enumerate(diff):
                if i < mu * settings.PROPORTION_DIVERSE_IND:
                    selected.append(ind)

            while len(selected) < mu:
                selected.append(pareto_front.pop(0))

            population[:] = selected
        else:
            population[:] = toolbox.select(population + offspring, mu)


        # Update the statistics with the new population
        record = stats.compile(population) if stats is not None else {}

        # run metric algorithms
        record = calc_metrics(toolbox, population, record)
        record['hv_hof'] = ndm.hypervolume(halloffame.items)
        record['hv_size'] = len(halloffame)

        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print logbook.stream

        # in case interrupted
        save_files(logbook, population, halloffame, apk_dir)

    return population, logbook


def getIndividualsWithHighDistance(population, n):
    sorted_pop = sorted(population, key=lambda x: x.avg_dist, reverse=True)
    while len(sorted_pop) > n:
        sorted_pop.pop(-1)

    return sorted_pop


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
            ind, = toolbox.mutate(ind)
            del ind.fitness.values
            offspring.append(ind)
        else:  # Apply reproduction
            offspring.append(random.choice(population))

    return offspring


def calc_metrics(toolbox, population, record):
    pareto_front = toolbox.pareto_front(population, settings.POPULATION_SIZE, True)[0]

    front_proportion = ndm.proportion_pareto_optimal(pareto_front, population)
    record['proportion_pareto_optimal'] = front_proportion

    max_seq_len = record['max'][1]
    diameter_records = pm.population_diameter(population, max_seq_len)
    record.update(diameter_records)

    diversity = pm.population_diversity(population)
    record['population_diversity'] = diversity

    # hypervolume
    hv_standard = ndm.hypervolume(pareto_front)
    record['hv_standard'] = hv_standard

    graph_records = cm.analyze_graph(pareto_front, hv_standard, max_edge_weights=settings.MAX_EDGE_WEIGHTS)
    for gr in graph_records:
        record.update(gr)

    return record


def save_files(logbook, population, hof, instrumented_app_dir):
    # persistent
    logbook_file = open(instrumented_app_dir + "/intermediate/logbook.pickle", 'wb')
    pickle.dump(logbook, logbook_file)
    logbook_file.close()

    population_file = open(instrumented_app_dir + "/intermediate/pop.pickle", 'wb')
    pickle.dump(population, population_file)
    population_file.close()

    hof_file = open(instrumented_app_dir + "/intermediate/hof.pickle", 'wb')
    pickle.dump(hof, hof_file)
    hof_file.close()


def load_files(instrumented_app_dir):
    logbook = pickle.load(open(instrumented_app_dir + "/intermediate/logbook.pickle"))
    population = pickle.load(open(instrumented_app_dir + "/intermediate/pop.pickle"))
    hof = pickle.load(open(instrumented_app_dir + "/intermediate/hof.pickle"))

    return logbook, population, hof