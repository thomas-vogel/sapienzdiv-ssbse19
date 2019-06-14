# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import os

app_dir = ""
target_dir = ""

for dir_name in os.listdir(app_dir):
    crash_path = app_dir + "/" + dir_name + "/crashes"
    if os.path.isdir(crash_path):
        for file_name in os.listdir(crash_path):
            if file_name.find(".bugreport") != -1 or file_name.find(".script") != -1:
                file_path = crash_path + "/" + file_name
                print file_path
                print "cp " + file_path + " " + target_dir + "/" + dir_name + "^" + file_name
                os.system("cp " + file_path + " " + target_dir + "/" + dir_name + "^" + file_name)
