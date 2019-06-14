# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import os
import settings


def decode_apk(input_apk, output_dir):
    os.chdir(output_dir)
    os.system("java -jar " + settings.WORKING_DIR + "lib/apktool.jar d -f " + input_apk)


def upload_string_xml(device, decoded_dir, package_name):
    string_xml_path = decoded_dir + "/res/values/strings.xml"
    if settings.ENABLE_STRING_SEEDING is False or os.path.exists(string_xml_path) is False:
        # if not exist, upload dummy strings.xml
        string_xml_path = settings.WORKING_DIR + "resources/dummy_strings.xml"
    os.system("adb -s " + device + " shell rm /mnt/sdcard/" + package_name + "_strings.xml")
    os.system("adb -s " + device + " push " + string_xml_path + " /mnt/sdcard/" + package_name + "_strings.xml")
