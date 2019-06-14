# author: Thomas Vogel

import os
import json

import logbook_analysis
import bug_report_analysis
import analysis_settings as ids
import time_analysis


data = dict()
properties = [ids.GENERATION, ids.EXEC_TIME,
              ids.MAX_COVERAGE, ids.UNIQUE_CRASHES,
              ids.REDUNDANT_CRASHES, ids.NATIVE_CRASHES,
              ids.AVG_LENGTH, ids.AVG_MIN_LENGTH]


def analyze_method_on_apps(method, study):
    results_path = get_results_path(method, study)
    print("\nMethod : " + method)
    print("Results: " + results_path)

    # iterate over all runs
    runs = int(ids.REPETITIONS)
    for run in range(1, runs+1):
        results_path_run = results_path + "/" + str(run)
        # iterate over all apps of each run
        for folder_name in sorted(os.listdir(results_path_run), key=lambda v: v.upper()):
            app_folder_path = results_path_run + "/" + folder_name
            print("App: " + str(folder_name) + " (" + str(app_folder_path) + ")")
            if not os.path.isdir(app_folder_path):
                continue

            # get number of generations and max coverage
            gen, max_coverage = logbook_analysis.get_gen_and_max_coverage(app_folder_path)
            if gen == 0:
                print("Run " + str(run) + " of app " + str(folder_name)
                      + " produced no generation.")

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

            for property in properties:
                property_entry = method_entry.get(property)
                if property_entry is None:
                    property_entry = []
                    method_entry[property] = property_entry

                if property == ids.GENERATION:
                    property_value = gen
                elif property == ids.EXEC_TIME:
                    property_value = exec_time
                elif property == ids.MAX_COVERAGE:
                    property_value = max_coverage
                elif property == ids.UNIQUE_CRASHES:
                    property_value = unique_crash_count
                elif property == ids.REDUNDANT_CRASHES:
                    property_value = redundant_crash_count
                elif property == ids.NATIVE_CRASHES:
                    property_value = native_crash_count
                elif property == ids.AVG_LENGTH:
                    property_value = round(avg_length_of_all_fault_revealing_tests)
                elif property == ids.AVG_MIN_LENGTH:
                    property_value = round(avg_length_of_min_fault_revealing_tests)

                property_entry.append(property_value)


def get_results_path(method, study):
    return study + method + "/results"


if __name__ == "__main__":
    study = "/home/tom/SSBSE19/study2/"
    analyze_method_on_apps(ids.SAPIENZDIV, study)
    analyze_method_on_apps(ids.SAPIENZ, study)

    print data
    with open(study + 'data.json', 'w') as fp:
        json.dump(data, fp)

