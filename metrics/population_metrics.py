from __future__ import division

from deap import tools
import numpy
from math import log
import settings


def population_diameter(population, max_seq_len):
    stats = tools.Statistics()
    stats.register("avg_diameter", numpy.mean)
    stats.register("max_diameter", numpy.max)
    stats.register("min_diameter", numpy.min)
    distances = []

    # clear distances
    for ind in population:
        ind.distances = []

    for i in range(len(population)):
        for j in range(i + 1, len(population)):
            distance = distance_between_individuals(population[i], population[j])
            distances.append(distance)

    records = stats.compile(distances)

    # calculate relative diameter (search space = population size)
    rel_diameter = relative_diameter(records["avg_diameter"], max_seq_len)
    records["rel_diameter"] = rel_diameter

    print "Average diameter: " + str(records["avg_diameter"])
    print "Max diameter: " + str(records["max_diameter"])
    print "Relative diameter: " + str(rel_diameter)
    return records


# each individual is a test suite (list of test sequences)
def distance_between_individuals(first_individual, second_individual):
    distance = 0
    for i in range(0, len(first_individual)):
        distance += distance_between_test_sequences(first_individual[i], second_individual[i])

    # print "Calculated distance:" + str(distance)
    first_individual.distances.append(distance)
    first_individual.avg_dist = numpy.mean(first_individual.distances)
    second_individual.distances.append(distance)
    second_individual.avg_dist = numpy.mean(second_individual.distances)

    return distance


# each test sequence is a list of events, which are coded as strings
def distance_between_test_sequences(first_sequence, second_sequence):
    distance = abs(len(first_sequence) - len(second_sequence))

    for idx, event in enumerate(first_sequence):
        if idx < len(second_sequence):
            if event != second_sequence[idx]:
                distance += 1
        else:
            break

    return distance


def relative_diameter(avg_diameter, max_seq_len):
    return avg_diameter / (max_seq_len * settings.SUITE_SIZE)


# needs to be verified
def population_diversity(population):
    avg_seq_len, max_seq_len = get_avg_max_seq_len(population)
    diversity = 0
    total_suite_size = len(population) * settings.SUITE_SIZE
    for e_idx in range(0, max_seq_len):
        for tc_idx in range(0, settings.SUITE_SIZE):
            events = []
            for ind in population:
                tc = ind[tc_idx]
                if e_idx < len(tc):
                    events.append(tc[e_idx])
            k = number_of_duplicates(events)
            if k > 0:
                diversity += (k / total_suite_size * log(k / total_suite_size))

    diversity = averaging_factor(avg_seq_len) * diversity
    print "Population diversity: " + str(diversity)
    return diversity


def number_of_duplicates(array):
    no_duplicates = set(array)
    dup_count = len(array) - len(no_duplicates)
    return dup_count


def averaging_factor(avg_seq_len):
    res = -1.0 / (avg_seq_len * log(avg_seq_len))
    return res


def get_avg_max_seq_len(population):
    sequence_lengths = []
    for ind in population:
        for tc in ind:
            sequence_lengths.append(len(tc))

    max_seq_len = max(sequence_lengths)
    avg_seq_len = sum(sequence_lengths) / len(sequence_lengths)

    return avg_seq_len, max_seq_len


def extract_events(ind):
    events = []
    for seq in ind:
        for e in seq:
            events.append(e)
    return events
