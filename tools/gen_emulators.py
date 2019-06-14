# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import os
import sys

if __name__ == "__main__":
    n_emu = int(sys.argv[1])
    template_name = 'api19'
    template_avd = "/root/.android/avd/" + template_name
    for i in range(1, n_emu):
        os.system("cp -r " + template_avd + ".avd" + " " + template_avd + "_" + str(i) + ".avd")

        with open(template_avd + "_" + str(i) + ".ini", "w") as ini_file:
            ini_file.write("avd.ini.encoding=UTF-8\n")
            ini_file.write("path=/root/.android/avd/" + template_name + "_" + str(i) + ".avd\n")
            ini_file.write("path.rel=avd/" + template_name + "_" + str(i) + ".avd\n")
            ini_file.write("target=android-19\n")
