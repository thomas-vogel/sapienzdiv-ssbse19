# Copyright (c) 2016-present, Ke Mao. All rights reserved.
# Extended by Thomas Vogel


import os
import time
import datetime
from timeit import default_timer as timer

import settings


if __name__ == "__main__":
    """
	For batch processing APKs. One hour per APK
	All intermediate output are saved under the instrumented app folder
	"""
    start = 1
    for i in range(start, settings.REPEATED_RUNS + start):

        instrumented_app_dirs = []
        apk_path = settings.APK_DIR

        ith_apk = 0

        for dir in os.listdir(apk_path):
            dir_path = apk_path + dir
            if os.path.isdir(dir_path):
                target_dir = settings.REPEATED_RESULTS_DIR + "/" + str(i) + "/" + dir_path.split("/")[-1]
                if ith_apk >= settings.APK_OFFSET and (not os.path.exists(target_dir)):
                    instrumented_app_dirs.append(dir_path)
                ith_apk += 1

        print "Will work on apps:", instrumented_app_dirs

        for app_dir in instrumented_app_dirs:
            start_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            start = timer()

            os.system("python main.py " + app_dir)

            end = timer()
            os.system("touch " + app_dir + "/intermediate/started_at_" + start_date)
            os.system("touch " + app_dir + "/intermediate/finished_at_" + datetime.datetime.now().strftime(
                "%Y_%m_%d_%H_%M_%S"))

            duration = end - start
            print(str(settings.GENERATION) + " generations reached after " + str(duration) + " seconds. Will work on next app ...")

            dur_file = open(app_dir + "/intermediate/duration.txt", "w")
            dur_file.write(str(duration))
            dur_file.close()

            time.sleep(10)

            target_dir = settings.REPEATED_RESULTS_DIR + "/" + str(i) + "/" + app_dir.split("/")[-1]
            os.system("mkdir -p " + target_dir)
            os.system("cp -r " + app_dir + "/intermediate " + target_dir)
            os.system("cp -r " + app_dir + "/crashes " + target_dir)
            os.system("cp -r " + app_dir + "/coverages " + target_dir)

    print "### All Done."
