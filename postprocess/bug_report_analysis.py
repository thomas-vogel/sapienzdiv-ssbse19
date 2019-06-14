# author: Thomas Vogel

import os
import numpy as np
import analysis_settings as ids
from difflib import SequenceMatcher
import difflib


DEBUG = False


def get_crashes_and_lengths(crashes_folder_path):
    """
    process one app
    :param crashes_folder_path: */crashes/
    :return: number of unique bug reports, a list of bug reports path
    """
    if DEBUG:
        print("Check path: " + str(crashes_folder_path))

    total_crash_count = 0
    unique_crash_count = 0
    redundant_crash_count = 0
    native_crash_count = 0
    unique_bug_reports = []
    all_tests_for_unique_crash = dict()

    # create folder for unique crashes (bug reports)
    unique_bug_reports_path = crashes_folder_path + "/unique"
    try:
        os.system("rm -rf " + unique_bug_reports_path)
        os.system("mkdir " + unique_bug_reports_path)
    except:
        pass

    # check all crashes
    for file_name in sorted(os.listdir(crashes_folder_path)):
        if file_name.startswith("bugreport"):
            # bug report / crash found
            bugreport_file_name = file_name
            bugreport_file_path = crashes_folder_path + "/" + bugreport_file_name
            # increase total count of crashes
            total_crash_count += 1

            # assume crash is unique
            is_unique = True

            # check whether crash is unique
            unique_bugreport = "N/A"
            for unique_bugreport_file_name in unique_bug_reports:
                # search existing crashes for a redundant crash

                if is_crash_redundant(bugreport_file_path, crashes_folder_path + "/" + unique_bugreport_file_name):
                    # bug reports differ only in 2 or less lines => redundant crash found
                    is_unique = False
                    redundant_crash_count += 1
                    # add test of the redundant crash to the tests of the unique crash
                    tests_for_unique_crash = all_tests_for_unique_crash[unique_bugreport_file_name]
                    tests_for_unique_crash.append(get_test_for_crash(bugreport_file_name))
                    unique_bugreport = unique_bugreport_file_name
                    break

            # check whether the crash is native
            native_crash = is_crash_native(bugreport_file_path)

            if is_unique:
                # skip native crashes
                if not native_crash:
                    unique_bug_reports.append(bugreport_file_name)
                    unique_crash_count += 1
                    # cp bug report
                    os.system("cp " + bugreport_file_path + " " + unique_bug_reports_path)
                    all_tests_for_unique_crash[bugreport_file_name] = [get_test_for_crash(bugreport_file_name)]
                else:
                    native_crash_count += 1
            if DEBUG:
                print(str(total_crash_count) + ". Bug report: " + bugreport_file_name
                      + "\tunique = " + str(is_unique)
                      + "\t(duplicate of " + unique_bugreport + ")"
                      + "\tnative crash = " + str(native_crash))

    if DEBUG:
        print "Number of crashes: " + str(total_crash_count)
        print "Number of unique crashes: " + str(unique_crash_count)
        print "Number of redundant crashes: " + str(redundant_crash_count)
        print "Number of native crashes: " + str(native_crash_count)
        print "Unique bug reports:\t\t" + ', '.join(map(str, unique_bug_reports))
        print "\nTests for unique bug reports: "
        for crash, tests in all_tests_for_unique_crash.items():
            print "-- " + str(crash) + ":\n---- " + ', '.join(map(str, tests))

    avg_length_of_all_fault_revealing_tests = 0
    avg_length_of_min_fault_revealing_tests = 0
    if DEBUG:
        print "\nLength of tests for crashes:"
    all_lengths = []
    min_lengths = []
    if unique_crash_count > 0:
        for unique_crash in all_tests_for_unique_crash.keys():
            tests_for_unique_crash = all_tests_for_unique_crash[unique_crash]
            lengths_for_crash = []

            for test in tests_for_unique_crash:
                length_of_test = file_len(crashes_folder_path + "/" + test) - 4
                lengths_for_crash.append(length_of_test)

            min_l_for_bug = np.min(lengths_for_crash)
            avg_l_for_bug = np.mean(lengths_for_crash)
            if DEBUG:
                print("Crash " + str(unique_crash)
                      + ": Min: " + str(min_l_for_bug)
                      + "\tAvg: " + str(avg_l_for_bug))

            all_lengths.extend(lengths_for_crash)
            min_lengths.append(min_l_for_bug)

        avg_length_of_all_fault_revealing_tests = np.mean(all_lengths)
        avg_length_of_min_fault_revealing_tests = np.mean(min_lengths)

        if DEBUG:
            print("Average length of all fault revealing tests:                          \t\t"
                  + str(avg_length_of_all_fault_revealing_tests) + "\t\t--data: " + str(all_lengths))
            print("Average length of fault revealing tests that are minimal for each bug:\t\t"
                  + str(avg_length_of_min_fault_revealing_tests) + "\t\t--data: " + str(min_lengths))

    return unique_crash_count, redundant_crash_count, native_crash_count, \
           avg_length_of_all_fault_revealing_tests, avg_length_of_min_fault_revealing_tests, \
           total_crash_count, \
           all_lengths, min_lengths


