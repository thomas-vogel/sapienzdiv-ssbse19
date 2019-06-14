# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import os


def install(motifcore_path, motifcore_script_path, device):
    print "installing motifcore"
    # obtain write permission
    os.system("adb -s " + device + " shell mount -o rw,remount /system")

    # push
    os.system("adb -s " + device + " push " + motifcore_path + " /system/framework")
    os.system("adb -s " + device + " push " + motifcore_script_path + " /system/bin")


# recover permission
# os.system("adb -s " + device + " shell mount -o ro,remount /system")


if __name__ == "__main__":
    os.chdir("..")
    install("lib/motifcore.jar", "resources/motifcore", "emulator-5554")
