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
            # os.system("kill -9 $(lsof -i:5037 | tail -n +2 | awk '{print $2}')")
            # os.system("adb devices")
            thread.join()
        print self.process.returncode


def cal_coverage(path, gen, pop):
    activities = set()
    for file_name in os.listdir(path):
        if file_name.startswith("activity.coverage." + str(gen) + "." + str(pop) + "."):
            file_path = path + file_name
            file_coverage = open(file_path)
            for line in file_coverage:
                activities.add(line.strip())
            file_coverage.close()

    return 10.0 * len(activities)


# return accumulative coverage and average length
def get_suite_coverage(scripts, device, apk_dir, package_name, gen, pop):
    unique_crashes = set()

    # clean states
    os.system("adb -s " + device + " shell am force-stop " + package_name)
    os.system("adb -s " + device + " shell pm clear " + package_name)
    # os.system("rm " + apk_dir + "/intermediate/activity.coverage.*")

    # run scripts
    for index, script in enumerate(scripts):
        start_target = "adb -s " + device + " shell motifcore -p " + package_name + " -c android.intent.category.LAUNCHER 1"
        os.system(start_target)

        os.system("adb -s " + device + " push " + script + " /mnt/sdcard/")
        script_name = script.split("/")[-1]

        # command = Command("adb -s " + device + " shell motifcore -p " + package_name + " --bugreport --throttle " + str(
        # 	settings.THROTTLE) + " -f /mnt/sdcard/" + script_name + " 1")
        # command = Command("adb -s " + device + " shell motifcore -p " + package_name + " --bugreport " + "-f /mnt/sdcard/" + script_name + " 1")
        # command.run(timeout=600)
        cmd = "adb -s " + device + " shell motifcore -p " + package_name + " --bugreport --string-seeding /mnt/sdcard/" + package_name + "_strings.xml" + " -f /mnt/sdcard/" + script_name + " 1"
        os.system(settings.TIMEOUT_CMD + " " + str(settings.EVAL_TIMEOUT) + " " + cmd)
        # need to manually kill motifcore when timeout
        kill_motifcore_cmd = "shell ps | awk '/com\.android\.commands\.motifcore/ { system(\"adb -s " + device + " shell kill \" $2) }'"
        os.system("adb -s " + device + " " + kill_motifcore_cmd)

        os.system(
            "adb -s " + device + " pull /sdcard/activity.coverage " + apk_dir + "/coverages/activity.coverage." + str(
                gen) + "." + str(pop) + "." + str(index))

        crash_handler.handle(device, apk_dir, script, gen, pop, index, unique_crashes)

        # close app
        os.system("adb -s " + device + " shell pm clear " + package_name)
        os.system("adb -s " + device + " shell am force-stop " + package_name)

    coverage = cal_coverage(apk_dir + "/coverages/", gen, pop)

    # print "\n\n\n### get_suite_coverage: Coverage, num crashes =", coverage, ",", len(unique_crashes)

    return coverage, len(unique_crashes)
