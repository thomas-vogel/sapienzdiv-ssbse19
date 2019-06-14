import os
import sys
import pickle
import matplotlib.pyplot as plt
import matplotlib
import settings
import two_d_line
import numpy as np
from shutil import copyfile


plt.style.use(['seaborn-white', 'seaborn-paper'])
plt.style.use('~/Development/BA-Chinh-Tran-Hong/Software/sapienz/plot/sapienz.mplstyle')

plt.rcParams.update({'font.size': 30})
matplotlib.rc("font", family="Times New Roman")

linestyles = ['-', '--', '-.', ':', '-']


def get_mean_logbooks(working_dir):
    logbooks = []
    app_names = []
    mean_folder = os.path.join(working_dir, 'mean_values')
    files = [f for f in os.listdir(mean_folder) if os.path.isfile(os.path.join(mean_folder, f))]
    for f in files:
        if f.endswith('pickle'):
            file_path = os.path.join(mean_folder, f)
            lb = pickle.load(open(file_path))
            app_names.append(f.split('.')[0])
            logbooks.append(lb)

    return logbooks, app_names

def get_logbooks(working_dir):
    logbooks = []
    folders = [folder for folder in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, folder))]

    for folder in folders:
        folder_dir = os.path.join(working_dir, folder)

        file_path = os.path.join(folder_dir, 'intermediate/logbook.pickle')

        lb = pickle.load(open(file_path))

        logbooks.append(lb)
    print str(len(logbooks)) + ' Logbooks found'
    return logbooks


def plotStats(logbooks, app_names, working_dir, key, y_label=''):
    gen = logbooks[0].select('gen')
    lines = []
    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Generation")
    ax1.set_ylabel(y_label)
    for i, lb in enumerate(logbooks):
        y_values = lb.select(key)
        line = ax1.plot(gen, y_values, label=app_names[i], color="black", linestyle=linestyles[i])
        lines += line

    two_d_line.createFigure(fig, ax1, lines, working_dir, key)


def plotStats2(gen, arrays, app_names, working_dir, key, y_label=''):
    lines = []
    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Generation")
    ax1.set_ylabel(y_label)
    ax1.set_ylim([0, 250])
    for i, lb in enumerate(arrays):
        y_values = arrays[i]
        line = ax1.plot(gen, y_values, label=app_names[i], color="black", linestyle=linestyles[i])
        lines += line

    two_d_line.createFigure(fig, ax1, lines, working_dir, key)


def plotGraphMetric(logbooks, app_names, apk_dir, metric_key, y_label=''):
    gen = logbooks[0].select("gen")

    for i, weight in enumerate(settings.MAX_EDGE_WEIGHTS):
        lns = []
        fig, ax1 = plt.subplots()
        ax1.set_xlabel("Generation")
        ax1.set_ylabel(y_label)
        # ax1.set_ylim([-0.2, 1.2])

        for j, lb in enumerate(logbooks):
            lb_key = metric_key + '_' + str(weight)
            y_values = lb.select(lb_key)
            line = ax1.plot(gen, y_values, label=app_names[j], color="black", linestyle=linestyles[j])
            lns += line
        two_d_line.createFigure(fig, ax1, lns, apk_dir, metric_key + '_' + str(weight))


def plotBarChart(values, app_names, working_dir, ylabel=''):
    patterns = ('-', '+', 'x', '\\', '*', 'o', 'O', '.', '/')
    colors = ['y', 'r', 'b']

    ind = np.arange(len(values))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    for i, value in enumerate(values):
        rects1 = ax.bar(ind + width * i, value, width, color=colors[i], label=app_names[i])

    # add some text for labels, title and axes ticks
    ax.set_ylabel(ylabel)
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(app_names)
    plt.legend()

    plt.show()


def get_mean_vals(logbooks, key):
    arr = []
    for lb in logbooks:
        arr.append(lb.select(key))

    res = []
    if len(arr) == 0:
        return res

    for j in range(0, len(arr[0])):
        tmp = []
        for i in range(0, len(arr)):
            val = arr[i][j]
            if val is not None:
                tmp.append(val)
        print tmp
        res.append(np.mean(tmp))

    return res


