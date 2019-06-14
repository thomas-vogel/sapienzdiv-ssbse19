# author: Thomas Vogel

import json
import analysis_settings as ids
import matplotlib.pyplot as plt
import numpy as np
import os
import bug_report_analysis


def to_csv(data, methods, properties, csv_file_path):
    # delimiting character
    dc = ","
    empty_colum = " " + dc

    csv_file = open(csv_file_path, "w")
    csv_file.write(get_property_header(properties, methods, dc, empty_colum) + "\n")
    method_header = get_method_header(methods, dc) + empty_colum

    method_row = "APP" + dc + empty_colum
    for i in range(len(properties)):
        method_row = method_row + method_header
    csv_file.write(method_row + "\n")

    for app in sorted(data.keys(), key=lambda v: v.upper()):
        app_results = data[app]
        app_results_csv = app + dc + empty_colum
        for property in properties:
            property_results = get_property_for_methods(app_results, methods, property)
            app_results_csv += dc.join(map(str, property_results)) + dc + empty_colum
        csv_file.write(app_results_csv + "\n")


def get_property_for_methods(app_results, methods, property_name):
    property = []
    for method in methods:
        # print("Get property " + property_name + " for method " + method)
        app_results_for_method = app_results.get(method)
        if app_results_for_method is not None:
            property_value = app_results_for_method[property_name]
            if property_name == ids.MAX_COVERAGE or property_name == ids.AVG_MIN_LENGTH:
                property_value = int(property_value)  # use int instead of float
            if property_name == ids.AVG_MIN_LENGTH and property_value == 0:
                property_value = "--"
            if property_name == ids.EXEC_TIME:
                if property_value == -1:
                    property_value = "--"
                else:
                    # Execution time in minutes, then as integer
                    property_value = int(round(property_value / 60))
        else:
            # result for property of testing app with method is not available yet
            property_value = ""
        property.append(property_value)
    return property


def get_property_header(properties, methods, dc, empty_column):
    number_of_methods = len(methods)
    header = empty_column + empty_column
    for property in properties:
        header = header + property + dc
        for i in range(number_of_methods-1):
            header = header + "--" + dc
        header = header + " " + dc
    return header


def get_method_header(methods, dc):
    header = ""
    for method in methods:
        header = header + method + dc
    return header


def plot_coverage(data, file_path):
    cov_sapienz = []
    cov_sapienz_div = []

    sapienz_wins = 0
    sapienz_div_wins = 0
    tie = 0
    for app in sorted(data.keys(), key=lambda v: v.upper()):
        app_results = data[app]

        app_results_for_sapienz = app_results.get(ids.SAPIENZ)
        cov_app_sapienz = app_results_for_sapienz[ids.MAX_COVERAGE]
        cov_sapienz.append(cov_app_sapienz)

        app_results_for_sapienz_div = app_results.get(ids.SAPIENZDIV)
        cov_app_sapienz_div = app_results_for_sapienz_div[ids.MAX_COVERAGE]
        cov_sapienz_div.append(cov_app_sapienz_div)

        if cov_app_sapienz > cov_app_sapienz_div:
            sapienz_wins = sapienz_wins + 1
        elif cov_app_sapienz < cov_app_sapienz_div:
            sapienz_div_wins = sapienz_div_wins + 1
        else:
            tie = tie + 1

    print("COVERAGE:")
    print("SAPIENZ wins    : " + str(sapienz_wins))
    print("SAPIENZ DIV wins: " + str(sapienz_div_wins))
    print("TIE             : " + str(tie))
    print("SUM             : " + str(sapienz_wins + sapienz_div_wins + tie))

    coverages = [cov_sapienz, cov_sapienz_div]
    print(" -- Coverage SAPIENZ (" + str(len(cov_sapienz)) + " apps): " + str(cov_sapienz))
    print(" -- -- mean   " + str(np.mean(cov_sapienz)))
    print(" -- -- median " + str(np.median(cov_sapienz)))
    print(" -- Coverage SAPIENZ DIV (" + str(len(cov_sapienz_div)) + " apps): " + str(cov_sapienz_div))
    print(" -- -- mean " + str(np.mean(cov_sapienz_div)))
    print(" -- -- median " + str(np.median(cov_sapienz_div)))
    names = ["SAPIENZ", "SAPIENZ DIV"]
    labels = range(1, 3)
    plt.rcParams["figure.figsize"] = [3, 2]
    fig, ax = plt.subplots()
    # plt.title(str(cars_number) + " cars")
    ax.boxplot(coverages, 0, '', positions=labels)
    for i in range(len(coverages)):
        ax.plot(labels[i], np.mean(coverages[i]), ".", label='mean', color='black', linestyle=':')
    plt.xticks(labels, names)
    plt.ylabel('Coverage (66 apps)')
    # show the plot
    fig.tight_layout()
    # fig.subplots_adjust(left=0.05, right=0.98, bottom=0.05, top=0.95, hspace=0.04, wspace=0.0)
    fig.savefig(file_path)
    #plt.show()


