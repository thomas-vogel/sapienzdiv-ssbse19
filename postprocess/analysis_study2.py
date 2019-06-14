# author: Thomas Vogel

import json
import analysis_settings as ids
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from a12 import *
from VD_A import *


SMALL_SIZE = 18 #12
MEDIUM_SIZE = 20 #14
BIGGER_SIZE = 22 #16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def sec_to_min(secs):
    return round(secs / 60)


def analyze(data, plot_file_path, csv_file_path, tex_file_path):
    labels = [0.1, 0.6]
    plt.rcParams["figure.figsize"] = [20, 13] # 21, 13
    fig, axs = plt.subplots(4, 10, sharex='col', sharey='row')

    # write some info to csv
    csv_file = open(csv_file_path, "w")
    dc = ","
    empty_colum = " " + dc
    csv_file.write(empty_colum + "CRAHSHES SUM" + dc + "--" + dc + "CRASHES AVG" + dc + "--" + dc + "\n")
    csv_file.write("APP" + dc + "SAPIENZ" + dc + "SAPIENZ DIV" + dc + "SAPIENZ" + dc + "SAPIENZ DIV" + dc + "\n")

    # create tex table with effect size
    tex_file = open(tex_file_path, "w")
    tex_file.write(get_table_header())

    app_number = 0
    for app in sorted(data.keys(), key=lambda v: v.upper()):
        print("\n" + app)
        app_results = data[app]

        #
        # SAPIENZ
        #
        app_results_for_sapienz = app_results.get(ids.SAPIENZ)
        if app_results_for_sapienz is None:
            generations_for_sapienz = []
            exec_times_for_sapienz = []
            coverage_for_sapienz = []
            crashes_for_sapienz = []
            length_for_sapienz = []
        else:
            generations_for_sapienz = app_results_for_sapienz[ids.GENERATION]
            # generations_for_sapienz = filter_generations(generations_for_sapienz)
            exec_times_for_sapienz = app_results_for_sapienz[ids.EXEC_TIME]
            exec_times_for_sapienz = map(sec_to_min, exec_times_for_sapienz)

            coverage_for_sapienz = app_results_for_sapienz[ids.MAX_COVERAGE]
            coverage_for_sapienz = filter_coverage(coverage_for_sapienz)
            crashes_for_sapienz = app_results_for_sapienz[ids.UNIQUE_CRASHES]
            length_for_sapienz = app_results_for_sapienz[ids.AVG_MIN_LENGTH]
            length_for_sapienz = filter_length(length_for_sapienz)

        #
        # SAPIENZ DIV
        #
        app_results_for_sapienzdiv = app_results.get(ids.SAPIENZDIV)
        if app_results_for_sapienzdiv is None:
            generations_for_sapienzdiv = []
            exec_times_for_sapienzdiv = []
            coverage_for_sapienzdiv = []
            crashes_for_sapienzdiv = []
            length_for_sapienzdiv = []
        else:
            generations_for_sapienzdiv = app_results_for_sapienzdiv[ids.GENERATION]
            # generations_for_sapienzdiv = filter_generations(generations_for_sapienzdiv)
            exec_times_for_sapienzdiv = app_results_for_sapienzdiv[ids.EXEC_TIME]
            exec_times_for_sapienzdiv = map(sec_to_min, exec_times_for_sapienzdiv)

            coverage_for_sapienzdiv = app_results_for_sapienzdiv[ids.MAX_COVERAGE]
            coverage_for_sapienzdiv = filter_coverage(coverage_for_sapienzdiv)
            crashes_for_sapienzdiv = app_results_for_sapienzdiv[ids.UNIQUE_CRASHES]
            length_for_sapienzdiv = app_results_for_sapienzdiv[ids.AVG_MIN_LENGTH]
            length_for_sapienzdiv = filter_length(length_for_sapienzdiv)

        #
        # csv
        #
        csv_file.write(app + dc + str(np.sum(crashes_for_sapienz)) + dc + str(np.sum(crashes_for_sapienzdiv)) + dc
                       + str(np.mean(crashes_for_sapienz)) + dc + str(np.mean(crashes_for_sapienzdiv)) + dc + "\n")

        #
        # plot coverages
        #
        coverages_for_app = [coverage_for_sapienz, coverage_for_sapienzdiv]
        print(" -- Coverage: " + str(coverages_for_app))
        print(" ---- Mean   Sapienz/SapienzDiv: " + str(np.mean(coverage_for_sapienz)) + "/" + str(np.mean(coverage_for_sapienzdiv)))
        print(" ---- Median Sapienz/SapienzDiv: " + str(np.median(coverage_for_sapienz)) + "/" + str(np.median(coverage_for_sapienzdiv)))

        axs[0, app_number].boxplot(coverages_for_app, 0, '', positions=labels, widths=(0.3,0.3))
        for i in range(len(coverages_for_app)):
            if len(coverages_for_app[i]) > 0:
                axs[0, app_number].plot(labels[i], np.mean(coverages_for_app[i]), ".", label='mean', color='black', linestyle=':')
        axs[0, app_number].set_title(get_short_app_name(app))
        axs[0, app_number].set_xticklabels(["S", "Sd"])

        #
        # plot crashes
        #
        crashes_for_app = [crashes_for_sapienz, crashes_for_sapienzdiv]
        print(" -- Crashes " + str(crashes_for_app))
        print(" ---- Mean   Sapienz/SapienzDiv: " + str(np.mean(crashes_for_sapienz)) + "/" + str(np.mean(crashes_for_sapienzdiv)))
        print(" ---- Median Sapienz/SapienzDiv: " + str(np.median(crashes_for_sapienz)) + "/" + str(np.median(crashes_for_sapienzdiv)))

        axs[1, app_number].boxplot(crashes_for_app, 0, '', positions=labels, widths=(0.3, 0.3))
        for i in range(len(crashes_for_app)):
            if len(crashes_for_app[i]) > 0:
                axs[1, app_number].plot(labels[i], np.mean(crashes_for_app[i]), ".", label='mean', color='black',
                                        linestyle=':')
        # axs[1, app_number].set_title(get_short_app_name(app))
        axs[1, app_number].set_xticklabels(["S", "Sd"])

        #
        # plot length
        #
        lengths_for_app = [length_for_sapienz, length_for_sapienzdiv]
        print(" -- Lengths " + str(lengths_for_app))
        print(" ---- Mean   Sapienz/SapienzDiv: " + str(np.mean(length_for_sapienz)) + "/" + str(np.mean(length_for_sapienzdiv)))
        print(" ---- Median Sapienz/SapienzDiv: " + str(np.median(length_for_sapienz)) + "/" + str(np.median(length_for_sapienzdiv)))

        axs[2, app_number].boxplot(lengths_for_app, 0, '', positions=labels, widths=(0.3, 0.3))
        for i in range(len(lengths_for_app)):
            if len(lengths_for_app[i]) > 0:
                axs[2, app_number].plot(labels[i], np.mean(lengths_for_app[i]), ".", label='mean', color='black',
                                        linestyle=':')
        # axs[1, app_number].set_title(get_short_app_name(app))
        axs[2, app_number].set_xticklabels(["S", "Sd"])

        #
        # plot time
        #
        exec_times_for_app = [exec_times_for_sapienz, exec_times_for_sapienzdiv]
        print(" -- Execution Time: " + str(exec_times_for_app))
        print(" ---- Mean   Sapienz/SapienzDiv: " + str(np.mean(exec_times_for_sapienz)) + "/" + str(np.mean(exec_times_for_sapienzdiv)))
        print(" ---- Median Sapienz/SapienzDiv: " + str(np.median(exec_times_for_sapienz)) + "/" + str(np.median(exec_times_for_sapienzdiv)))

        axs[3, app_number].boxplot(exec_times_for_app, 0, '', positions=labels, widths=(0.3, 0.3))
        for i in range(len(exec_times_for_app)):
            if len(exec_times_for_app[i]) > 0:
                axs[3, app_number].plot(labels[i], np.mean(exec_times_for_app[i]), ".", label='mean', color='black',
                                        linestyle=':')
        # axs[3, app_number].set_title(get_short_app_name(app))
        axs[3, app_number].set_xticklabels(["S", "Sd"])


        #
        # plot generations
        #
        # generations_for_app = [generations_for_sapienz, generations_for_sapienzdiv]
        # print(" -- Generations: " + str(generations_for_app))
        #
        # axs[4, app_number].boxplot(generations_for_app, 0, '', positions=labels, widths=(0.3, 0.3))
        # for i in range(len(generations_for_app)):
        #     if len(generations_for_app[i]) > 0:
        #         axs[4, app_number].plot(labels[i], np.mean(generations_for_app[i]), ".", label='mean', color='black',
        #                                 linestyle=':')
        # #axs[3, app_number].set_title(get_short_app_name(app))
        # axs[4, app_number].set_xticklabels(["S", "Sdiv"])


        #
        # tests
        #
        cove_significant = kruskal(coverage_for_sapienz, coverage_for_sapienzdiv, "Coverage", app)
        cras_significant = kruskal(crashes_for_sapienz, crashes_for_sapienzdiv, "Crashes", app)
        leng_significant = kruskal(length_for_sapienz, length_for_sapienzdiv, "Length", app)
        time_significant = kruskal(exec_times_for_sapienz, exec_times_for_sapienzdiv, "ExecTime", app)

        #
        # effect size A12
        #
        cove_es = effect_size(coverage_for_sapienzdiv, coverage_for_sapienz, ids.MAX_COVERAGE, app)
        cras_es = effect_size(crashes_for_sapienzdiv, crashes_for_sapienz, ids.UNIQUE_CRASHES, app)
        leng_es = effect_size(length_for_sapienzdiv, length_for_sapienz, ids.AVG_MIN_LENGTH, app)
        time_es = effect_size(exec_times_for_sapienzdiv, exec_times_for_sapienz, ids.EXEC_TIME, app)

        table_row = get_short_app_name(app) + " & " + get_version(app) + " & "

        if cove_significant:
            table_row += "\\textbf{"
        table_row += float_to_str(cove_es)
        if cove_significant:
            table_row += "}"
        table_row += " & "

        if cras_significant:
            table_row += "\\textbf{"
        table_row += float_to_str(cras_es)
        if cras_significant:
            table_row += "}"
        table_row += " & "

        if leng_significant:
            table_row += "\\textbf{"
        table_row += float_to_str(leng_es)
        if leng_significant:
            table_row += "}"
        table_row += " & "

        if time_significant:
            table_row += "\\textbf{"
        table_row += float_to_str(time_es)
        if time_significant:
            table_row += "}"
        table_row += " \\\\ "

        tex_file.write(table_row + "\n")

        # next app
        app_number = app_number + 1

    tex_file.write(get_table_end())

    # set labels for y axes
    axs[0, 0].set(ylabel="Coverage")
    axs[1, 0].set(ylabel="#Crashes")
    axs[2, 0].set(ylabel="Length")
    axs[3, 0].set(ylabel="Time (min)")
    # axs[4, 0].set(ylabel="Generations")

    # show the plot
    fig.tight_layout()
    fig.subplots_adjust(left=0.05, right=0.98, bottom=0.05, top=0.95,
                        hspace=0.04, wspace=0.0)
    fig.savefig(plot_file_path)
    #plt.show()


