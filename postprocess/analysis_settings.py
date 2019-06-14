# author: Thomas Vogel

# methods
SAPIENZ = "sapienz"
RMDUPLICATES = "rmduplicates"
DIVINITPOP = "divinitpop"
INCMOSTDIVERSE = "incmostdiverse"
RERANDOM = "rerandom"
SAPIENZDIV = "sapienzdiv"

# properties
GENERATION = "gen"
MAX_COVERAGE = "cov"
UNIQUE_CRASHES = "u_crashes"
REDUNDANT_CRASHES = "r_crashes"
NATIVE_CRASHES = "n_crashes"
TOTAL_CRASHES = "t_crashes"
AVG_LENGTH = "avg_length"
AVG_MIN_LENGTH = "avg_min_length"
EXEC_TIME = "exec_time"

# study 2
REPETITIONS = 20


# unique crash identification methods
UNIQUE_CRASH_SIM = "SIM"
UNIQUE_CRASH_DIFF = "DIFF"

# Using "SIM" the degree of similarity so that two crashes are not unique
SIM_THRESHOLD = 0.90
# Using "DIFF", the number of diffs for unique crash
DIFF_THRESHOLD = 3

# used method
UNIQUE_CRASH_IDENTIFICATION = UNIQUE_CRASH_DIFF




def get_short_app_name(app):
    if app == "a2dp.Vol_93_src":
        return "a2dp"
    elif app == "aarddict.android_13_src":
        return "aarddict"
    elif app == "aLogCat":
        return "aLogCat"
    elif app == "Amazed":
        return "Amazed"
    elif app == "AnyCut":
        return "AnyCut"
    elif app == "baterrydog":
        return "baterrydog"
    elif app == "be.ppareit.swiftp_free_21_src":
        return "swiftp"
    elif app == "Book-Catalogue":
        return "Book-Catalogue"
    elif app == "caldwell.ben.bites_4_src":
        return "bites"
    elif app == "ch.blinkenlights.battery_1335983644_src":
        return "battery"
    elif app == "com.addi_44_src":
        return "addi"
    elif app == "com.angrydoughnuts.android.alarmclock_8_src":
        return "alarmclock"
    elif app == "com.chmod0.manpages_3_src":
        return "manpages"
    elif app == "com.evancharlton.mileage_3110_src":
        return "mileage"
    elif app == "com.everysoft.autoanswer_6_src":
        return "autoanswer"
    elif app == "com.gluegadget.hndroid_3_src":
        return "hndroid"
    elif app == "com.hectorone.multismssender_13_src":
        return "multismssender"
    elif app == "com.irahul.worldclock_2_src":
        return "worldclock"
    elif app == "com.kvance.Nectroid_11_src":
        return "Nectroid"
    elif app == "com.morphoss.acal_60_src":
        return "acal"
    elif app == "com.teleca.jamendo_38_src":
        return "jamendo"
    elif app == "com.templaro.opsiz.aka_10_src":
        return "aka"
    elif app == "com.tum.yahtzee_1_src":
        return "yahtzee"
    elif app == "com.zoffcc.applications.aagtl_31_src":
        return "aagtl"
    elif app == "CountdownTimer":
        return "CountdownTimer"
    elif app == "cri.sanity_21100_src":
        return "sanity"
    elif app == "dalvik-explorer":
        return "dalvik-explorer"
    elif app == "de.homac.Mirrored_9_src":
        return "Mirrored"
    elif app == "dialer2":
        return "dialer2"
    elif app == "DivideAndConquer":
        return "DivideAndConquer"
    elif app == "fileexplorer":
        return "fileexplorer"
    elif app == "gestures":
        return "gestures"
    elif app == "hotdeath":
        return "hotdeath"
    elif app == "hu.vsza.adsdroid_2_src":
        return "adsdroid"
    elif app == "i4nc4mp.myLock_28_src":
        return "myLock"
    elif app == "in.shick.lockpatterngenerator_6_src":
        return "lockpatterngenerator"
    elif app == "jp.gr.java_conf.hatalab.mnv_40_src":
        return "mnv"
    elif app == "k9mail":
        return "k9mail"
    elif app == "LolcatBuilder":
        return "LolcatBuilder"
    elif app == "MunchLife":
        return "MunchLife"
    elif app == "MyExpenses":
        return "MyExpenses"
    elif app == "net.fercanet.LNM_3_src":
        return "LNM"
    elif app == "netcounter":
        return "netcounter"
    elif app == "org.beide.bomber_1_src":
        return "bomber"
    elif app == "org.liberty.android.fantastischmemo_135_src":
        return "fantastischmemo"
    elif app == "org.scoutant.blokish_13_src":
        return "blokish"
    elif app == "org.smerty.zooborns_14_src":
        return "zooborns"
    elif app == "org.waxworlds.edam.importcontacts_2_src":
        return "importcontacts"
    elif app == "org.wikipedia_17_src":
        return "wikipedia"
    elif app == "PasswordMakerProForAndroid":
        return "PasswordMaker"
    elif app == "passwordmanager":
        return "passwordmanager"
    elif app == "Photostream":
        return "Photostream"
    elif app == "QuickSettings":
        return "QuickSettings"
    elif app == "RandomMusicPlayer":
        return "RandomMusicPlayer"
    elif app == "Ringdroid":
        return "Ringdroid"
    elif app == "soundboard":
        return "soundboard"
    elif app == "SpriteMethodTest":
        return "SpriteMethodTest"
    elif app == "SpriteText":
        return "SpriteText"
    elif app == "SyncMyPix":
        return "SyncMyPix"
    elif app == "tippy_1.1.3":
        return "tippy"
    elif app == "tomdroid-src-0.5.0":
        return "tomdroid"
    elif app == "Translate":
        return "Translate"
    elif app == "Triangle":
        return "Triangle"
    elif app == "weight-chart":
        return "weight-chart"
    elif app == "whohasmystuff-1.0.7":
        return "whohasmystuff"
    elif app == "Wordpress_394":
        return "Wordpress"