# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import os
import time

import subprocess as sub

import settings
from util import motifcore_installer
from util import pack_and_deploy

LG_G2 = '0988484c6013b082'


def get_all_available_emulators():
    """:returns list of all emulators"""
    ret = []
    p = sub.Popen('emulator -list-avds', stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    output, errors = p.communicate()
    segs = output.split("\n")
    for seg in segs:
        device = seg.strip()
        if device != '':
            ret.append(device)

    return ret


def get_devices():
    """ will also get devices ready
	:return: a list of avaiable devices names, e.g., emulator-5556
	"""
    ret = []
    p = sub.Popen('adb devices', stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    output, errors = p.communicate()
    print output
    segs = output.split("\n")
    for seg in segs:
        device = seg.split("\t")[0].strip()
        if device == LG_G2:
            ret.append(device)
        if device.startswith("emulator-") or device.startswith('192.168.'):
            p = sub.Popen('adb -s ' + device + ' shell getprop init.svc.bootanim', stdout=sub.PIPE, stderr=sub.PIPE,
                          shell=True)
            output, errors = p.communicate()
            print "found emulator:", device
            if output.strip() != "stopped":
                time.sleep(10)
                print "waiting for the emulator:", device
                return get_devices()
            else:
                ret.append(device)

    return ret


def find_between_r(s, first, last):
    try:
        start = s.rindex(first) + len(first)
        end = s.rindex(last, start)
        return s[start:end]
    except ValueError:
        return ""


def get_genymotion_device_ids():
    p = sub.Popen('vboxmanage list vms', stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    output, errors = p.communicate()
    segs = output.split("\n")
    ret = []
    for seg in segs:
        seg = seg.strip()
        device_id = find_between_r(seg, '{', '}')
        print "device id: " + device_id
        ret.append(device_id)
    assert len(ret) > 0
    return ret


def device_running(device_id):
    p = sub.Popen('vboxmanage showvminfo ' + device_id + ' | grep -c "running (since"', stdout=sub.PIPE,
                  stderr=sub.PIPE, shell=True)
    output, errors = p.communicate()
    status = output.strip()
    return status == '1'


def devices_running():
    count = 0
    for device_id in get_genymotion_device_ids():
        if not device_id == '':
            if device_running(device_id):
                count += 1
    print "Devices running: " + str(count)
    return count


def clear_zombie_emulators():
    os.system("adb kill-server")
    time.sleep(2)


def boot_genymotion_devices():
    clear_zombie_emulators()
    for i in range(settings.DEVICE_NUM - devices_running()):
        for device_id in get_genymotion_device_ids():
            if not device_id == '' and not device_running(device_id):
                print "booting genymotion emulator: " + device_id
                sub.Popen(settings.GENYMOTION_HOME + "player --vm-name " + device_id, stdout=sub.PIPE, stderr=sub.PIPE,
                          shell=True)
                time.sleep(2)
                break
    print "Waiting", settings.AVD_BOOT_DELAY, "seconds"
    time.sleep(settings.AVD_BOOT_DELAY)


def shutdown_genymotion_devices():
    os.system("pkill player")
    os.system("pkill VBoxHeadless")
    os.system("adb kill-server")


def boot_devices(wipe_data=False):
    """
	prepare the env of the device
	:return:
	"""
    # for i in range(1, settings.DEVICE_NUM):
    if len(get_devices()) >= settings.DEVICE_NUM:
        print "enough devices running"
        return
    count = 0
    for device_name in get_all_available_emulators():
        # device_name = settings.AVD_NAME + '_' + str(i)
        if count == settings.DEVICE_NUM:
            break
        print "Booting Device:", device_name
        time.sleep(0.3)

#        options = ' -writable-system'
	options = ''
        if wipe_data:
            options += ' -wipe-data'
        if settings.HEADLESS:
            options += ' -no-window'
	cmd = 'emulator -avd ' + device_name + options
	print 'Boot command:' + cmd
        sub.Popen('emulator -avd ' + device_name + options,
                      stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        count += 1
    while len(get_devices()) != settings.DEVICE_NUM:
        print "Waiting for devices to finish booting"
        time.sleep(10)


def clean_sdcard():
    for device in get_devices():
        os.system("adb -s " + device + " shell mount -o rw,remount rootfs /")
        os.system("adb -s " + device + " shell chmod 777 /mnt/sdcard")

        os.system("adb -s " + device + " shell rm -rf /mnt/sdcard/*")


def prepare_motifcore():
    for device in get_devices():
        motifcore_installer.install(settings.WORKING_DIR + "lib/motifcore.jar",
                                    settings.WORKING_DIR + "resources/motifcore", device)


def pack_and_deploy_aut():
    # instrument the app under test
    pack_and_deploy.main(get_devices())


def destroy_devices():
    for device in get_devices():
        os.system("adb -s " + device + " emu kill")
    # do: force kill
    os.system("kill -9  $(ps aux | grep 'emulator' | awk '{print $2}')")


if __name__ == "__main__":
    destroy_devices()
