import platform
from os.path import expanduser


def is_mac_os():
    return platform.system() == "Darwin"

HOME_DIR = expanduser("~")

# === Env. Paths ===
# path should end with a '/'
# the path of sapienz folder
WORKING_DIR = HOME_DIR + '/sapienz-div/'

if is_mac_os():
    ANDROID_HOME = HOME_DIR + '/Library/Android/sdk/'
    GENYMOTION_HOME = '/Applications/Genymotion.app/Contents/MacOS/'
else:
    ANDROID_HOME = HOME_DIR + '/android-sdk-linux/'
    GENYMOTION_HOME = '/home/ubuntu/genymotion/'

DEBUG = False
# if False, "0" will be used
ENABLE_STRING_SEEDING = False
# use headless evaluator
HEADLESS = True

USE_REAL_DEVICE = False

# === Emulator ===
DEVICE_NUM = 10
AVD_BOOT_DELAY = 100
AVD_SERIES = "emulator"
AVD_NAME="Nexus_4_API_19"
EVAL_TIMEOUT = 120
# if run on Mac OS, use "gtimeout"
TIMEOUT_CMD = "timeout"

    
# === GA parameters ===
SEQUENCE_LENGTH_MIN = 20
SEQUENCE_LENGTH_MAX = 500 # default 500
SUITE_SIZE = 5 # min = 3
POPULATION_SIZE = 50
OFFSPRING_SIZE = 50
GENERATION = 10
# Crossover probability
CXPB = 0.7
# Mutation probability
MUTPB = 0.3

# Custom options
RE_RANDOMIZE = True
DIVERSITY_THRESHOLD = 0.5
INCLUDE_MOST_DIVERSE = True
PROPORTION_DIVERSE_IND = 0.3
DIVERSE_INITIAL_POP = True
REMOVE_DUPLICATES = True

# do or do not resume runs
IGNORE_INTERRUPTED_RUNS = True

# === For connectedness metric
MAX_DISTANCE = SEQUENCE_LENGTH_MAX * SUITE_SIZE
# MAX_EDGE_WEIGHTS = [300, 200, 100]
MAX_EDGE_WEIGHTS = [300]

# === Only for main_multi ===
# start from the ith apk
APK_OFFSET = 0
APK_DIR = HOME_DIR + '/subjects/'
REPEATED_RESULTS_DIR = HOME_DIR + '/results/'
REPEATED_RUNS = 1


# === MOTIFCORE script ===
# for initial population
MOTIFCORE_SCRIPT_PATH = '/mnt/sdcard/motifcore.script'
# header for evolved scripts
MOTIFCORE_SCRIPT_HEADER = 'type= raw events\ncount= -1\nspeed= 1.0\nstart data >>\n'
