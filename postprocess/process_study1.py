# author: Thomas Vogel

import os
import json

import logbook_analysis
import bug_report_analysis
import time_analysis
import analysis_settings as ids
import numpy as np


data = dict()


def analyze_method_on_apps(method, study):
    results_path = get_results_path(method, study)
    print("\nMethod : " + method)
    print("Results: " + results_path)

    length_of_all_fault_revealing_sequences_all_apps = []
    min_length_of_all_fault_revealing_sequences_all_apps = []

    for folder_name in sorted(os.listdir(results_path), key=lambda v: v.upper()):
        app_folder_path = results_path + "/" + folder_name
        print("App: " + str(folder_name) + " (" + str(app_folder_path) + ")")
        if not os.path.isdir(app_folder_path):
            continue

        # get number of generations and max coverage
        gen, max_coverage = logbook_analysis.get_gen_and_max_coverage(app_folder_path)

        # get crash infos and length of test sequences
        crashes_folder_path = app_folder_path + "/crashes"
        if not os.path.isdir(crashes_folder_path):
            continue

        crash_info = bug_report_analysis.get_crashes_and_lengths(crashes_folder_path)
        unique_crash_count = crash_info[0]
        redundant_crash_count = crash_info[1]
        native_crash_count = crash_info[2]
        avg_length_of_all_fault_revealing_tests = crash_info[3]
        avg_length_of_min_fault_revealing_tests = crash_info[4]
        total_crash_count = crash_info[5]

        length_of_all_fault_revealing_sequences = crash_info[6]
        length_of_all_fault_revealing_sequences_all_apps.extend(length_of_all_fault_revealing_sequences)
        min_length_of_all_fault_revealing_sequences = crash_info[7]
        min_length_of_all_fault_revealing_sequences_all_apps.extend(min_length_of_all_fault_revealing_sequences)

        # get execution time
        exec_time = time_analysis.get_duration(app_folder_path)

        # store results in dictionary
        app_entry = data.get(folder_name)
        if app_entry is None:
            app_entry = dict()
            data[folder_name] = app_entry
        method_entry = app_entry.get(method)
        if method_entry is None:
            method_entry = dict()
            app_entry[method] = method_entry
        else:
            print("Method processed twice for the app.")

        method_entry[ids.GENERATION] = gen
        method_entry[ids.MAX_COVERAGE] = max_coverage
        method_entry[ids.UNIQUE_CRASHES] = unique_crash_count
        method_entry[ids.REDUNDANT_CRASHES] = redundant_crash_count
        method_entry[ids.NATIVE_CRASHES] = native_crash_count
        method_entry[ids.AVG_LENGTH] = round(avg_length_of_all_fault_revealing_tests)
        method_entry[ids.AVG_MIN_LENGTH] = round(avg_length_of_min_fault_revealing_tests)
        method_entry[ids.TOTAL_CRASHES] = total_crash_count
        method_entry[ids.EXEC_TIME] = exec_time

    print("FAULT REVEALING SEQUENCE LENGTH OVER ALL APPS FOR " + str(method))
    print("AVERAGE OF ALL SEQUENCES = " + str(np.mean(length_of_all_fault_revealing_sequences_all_apps)))
    print("AVERAGE OF MIN SEQUENCES = " + str(np.mean(min_length_of_all_fault_revealing_sequences_all_apps)))


def get_results_path(method, study):
    return study + method + "/results/1"


if __name__ == "__main__":
    study = "/home/tom/SSBSE19/study1/"
    analyze_method_on_apps(ids.SAPIENZDIV, study)
    analyze_method_on_apps(ids.SAPIENZ, study)

    print data
    with open(study + 'data.json', 'w') as fp:
        json.dump(data, fp)