def plot_time(data, file_path):
    time_sapienz = []
    time_sapienz_div = []

    sapienz_wins = 0
    sapienz_div_wins = 0
    tie = 0
    for app in sorted(data.keys(), key=lambda v: v.upper()):
        app_results = data[app]

        app_results_for_sapienz = app_results.get(ids.SAPIENZ)
        time_app_sapienz = app_results_for_sapienz[ids.EXEC_TIME]
        time_sapienz.append(round(time_app_sapienz / 60)) # use min, not sec

        app_results_for_sapienz_div = app_results.get(ids.SAPIENZDIV)
        time_app_sapienz_div = app_results_for_sapienz_div[ids.EXEC_TIME]
        time_sapienz_div.append(round(time_app_sapienz_div / 60)) # use min, not sec

        if time_app_sapienz < time_app_sapienz_div:
            sapienz_wins = sapienz_wins + 1
        elif time_app_sapienz > time_app_sapienz_div:
            sapienz_div_wins = sapienz_div_wins + 1
        else:
            tie = tie + 1

    print("TIME (min):")
    print("SAPIENZ wins    : " + str(sapienz_wins))
    print("SAPIENZ DIV wins: " + str(sapienz_div_wins))
    print("TIE             : " + str(tie))
    print("SUM             : " + str(sapienz_wins + sapienz_div_wins + tie))

    times = [time_sapienz, time_sapienz_div]
    print(" -- Time SAPIENZ : " + str(time_sapienz))
    print(" -- -- mean   " + str(np.mean(time_sapienz)))
    print(" -- -- median " + str(np.median(time_sapienz)))
    print(" -- Time SAPIENZ DIV: " + str(time_sapienz_div))
    print(" -- -- mean   " + str(np.mean(time_sapienz_div)))
    print(" -- -- median " + str(np.median(time_sapienz_div)))
    names = ["SAPIENZ", "SAPIENZ DIV"]
    labels = range(1, 3)
    plt.rcParams["figure.figsize"] = [3, 2]
    fig, ax = plt.subplots()
    # plt.title(str(cars_number) + " cars")
    ax.boxplot(times, 0, '', positions=labels)
    for i in range(len(times)):
        ax.plot(labels[i], np.mean(times[i]), ".", label='mean', color='black', linestyle=':')
    plt.xticks(labels, names)
    plt.yticks([60,90,120,150,180])
    plt.ylabel('Time (min) (66 apps)')
    # show the plot
    fig.tight_layout()
    # fig.subplots_adjust(left=0.05, right=0.98, bottom=0.05, top=0.95, hspace=0.04, wspace=0.0)
    fig.savefig(file_path)
    #plt.show()


def crash_analysis(data):
    app_crashed_sapienz = 0
    app_crashed_sapienz_div = 0

    unique_crashes_sapienz = 0
    unique_crashes_sapienz_div = 0

    total_crashes_sapienz = 0
    total_crashes_sapienz_div = 0

    native_crashes_sapienz = 0
    native_crashes_sapienz_div = 0

    for app in sorted(data.keys(), key=lambda v: v.upper()):
        app_results = data[app]

        app_results_for_sapienz = app_results.get(ids.SAPIENZ)
        if app_results_for_sapienz[ids.UNIQUE_CRASHES] > 0:
            app_crashed_sapienz = app_crashed_sapienz + 1
        unique_crashes_sapienz = unique_crashes_sapienz + app_results_for_sapienz[ids.UNIQUE_CRASHES]
        total_crashes_sapienz = total_crashes_sapienz + app_results_for_sapienz[ids.TOTAL_CRASHES]
        native_crashes_sapienz = native_crashes_sapienz + app_results_for_sapienz[ids.NATIVE_CRASHES]

        app_results_for_sapienz_div = app_results.get(ids.SAPIENZDIV)
        if app_results_for_sapienz_div[ids.UNIQUE_CRASHES] > 0:
            app_crashed_sapienz_div = app_crashed_sapienz_div + 1
        unique_crashes_sapienz_div = unique_crashes_sapienz_div + app_results_for_sapienz_div[ids.UNIQUE_CRASHES]
        total_crashes_sapienz_div = total_crashes_sapienz_div + app_results_for_sapienz_div[ids.TOTAL_CRASHES]
        native_crashes_sapienz_div = native_crashes_sapienz_div + app_results_for_sapienz_div[ids.NATIVE_CRASHES]

    print("CRASHES:")
    print("# App Crashed SAPIENZ      : " + str(app_crashed_sapienz))
    print("# App Crashed SAPIENZDIV   : " + str(app_crashed_sapienz_div))
    print("# Unique Crashes SAPIENZ   : " + str(unique_crashes_sapienz))
    print("# Unique Crashes SAPIENZDIV: " + str(unique_crashes_sapienz_div))
    print("# Total Crashes SAPIENZ    : " + str(total_crashes_sapienz))
    print("# Total Crashes SAPIENZDIV : " + str(total_crashes_sapienz_div))
    print("# Excl. Crashes (native + EMMA) SAPIENZ    : " + str(native_crashes_sapienz))
    print("# Excl. Crashes (native + EMMA) SAPIENZDIV : " + str(native_crashes_sapienz_div))
    print("# Total - Excl. Crashes SAPIENZ    : " + str(total_crashes_sapienz - native_crashes_sapienz))
    print("# Total - Excl. Crashes SAPIENZDIV : " + str(total_crashes_sapienz_div - native_crashes_sapienz_div))