def float_to_str(f):
    s = str(f)
    if len(s) == 3:
        s += "0"
    return s


def filter_coverage(coverages):
    return filter(lambda a: a != 0, coverages)


def filter_length(lengths):
    return filter(lambda a: a != 0, lengths)


def filter_generations(gens):
    return filter(lambda a: a != 0, gens)


def get_short_app_name(app):
    if app == "apps.babycaretimer_6_src":
        return "BabyCare"
    if app == "arity.calculator_27_src":
        return "Arity"
    if app == "com.brocktice.JustSit":
        return "JustSit"
    if app == "com.frankcalise.h2droid":
        return "Hydrate"
    if app == "com.github.wdkapps.fillup":
        return "FillUp"
    if app == "com.leafdigital.kanji.android":
        return "Kanji"
    if app == "com.mkf.droidsat":
        return "Droidsat"
    if app == "com.totsp.bookworm_19_src":
        return "BookWorm"
    if app == "com.zapta.apps.maniana":
        return "Maniana"
    if app == "pro.oneredpixel.l9droid":
        return "L9Droid"


def get_version(app):
    if app == "apps.babycaretimer_6_src":
        return "1.5"
    if app == "arity.calculator_27_src":
        return "1.27"
    if app == "com.brocktice.JustSit":
        return "0.3.3"
    if app == "com.frankcalise.h2droid":
        return "1.5"
    if app == "com.github.wdkapps.fillup":
        return "1.7.2"
    if app == "com.leafdigital.kanji.android":
        return "1.0"
    if app == "com.mkf.droidsat":
        return "2.52"
    if app == "com.totsp.bookworm_19_src":
        return "1.0.18"
    if app == "com.zapta.apps.maniana":
        return "1.26"
    if app == "pro.oneredpixel.l9droid":
        return "0.6"


