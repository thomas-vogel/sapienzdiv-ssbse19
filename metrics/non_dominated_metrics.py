from __future__ import division
from deap.benchmarks.tools import hv

import numpy
import settings


def proportion_pareto_optimal(pareto_front, population):
    return len(pareto_front) / len(population)


def hypervolume(front):
    # reference point
    ref = [0.0, float(settings.SEQUENCE_LENGTH_MAX), 0.0]
    wobj = []

    for ind in front:
        # each fitness value + 1 to avoid empty hypervolume
        # fitness for length: no multiplication with -1 because the length objective is minimized!
        temp = ((ind.fitness.wvalues[0] + 1) * -1, (ind.fitness.wvalues[1] + 1), (ind.fitness.wvalues[2] + 1) * -1)
        wobj.append(temp)

    if ref is None:
        ref = numpy.max(wobj, axis=0) + 1
    res = hv.hypervolume(wobj, ref)

    print "Hypervolume: " + str(res)

    return res
