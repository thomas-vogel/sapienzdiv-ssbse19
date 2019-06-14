from __future__ import division

import pickle
import sys
import os
import settings
from plot import two_d_line

metrics = ["hv_standard", "proportion_pareto_optimal",
           "rel_diameter", "population_diversity", "kconnec"]

k_metrics = ["pconnec", "sing", "hvconnec", "avgconnec", "nconnec", "lconnec"]

app_dirs = []


def summarize_metrics(working_dir, app_name, count):
    logbooks = get_logbooks(working_dir, app_name, count)
    plot_objectives(logbooks)
    plot_diameter(logbooks)
    plot_metrics(logbooks)
    for app_dir in app_dirs:
        os.system(
            'cd ' + app_dir + '/intermediate && pdfunite obj_0.pdf obj_1.pdf obj_2.pdf hv_standard.pdf '
                              'proportion_pareto_optimal.pdf population_diameter.pdf rel_diameter.pdf '
                              'population_diversity.pdf pconnec.pdf sing.pdf hvconnec.pdf avgconnec.pdf nconnec.pdf '
                              'lconnec.pdf kconnec.pdf summary.pdf')


def plot_objectives(logbooks):
    for obj in range(0, 3):
        y_min, y_max = find_ylim_objective(logbooks, obj)
        for i, logbook in enumerate(logbooks):
            two_d_line.y_min = y_min
            two_d_line.y_max = y_max
            two_d_line.plot(logbook, obj, app_dirs[i])


def find_ylim_objective(logbooks, obj):
    max_values = []
    min_values = []
    for logbook in logbooks:
        values = two_d_line.extract_axis(logbook.select('max'), obj)
        max_values.append(max(values))
        values = two_d_line.extract_axis(logbook.select('min'), obj)
        min_values.append(min(values))

    return min(min_values) * 0.9, max(max_values) * 1.1


def plot_diameter(logbooks):
    _, y_max = find_ylim(logbooks, "max_diameter")
    y_min, _ = find_ylim(logbooks, "min_diameter")
    for i, logbook in enumerate(logbooks):
        two_d_line.y_min = y_min
        two_d_line.y_max = y_max
        two_d_line.plotPopulationDiameter(logbook, app_dirs[i])


def plot_metrics(logbooks):
    for key in metrics:
        y_min, y_max = find_ylim(logbooks, key)
        for i, logbook in enumerate(logbooks):
            two_d_line.y_min = y_min
            two_d_line.y_max = y_max
            two_d_line.plotStats(logbook, app_dirs[i], key, key)

    for key in k_metrics:
        y_min, y_max = find_ylim_k_metric(logbooks, key)
        for i, logbook in enumerate(logbooks):
            two_d_line.y_min = y_min
            two_d_line.y_max = y_max
            two_d_line.plotGraphMetric(logbook, app_dirs[i], key, key)


def find_ylim(logbooks, key):
    max_values = []
    min_values = []
    for lb in logbooks:
        values = lb.select(key)
        max_values.append(max(values))
        min_values.append(min(values))

    min_val = min(min_values)
    min_val = min_val * 0.9
    max_val = max(max_values)
    max_val = max_val * 1.1
    return min_val, max_val


def find_ylim_k_metric(logbooks, key):
    max_values = []
    min_values = []
    for i, weight in enumerate(settings.MAX_EDGE_WEIGHTS):
        k_key = key + '_' + str(weight)
        min_val, max_val = find_ylim(logbooks, k_key)
        min_values.append(min_val)
        max_values.append(max_val)

    return min(min_values), max(max_values)


def get_logbooks(working_dir, app_name, count):
    global app_dirs
    logbooks = []
    for i in range(0, count):
        if i == 0:
            app_dir = working_dir + app_name + ".apk_output"
            lb = pickle.load(open(app_dir + "/intermediate/logbook.pickle"))
            logbooks.append(lb)
        else:
            app_dir = working_dir + app_name + ".apk_output_" + str(i)
            lb = pickle.load(open(app_dir + "/intermediate/logbook.pickle"))
            logbooks.append(lb)
        app_dirs.append(app_dir)
    return logbooks


if __name__ == "__main__":
    working_dir = sys.argv[1]
    app_name = sys.argv[2]
    count = sys.argv[3]
    if not working_dir.endswith('/'):
        working_dir = working_dir + '/'
    summarize_metrics(working_dir, app_name, int(count))