def compare_crashes(method1, method2, study):
    results_path_method1 = study + method1 + "/results/1"
    results_path_method2 = study + method2 + "/results/1"

    disjoint_crashes_method1 = []
    intersecting_crashes_method1 = []

    for folder_name in sorted(os.listdir(results_path_method1), key=lambda v: v.upper()):
        app_folder_path_method1 = results_path_method1 + "/" + folder_name
        app_folder_path_method2 = results_path_method2 + "/" + folder_name

        crashes_folder_path_method1 = app_folder_path_method1 + "/crashes/unique"
        crashes_folder_path_method2 = app_folder_path_method2 + "/crashes/unique"

        for file_name1 in sorted(os.listdir(crashes_folder_path_method1)):
            if file_name1.startswith("bugreport"):
                # bug report / crash found
                bugreport_file_name_method1 = file_name1
                bugreport_file_path_method1 = crashes_folder_path_method1 + "/" + bugreport_file_name_method1

                is_unique = True

                for file_name2 in sorted(os.listdir(crashes_folder_path_method2)):
                    if file_name2.startswith("bugreport"):
                        bugreport_file_name_method2 = file_name2
                        bugreport_file_path_method2 = crashes_folder_path_method2 + "/" + bugreport_file_name_method2

                        if bug_report_analysis.is_crash_redundant(bugreport_file_path_method1, bugreport_file_path_method2):
                            is_unique = False
                            #print("INTERSECTING: " + bugreport_file_path_method1 + "\nWITH        : " + bugreport_file_path_method2)
                            break

                if is_unique:
                    disjoint_crashes_method1.append(bugreport_file_path_method1)
                    #print("UNIQUE: " + bugreport_file_path_method1)
                else:
                    intersecting_crashes_method1.append(bugreport_file_path_method1)
        #print

    print("PAIRWISE CRASH COMPARISON: " + str(method1) + " vs " + str(method2))
    print(method1 + " # disjoint    : " + str(len(disjoint_crashes_method1)))
    print(method1 + " # intersecting: " + str(len(intersecting_crashes_method1)))
    print(method1 + " # SUM of both : " + str(len(disjoint_crashes_method1) + len(intersecting_crashes_method1)))


if __name__ == "__main__":
    study = "/home/tom/SSBSE19/study1/"
    with open(study + 'data.json') as f:
        data = json.load(f)

    # methods to analyze
    methods = [ids.SAPIENZ, ids.SAPIENZDIV]
    # methods = [ids.SAPIENZ, ids.RMDUPLICATES, ids.DIVINITPOP, ids.INCMOSTDIVERSE, ids.RERANDOM, ids.SAPIENZDIV]

    # properties to analyze
    properties = [ids.MAX_COVERAGE, ids.UNIQUE_CRASHES,
                  ids.AVG_MIN_LENGTH, ids.EXEC_TIME] # ids.GENERATION

    to_csv(data, methods, properties, study + "study1.csv")

    print
    plot_coverage(data, study + "coverage68.pdf")

    print
    crash_analysis(data)

    print
    plot_time(data, study + "time68.pdf")

    print
    compare_crashes(ids.SAPIENZ, ids.SAPIENZDIV, study)
    compare_crashes(ids.SAPIENZDIV, ids.SAPIENZ, study)