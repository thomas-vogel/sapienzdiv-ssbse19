from enum import Enum
import os

class AndroidKey(Enum):
    MENU = 1
    HOME = 3
    BACK = 4
    DPAD_UP = 19
    DPAD_DOWN = 20
    DPAD_LEFT = 21
    DPAD_RIGHT = 22
    DPAD_CENTER = 23
    VOLUME_UP = 24
    VOLUME_DOWN = 25
    POWER = 26
    CAMERA = 27
    CLEAR = 28
    COMMA = 55
    PERIOD = 56
    ALT_LEFT = 57
    ALT_RIGHT = 58
    SHIFT_LEFT = 59
    SHIFT_RIGHT = 60
    TAB = 61
    SPACE = 62
    ENTER = 66
    DEL = 67
    FOCUS = 80
    NOTIFICATION = 83
    SEARCH = 84


device = ""


def send_click(x, y):
    print "Click at {} / {}".format(x, y)
    click_cmd = "input tap {} {}".format(x, y)
    execute_shell_cmd(click_cmd)


def send_text(text):
    send_text_cmd = "input text {}".format(text)
    execute_shell_cmd(send_text_cmd)


def sendKey(keycode):
    key_cmd = "input keyevent {}".format(keycode.value)
    execute_shell_cmd(key_cmd)


def send_swipe(down_x, down_y, up_x, up_y):
    print "Swipe from {} / {} to {} {}".format(down_x, down_y, up_x, up_y)
    swipe_cmd = "input swipe {} {} {} {}".format(down_x, down_y, up_x, up_y)
    execute_shell_cmd(swipe_cmd)


def execute_shell_cmd(cmd):
    if device != "":
        cmd = "adb -s " + device + " shell " + cmd
    else:
        cmd = "adb shell " + cmd
    os.system(cmd)
