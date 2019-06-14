# Copyright (c) 2016-present, Ke Mao. All rights reserved


import multiprocessing as mp
import time

from devices import emulator, real_device
import settings

# global results for mp callback
results = []
idle_devices = []


def process_results(data):
    individual, device = data
    results.append(individual)
    idle_devices.append(device)


def initPopulation(container, func, n, apk_dir, package_name):
    """Call the function *container* with a generator function corresponding
	to the calling *n* times the function *func*.
	"""
    # init global states

    if settings.DEBUG:
        print "### Init population in parallel"
        print "n=", n
    ret = []
    while len(results) > 0:
        results.pop()
    while len(idle_devices) > 0:
        idle_devices.pop()

    # 1. get idle devices
    if settings.USE_REAL_DEVICE:
        idle_devices.extend(real_device.get_devices())
    else:
        idle_devices.extend(emulator.get_devices())

    # 2. assign tasks to devices
    pool = mp.Pool(processes=len(idle_devices))
    for i in range(0, n):
        while len(idle_devices) == 0:
            time.sleep(0.1)
        if settings.DEBUG:
            print "### Call apply_async"
        pool.apply_async(func, args=(idle_devices.pop(0), apk_dir, package_name), callback=process_results)

    # should wait for all processes finish
    pool.close()
    pool.join()
    ret.extend(results)

    return ret