def kruskal(sapienz_data, sapienzdiv_data, property, app):
    msg = "Test property " + property + " of app " + app + ": "
    H, pval = stats.mstats.kruskalwallis(sapienz_data, sapienzdiv_data)

    msg += "H-statistic:" + str(H) + "\tP-Value:" + str(pval) + "\t"

    if pval < 0.05:
        print(msg + "Reject NULL hypothesis - Significant differences exist between groups.")
        return True
    if pval > 0.05:
        print(msg + "Accept NULL hypothesis - No significant difference between groups.")
        return False


def effect_size(sapienzdiv_data, sapienz_data, property, app):
    # max obj., then rev true
    # min obj., then rev false
    if property == ids.UNIQUE_CRASHES or property == ids.MAX_COVERAGE:
        rev = True
    elif property == ids.AVG_MIN_LENGTH or property == ids.EXEC_TIME:
        rev = False

    # use effect size code by Tim
    es_tim = a12(sapienzdiv_data, sapienz_data, rev)
    es_tim_round = round(es_tim, 2)
    # compute with alternative code
    if len(sapienzdiv_data) == len(sapienz_data):
        if rev:
            es_alt = VD_A(sapienzdiv_data, sapienz_data)
        else:
            es_alt = VD_A(sapienz_data, sapienzdiv_data)
        es_alt_round = round(es_alt[0], 2)
    else:
        es_alt_round = "N/A"
    print("Effect size SAPIENZ-SAPIENZDIV for property " + property + ": " + str(es_tim_round) + " / " + str(es_alt_round) + "\t(app: " + str(app) + ")")
    return es_tim_round


def get_table_header():
    header = "\\begin{tabular}{lrrrrr}\n" \
            + "\\toprule\n" \
            + "\\textbf{App} & \\textbf{Ver.} & \\textbf{Coverage Sd-S} & \\textbf{\\#Crashes Sd-S} & \\textbf{Length Sd-S} & \\textbf{Time Sd-S} \\\\ \n" \
            + "\\midrule\n"
    return header


def get_table_end():
    end = "\\bottomrule\n" \
          + "\\end{tabular}"
    return end


if __name__ == "__main__":
    study = "/home/tom/SSBSE19/study2/"
    with open(study + 'data.json') as f:
        data = json.load(f)

    analyze(data, study + "study2.pdf", study + "study2.csv", study + "effectsize.tex")