def get_test_for_crash(bug_report_file_name):
    suffix = bug_report_file_name.split("bugreport.")[1]
    return "script." + suffix


def file_len(fname):
    with open(fname) as f:
        return sum(1 for _ in f)


# return true if the stack traces are redundant/identical/similar to the other crash
def is_crash_redundant(bugreport_file_path, other_bugreport_file_path):
    if ids.UNIQUE_CRASH_IDENTIFICATION == ids.UNIQUE_CRASH_DIFF:
        if len(get_diff_lines(bugreport_file_path, other_bugreport_file_path)) <= (ids.DIFF_THRESHOLD * 2):
            # check that length differ only <= ids.DIFF_THRESHOLD lines
            return file_length_diff(bugreport_file_path, other_bugreport_file_path) <= ids.DIFF_THRESHOLD
        else:
            return False
    elif ids.UNIQUE_CRASH_IDENTIFICATION == ids.UNIQUE_CRASH_SIM:
        return similar_files(bugreport_file_path, other_bugreport_file_path)


def similar_files(bugreport_file_path, other_bugreport_file_path):
    with open(bugreport_file_path, 'r') as file1:
        with open(other_bugreport_file_path, 'r') as file2:
            bugreport_content = pre_process(file1)
            other_bugreport_content = pre_process(file2)
            similarity = similar_contents(bugreport_content, other_bugreport_content)
            print 'Sim: ' + str(similarity)
            if similarity > ids.SIM_THRESHOLD:
                return True
            else:
                return False


def similar_contents(bugreport_content, other_bugreport_content):
    return SequenceMatcher(None, bugreport_content, other_bugreport_content).ratio()


def file_length_diff(bugreport_file_path, other_bugreport_file_path):
    l_bugreport_file_path = file_len(bugreport_file_path)
    l_other_bugreport_file_path = file_len(other_bugreport_file_path)
    # print("" + str(l_bugreport_file_path) + " vs " + str(l_other_bugreport_file_path))
    return np.abs(file_len(bugreport_file_path) - file_len(other_bugreport_file_path))


# returns the lines of both files that are different.
# Thus, if the two files differ in one line,
# this line of each of the two files are in the result,
# hence, for one diff, two files are returned.
def get_diff_lines(file_path_1, file_path_2):
    with open(file_path_1, 'r') as file1:
        with open(file_path_2, 'r') as file2:
            content1 = pre_process(file1)
            content2 = pre_process(file2)
            diff_lines = set(content1).symmetric_difference(content2)

    diff_lines.discard('\n')
    return diff_lines


# removes the suffix starting wiht $1@ from a line as in
# com.angrydoughnuts.android.alarmclock.NotificationServiceBinder$1@b216e838.
# Result is com.angrydoughnuts.android.alarmclock.NotificationServiceBinder.
def pre_process(bug_report_file):
    lines = bug_report_file.readlines()
    # print lines
    for idx, line in enumerate(lines):
        #
        if '$1@' in line:
            splits = line.split("$1@")
            newline = splits[0]
            lines[idx] = newline

        # skip the pid number in the first line
        if idx == 0 and '(pid' in line:
            splits = line.split("(pid")
            newline = splits[0]
            lines[idx] = newline
    # print lines
    # print lines == lines
    return lines


def get_content(bugreport_file_path):
    with open(bugreport_file_path, 'r') as f:
        lines = f.readlines()
        return lines


def is_crash_native(bug_report_file_path):
    bug_report = open(bug_report_file_path, 'r')
    lines = bug_report.readlines()
    for line in lines:
        if line == "// Short Msg: Native crash\n":
            # print("NATIVE: " + str(bug_report_file_path))
            return True
        if "emma" in line:
            #print("emma $$$ " + line)
            return True
        if "Emma" in line:
            #print("Emma $$$ " + line)
            return True
    return False


def mydiff(bugreport_file_path, other_bugreport_file_path):
    with open(bugreport_file_path, 'r') as file1:
        with open(other_bugreport_file_path, 'r') as file2:
            content1 = pre_process(file1)
            content2 = pre_process(file2)
            d = difflib.Differ()
            #diff = d.compare(content1, content2)
            diff = difflib.unified_diff(content1, content2)
            print ''.join(diff)

