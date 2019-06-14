#!/bin/bash
# script to setup the environment to run Sapienz
# this script must run as root ("sudo su") otherwise it will not work

# check if is running root user
if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "Not running as root"
    exit
fi

# update package list
yes Y | apt install software-properties-common

# install java sdk
yes | add-apt-repository ppa:openjdk-r/ppa
apt update
yes | apt install openjdk-7-jre openjdk-7-jdk

# install android sdk
wget -O ~/android-sdk_r24.2-linux.tgz http://dl.google.com/android/android-sdk_r24.2-linux.tgz
tar -xvf ~/android-sdk_r24.2-linux.tgz -C ~/
yes | apt-get install lib32stdc++6 lib32z1

# set android env variables as root
echo 'ANDROID_HOME=$HOME/android-sdk-linux' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/emulator' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/tools' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/build-tools/19.1.0' >> ~/.bashrc
source ~/.bashrc

# install platform tools and sdk level 19
(while sleep 3; do echo "y"; done) | android update sdk -u -a -t 2,15,29,128,129,130,131

# create emulators (-c 512M is the size of the sd card so that the emulator will have an sdcard that is needed for EMMA)
echo "no" | android create avd -n api19 -t 'android-19' -c 512M --force --abi google_apis/x86
# copy emulators: parameter (10) is the number of duplicated emulators to be created.
echo "Copying emulators"
python tools/gen_emulators.py 10

yes | apt install libfreetype6-dev libxml2-dev libxslt1-dev python-dev

# install python dependencies for sapienz
yes | apt install python-pip python-tk
pip install --upgrade pip==9.0.3
pip install -r requirements.txt

# install tmux
yes | apt install tmux
# install pdfunite
yes | apt install poppler-utils

