# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import os, sys, shutil, datetime, time
from lxml import html
from bs4 import UnicodeDammit
import settings
import subprocess, threading
from crashes import crash_handler


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print '... Evaluate Script Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print '... Evaluate Script Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print self.process.returncode


def cal_coverage(coverage_file, covids_file):
    print "before open"
    ec_reader = open(coverage_file)
    em_reader = open(covids_file)
    print "after open"

    covered = set()
    total = 0

    for line in em_reader:
        if line.strip() != "":
            total += 1

    for line in ec_reader:
        line = line.strip()
        if line != "":
            covered.add(line)

    print "return coverage:", 100.0 * len(covered) / total
    return 100.0 * len(covered) / total


# return accumulative coverage and average length
def get_ella_suite_coverage(scripts, device, apk_dir, package_name, gen):
    num_crashes = 0
    std_out_file = apk_dir + "/intermediate/" + "output.stdout"

    # clean states
    os.system("adb -s " + device + " shell am force-stop " + package_name)
    os.system("adb -s " + device + " shell pm clear " + package_name)
    os.system("rm " + apk_dir + "/coverage.dat*")

    # run scripts
    for index, script in enumerate(scripts):
        start_target = "adb -s " + device + " shell motifcore -p " + package_name + " -c android.intent.category.LAUNCHER 1"
        os.system(start_target + " > " + std_out_file)
        # p = subprocess.Popen(start_target, shell=True, stdout=subprocess.PIPE).communicate()[0]

        os.system("adb -s " + device + " push " + script + " /mnt/sdcard/" + " > " + std_out_file)
        script_name = script.split("/")[-1]
        # start motifcore replay
        # add timeout
        command = Command("adb -s " + device + " shell motifcore -p " + package_name + " --bugreport --throttle " + str(
            settings.THROTTLE) + " -f /mnt/sdcard/" + script_name + " 1")
        command.run(timeout=600)
        # print "... Start evaluating a script"
        # p = subprocess.Popen("adb -s " + settings.DEVICE + " shell motifcore -p " + package_name + " --throttle " + str(settings.THROTTLE) + " -f /mnt/sdcard/" + script_name + " 1", shell=True, stdout=subprocess.PIPE).communicate()[0]
        # os.system("adb -s " + device + " shell motifcore -p " + package_name + " --bugreport --throttle " + str(settings.THROTTLE) + " -f /mnt/sdcard/" + script_name + " 1" + " > " + std_out_file)
        # print "... Finished evaluating a script"

        # TODO: handle the bugreport: save to db together with generation info and the script
        if crash_handler.handle(device, apk_dir, script):
            num_crashes += 1

        # close app
        os.system("adb -s " + device + " shell pm clear " + package_name + " > " + std_out_file)
        os.system("adb -s " + device + " shell am force-stop " + package_name + " > " + std_out_file)

    coverage_file = ''
    covids_file = apk_dir + "/covids"
    coverage_file_count = 0
    for file_name in os.listdir(apk_dir):
        if file_name.startswith("coverage.dat"):
            coverage_file_count += 1
            coverage_file = apk_dir + "/" + file_name

    assert coverage_file_count == 1

    coverage = cal_coverage(coverage_file, covids_file)
    return coverage, num_crashes
