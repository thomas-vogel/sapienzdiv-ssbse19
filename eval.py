from os import listdir, system
from os.path import isfile, join, isdir
import pickle
import matplotlib.pyplot as plt
import matplotlib
import settings
import numpy as np
from difflib import SequenceMatcher


plt.style.use(['seaborn-white', 'seaborn-paper'])
plt.style.use('~/Development/BA-Chinh-Tran-Hong/Software/sapienz/plot/sapienz.mplstyle')

plt.rcParams.update({'font.size': 30})
matplotlib.rc("font", family="Times New Roman")

linestyles = ['-', '--', '-.', ':', '.']

GEN = 40

def get_logbooks(dir):
    logbooks = []
    for folder in listdir(dir):
        if '.DS_Store' in folder or folder == 'norerandom': #fixme
            continue
        intermediate_folder = join(dir, folder) + "/intermediate"
        files = [f for f in listdir(intermediate_folder) if isfile(join(intermediate_folder, f))]
        for f in files:
            if f == 'logbook.pickle':
                file_path = join(intermediate_folder, f)
                lb = pickle.load(open(file_path))
                logbooks.append(lb)
    print "Logbook count: " + str(len(logbooks))
    return logbooks


def extract_axis(array, axis):
    ret = []
    for elem in array:
        ret.append(elem[axis])
    return ret


def file_len(fname):
    with open(fname) as f:
        return sum(1 for _ in f)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def is_unique(content, unique_crashes):
    for c in unique_crashes:
        similarity = similar(c, content)
        #print 'Sim: ' + str(similarity)
        if similarity > 0.90:
            return False

    return True


def mean_crash_script_lengths(crash_scripts):
    file_lengths = []
    for c in crash_scripts:
        file_lengths.append(file_len(c))

    if len(file_lengths) == 0:
        return 0
    return np.mean(file_lengths)

def unique_crashes(dir):
    min_lengths = []
    crash_lengths = []
    unique_crashes_counts = []
    total_crashes_counts = []
    # for each output folder
    for folder in listdir(dir):
        min_length = 1000
        unique_crashes = set()
        total_crashes = []
        unique_crashes_scripts = []
        crashes_folder = join(dir, folder) + "/crashes"
        if not isdir(crashes_folder):
            continue
        files = [f for f in listdir(crashes_folder) if isfile(join(crashes_folder, f))]
        # for each file in crashes folder
        for f in files:
            # if is stack trace
            if f.startswith('bugreport'):
                with open(join(crashes_folder, f)) as bug_report_file:
                    content = ""
                    for line_no, line in enumerate(bug_report_file):
                        if line_no == 0:
                            continue
                        content += line
                    total_crashes.append(content)
                    if len(unique_crashes) > 0:
                        if is_unique(content, unique_crashes):
                            unique_crashes.add(content)
                            unique_crashes_scripts.append(join(crashes_folder, f.replace('bugreport', 'script')))
                    else:
                        unique_crashes.add(content)
                        unique_crashes_scripts.append(join(crashes_folder, f.replace('bugreport', 'script')))
            # if is crash script
            elif f.startswith('script'):
                script_length = file_len(join(crashes_folder, f)) - 4
                if script_length < min_length:
                    min_length = script_length

        # calculate mean crash script length of unique crashes
        crash_lengths.append(mean_crash_script_lengths(unique_crashes_scripts))

        if min_length != 1000:
            min_lengths.append(min_length)
        unique_crashes_counts.append(len(unique_crashes))
        total_crashes_counts.append(len(total_crashes))
    if len(unique_crashes_counts) == 0:
        return 0, 0, 0
    return np.mean(unique_crashes_counts), sum(total_crashes_counts), np.mean(min_lengths), np.mean(crash_lengths)


def get_results(logbooks, working_dir, gen):
    max_covs = []
    min_lens = []
    max_crashes = []
    hypervolumes = []

    for lb in logbooks:
        if len(lb.select('gen')) <= gen:
            gen = 39
        max_covs.append(max(extract_axis(lb.select("max"), 0)[0:gen+1]))
        min_lens.append(min(extract_axis(lb.select("min"), 1)[0:gen+1]))
        max_crashes.append(max(extract_axis(lb.select("max"), 2)[0:gen+1]))

        hypervolumes.append(max(lb.select('hv_hof')[0:gen+1]))

    number_unique_crashes, total_crashes, min_crash_script_len, avg_crash_script_len = unique_crashes(working_dir)
    print "Generations: " + str(gen)
    print "Max. Coverage: " + str(np.mean(max_covs))
    print "Min. Length: " + str(np.mean(min_lens))
    print "Max. crashes: " + str(np.mean(max_crashes))
    print "Number of unique Crashes: " + str(number_unique_crashes)
    print "Number of total Crashes: " + str(total_crashes)
    print "Min. crash script length: " + str(min_crash_script_len)
    print "Avg. crash script length: " + str(avg_crash_script_len)
    print "HV: " + str(np.mean(hypervolumes))


def get_results_for_app(app):
    print "Analyzing " + app
    #working_dir = "/Users/ctran/Desktop/USBVeritasData/"
    standard_results_folder = "/Volumes/VERITAS/Sapienz/metric_results/"
    enhanced_results_folder = "/Volumes/VERITAS/Sapienz/enhanced_results/"

    logbooks = get_logbooks(standard_results_folder + app + "/")
    print "------Standard Results------"
    get_results(logbooks, standard_results_folder + app, GEN)

    logbooks = get_logbooks(enhanced_results_folder + app + "/")
    print "------Enhanced Results------"
    get_results(logbooks, enhanced_results_folder + app, GEN)


if __name__ == "__main__":
    apps = ['aarddict', 'dalvik_explorer', 'dialer2', 'hotdeath', 'k9-mail', 'keepass', 'lpg', 'mileage', 'munchlife', 'mylock']
    for app in apps:
        get_results_for_app(app)
        print '---------------------------------\n'