def save_mean_vals(working_dir, logbooks, app_name):
    dict = {}
    mean_values_folder = os.path.join(working_dir, 'mean_values')
    # create output folder
    if not os.path.exists(mean_values_folder):
        os.makedirs(mean_values_folder)

    for m, desc in metrics.iteritems():
        res = get_mean_vals(logbooks, m)
        dict[m] = res

    dict_file = open(os.path.join(mean_values_folder, app_name + '.pickle'), 'wb')
    pickle.dump(dict, dict_file)
    dict_file.close()


def calculate_means(working_dir):
    folders = [f for f in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, f))]
    for folder in folders:
        if folder == 'mean_values' or folder == 'intermediate':
            continue
        folder_path = os.path.join(working_dir, folder)
        logbooks = get_logbooks(folder_path)
        save_mean_vals(working_dir, logbooks, folder)



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
    # min_val = -0.1 * max(max_diameter)
    # ax1.set_ylim(ymin=min_val)
    # ax1.xaxis.set_major_locator(loc)

    lns = line1 + line2 + line3
    two_d_line.createFigure(fig, ax1, lns, apk_dir, 'population_diameter')

metrics = {'max_diameter': 'Maximum diameter',
           'min_diameter': 'Minimum diameter',
           'avg_diameter': 'Average diameter',
           'hv_hof': 'Hypervolume',
           'population_diversity': '',
           'rel_diameter': 'Relative diameter',
           'proportion_pareto_optimal': 'Percentage of Pareto optimal solutions',
           'kconnec': 'Minimum distance for connected graph',
           'pconnec_300': 'Percentage of solutions in clusters',
           'lconnec_300': 'Number of solutions in largest cluster',
           'nconnec_300': 'Number of clusters',
           'sing_300': 'Percentage of singletons',
           'avgconnec_300': 'Average distance in largest cluster',
           'hvconnec_300': 'Percentage of hypervolume covered by largest cluster'}

if __name__ == "__main__":
    #working_dir = sys.argv[1]
    apps = ['aarddict', 'k9-mail', 'keepass', 'hotdeath', 'munchlife']
    for app in apps:
        working_dir = '/Users/ctran/Desktop/40gen-50ind/metric_results/' + app

        calculate_means(working_dir)

        dicts, app_names = get_mean_logbooks(working_dir)
        metric = 'avgconnec_300'

        pareto_opt = dicts[0].get(metric)
        arrs = [pareto_opt]
        metric_names = ['Average distance in largest cluster']
        plotStats2(range(0, len(arrs[0])), arrs, metric_names, working_dir, metric, 'k')

        dest = '/Users/ctran/Dropbox/BA-Tex/img/metrics/' + app
        copyfile(os.path.join(working_dir + '/intermediate', metric + '.pdf'), os.path.join(dest, metric + '.pdf'))


        # pconnec = dicts[0].get('pconnec_300')
    # sing = dicts[0].get('sing_300')
    # arrs = [pconnec, sing]
    # metric_names = ['pconnec', 'sing']
    # plotStats2(range(0, len(arrs[0])), arrs, metric_names, working_dir, 'pconnec_sing', 'percentage')
    # max_diameter = dicts[0].get('max_diameter')
    # avg_diameter = dicts[0].get('avg_diameter')
    # min_diameter = dicts[0].get('min_diameter')
    #
    # arrs = [max_diameter, avg_diameter, min_diameter]
    # metrics_names = ['Maximum diameter', 'Average diameter', 'Minimum diameter']
    # plotStats2(range(0, len(arrs[0])), arrs, metrics_names, working_dir, 'population_diameter', 'diameter')

    # for m, desc in metrics.iteritems():
    #     arrays = []
    #     for d in dicts:
    #         arrays.append(d.get(m))
    #
    #     print arrays
    #     plotStats2(range(0, len(arrays[0])), arrays, app_names, working_dir, m, desc)
