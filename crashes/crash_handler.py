# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import subprocess
import os


def handle(device, apk_dir, script_path, gen, pop, index, unique_crashes):
    """
	:param device:
	:param apk_dir:
	:param script_path:
	:param gen_str: string, "init" is caused when init,
		"0" is caused when evaluate the init population
	:return: True if it is a real crash
	"""

    p = subprocess.Popen("adb -s " + device + " shell ls /mnt/sdcard/bugreport.crash", stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    output, errors = p.communicate()
    if output.find("No such file or directory") != -1:
        # no crash
        pass
    else:
        # save the crash report
        os.system("adb -s " + device + " pull /mnt/sdcard/bugreport.crash " + apk_dir + "/")
        # filter duplicate crashes
        with open(apk_dir + "/bugreport.crash") as bug_report_file:
            content = ""
            for line_no, line in enumerate(bug_report_file):
                if line_no == 0:
                    # should not caused by android itself
                    if line.startswith("// CRASH: com.android."):
                        os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
                        return False
                    continue
                content += line
            if content in unique_crashes:
                os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
                return False
            else:
                unique_crashes.add(content)

        # ts = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.%f")[:-3]
        os.system("mv " + apk_dir + "/bugreport.crash " + apk_dir + "/crashes/" + "bugreport." + str(gen) + "." + str(
            pop) + "." + str(index))
        # save the script, indicate its ith gen
        os.system("cp " + script_path + " " + apk_dir + "/crashes/" + "script." + str(gen) + "." + str(pop) + "." + str(
            index))
        print "### Caught a crash."
        os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
        return True

    os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
    return False
