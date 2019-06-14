# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

import sys
import os
import settings
from metrics import connectedness_metrics as cm

colors = ["g-", "b-", "r-", "c-", "m-", "y-", "k-", "w-"]

y_min = 0
y_max = 0

plt.style.use(['seaborn-white', 'seaborn-paper'])
# plt.style.use('~/sapienz-div/plot/sapienz.mplstyle')
plt.style.use('./plot/sapienz.mplstyle')

loc = plticker.MultipleLocator(base=5.0) # this locator puts ticks at regular intervals
linestyles = ['-', '--', '-.', ':', '.']


def extract_axis(array, axis):
    ret = []
    for elem in array:
        ret.append(elem[axis])
    return ret


def createFigure(fig, axis, lines, apk_dir, file_name):
    global y_max, y_min
    # print "ymin : " + str(y_min)
    # print "ymax : " + str(y_max)
    if y_max != 0 or y_min != 0:
        plt.ylim(y_min, y_max)
    axis.set_xlabel("Generation")
    axis.grid(True, linestyle=':', linewidth=1)
    labs = [l.get_label() for l in lines]
    leg = axis.legend(lines, labs, loc="best", frameon=False)
    leg.get_frame().set_alpha(0.5)
    # plt.show()
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)

    intermediate_folder = os.path.join(apk_dir, 'intermediate')
    # create output folder
    if not os.path.exists(intermediate_folder):
        os.makedirs(intermediate_folder)

    fig.savefig(apk_dir + '/intermediate/' + file_name + '.pdf', dpi=300)
    y_min = 0
    y_max = 0


def plot(logbook, axis, apk_dir):
    gen = logbook.select("gen")
    fit_avg = extract_axis(logbook.select("avg"), axis)
    fit_min = extract_axis(logbook.select("min"), axis)
    fit_max = extract_axis(logbook.select("max"), axis)

    fig, ax1 = plt.subplots()
    line3 = ax1.plot(gen, fit_max, label="Max Fitness", color="black", linestyle=linestyles[0])
    line1 = ax1.plot(gen, fit_avg, label="Avg Fitness", color="black", linestyle=linestyles[1])
    line2 = ax1.plot(gen, fit_min, label="Min Fitness", color="black", linestyle=linestyles[2])

    createFigure(fig, ax1, line1 + line2 + line3, apk_dir, 'obj_' + str(axis))


def plotProportionParetoOptimal(logbook, apk_dir):
    plotStats(logbook, apk_dir, 'proportion_pareto_optimal', 'Proportions of Pareto Optimal Solutions', '')
    plotStats(logbook, apk_dir, 'hv_size', 'Hall of Fame size', '')


def plotPopulationDiameter(logbook, apk_dir):
    gen = logbook.select("gen")
    max_diameter = logbook.select("max_diameter")
    avg_diameter = logbook.select("avg_diameter")
    min_diameter = logbook.select("min_diameter")

    fig, ax1 = plt.subplots()
    line1 = ax1.plot(gen, max_diameter, label="Max. Diameter", markevery=5, color="black", linestyle='-')
    line2 = ax1.plot(gen, avg_diameter, label="Avg. Diameter", markevery=5, color="black", linestyle='--')
    line3 = ax1.plot(gen, min_diameter, label="Min. Diameter", markevery=5, color="black", linestyle=':')
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Diameter")
    min_val = -0.1 * max(max_diameter)
    ax1.set_ylim(ymin=min_val)
    ax1.xaxis.set_major_locator(loc)

    lns = line1 + line2 + line3
    createFigure(fig, ax1, lns, apk_dir, 'population_diameter')


def plotRelativeDiameter(logbook, apk_dir):
    plotStats(logbook, apk_dir, 'rel_diameter', 'Relative Diameter', '')


def plotPopulationDiversity(logbook, apk_dir):
    plotStats(logbook, apk_dir, 'population_diversity', 'Population Diversity', '')


def plotStats(logbook, apk_dir, key, label='', y_label=''):
    gen = logbook.select("gen")
    y_values = logbook.select(key)

    fig, ax1 = plt.subplots()
    line1 = ax1.plot(gen, y_values, label=label, markevery=5, color="black")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel(y_label)

    createFigure(fig, ax1, line1, apk_dir, key)


def plotGraphMetrics(logbook, apk_dir):
    for key, desc in cm.metrics.iteritems():
        if key != 'kconnec':
            plotGraphMetric(logbook, apk_dir, key, desc)
        else:
            plotStats(logbook, apk_dir, 'kconnec', 'Minimum distance necessary for a connected graph (kconnec)',
                      'Distance')


def plotGraphMetric(logbook, apk_dir, metric_key, metric_name):
    gen = logbook.select("gen")
    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Generation")
    lns = []
    for i, weight in enumerate(settings.MAX_EDGE_WEIGHTS):
        lb_key = metric_key + '_' + str(weight)
        y_values = logbook.select(lb_key)
        plt.text = metric_name
        line = ax1.plot(gen, y_values, label="k = " + str(weight), color="black", linestyle=linestyles[i])
        lns += line

    createFigure(fig, ax1, lns, apk_dir, metric_key)


def plotHypervolume(logbook, apk_dir):
    plotStats(logbook, apk_dir, 'hv_standard', 'Hypervolume', '')
    plotStats(logbook, apk_dir, 'hv_hof', 'Hypervolume Hall of Fame', '')


if __name__ == "__main__":
    logbook_dir = sys.argv[1]

    logbook = pickle.load(open(logbook_dir))  # draw graphs
    logbook_file_name = logbook_dir.split('/')[-1]
    instrumented_app_dir = logbook_dir.replace('/' + logbook_file_name, '')
    os.system("mkdir " + instrumented_app_dir + "/intermediate")

    # plot(logbook, 0, instrumented_app_dir)
    # plot(logbook, 1, instrumented_app_dir)
    # plot(logbook, 2, instrumented_app_dir)
    # plotProportionParetoOptimal(logbook, instrumented_app_dir)
    plotPopulationDiameter(logbook, instrumented_app_dir)
    # plotRelativeDiameter(logbook, instrumented_app_dir)
    # plotPopulationDiversity(logbook, instrumented_app_dir)
    # plotGraphMetrics(logbook, instrumented_app_dir)
    # plotHypervolume(logbook, instrumented_app_dir)
