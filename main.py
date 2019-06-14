# Copyright (c) 2016-present, Ke Mao. All rights reserved.

import datetime
import os
import pickle
import platform
import random
import subprocess
import sys
import time

import networkx as nx
import numpy
from deap import creator, base, tools

import settings
from algorithms import eaMuPlusLambdaParallel
from analysers import static_analyser
from coverages import act_coverage
from coverages import emma_coverage
from crashes import crash_handler
from devices import emulator, real_device
from init import initRepeatParallel
from metrics import connectedness_metrics as cm
from metrics import population_metrics as pm
from plot import two_d_line
from util import adb_shell
from util.adb_shell import AndroidKey


class CanNotInitSeqException(Exception):
    pass


# get one test suite by running multiple times of MotifCore
def get_suite(device, apk_dir, package_name):
    ret = []
    unique_crashes = set()
    for i in range(0, settings.SUITE_SIZE):
        # get_sequence may return empty sequence
        seq = []
        repeated = 0
        while len(seq) <= 2:
            seq = get_sequence(device, apk_dir, package_name, i, unique_crashes)
            repeated += 1
            if repeated > 20:
                raise CanNotInitSeqException("Cannot get sequence via MotifCore.")
        ret.append(seq)

    return ret


### helper functions
# get one event sequence by running revised motifcore
# note: the launch activity is started by emma instrument
def get_sequence(device, apk_dir, package_name, index, unique_crashes):
    std_out_file = apk_dir + "/intermediate/" + "output.stdout"
    random.seed()

    motifcore_events = random.randint(settings.SEQUENCE_LENGTH_MIN, settings.SEQUENCE_LENGTH_MAX)

    ret = []

    # clear data
    # os.system("adb -s " + device + " shell pm clear " + package_name)

    # start motifcore
    print "... Start generating a sequence"
    # command = Command("adb -s " + device + " shell motifcore -p " + package_name + " -v --throttle " + str(
    # 	settings.THROTTLE) + " " + str(motifcore_events))
    # command.run(timeout=600)
    cmd = "adb -s " + device + " shell motifcore -p " + package_name + " --ignore-crashes --ignore-security-exceptions --ignore-timeouts --bugreport --string-seeding /mnt/sdcard/" + package_name + "_strings.xml -v " + str(
        motifcore_events)
    os.system(settings.TIMEOUT_CMD + " " + str(settings.EVAL_TIMEOUT) + " " + cmd)
    # need to kill motifcore when timeout
    kill_motifcore_cmd = "shell ps | awk '/com\.android\.commands\.motifcore/ { system(\"adb -s " + device + " shell kill \" $2) }'"
    os.system("adb -s " + device + " " + kill_motifcore_cmd)

    print "... Finish generating a sequence"
    # access the generated script, should ignore the first launch activity
    script_name = settings.MOTIFCORE_SCRIPT_PATH.split("/")[-1]
    ts = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.%f")[:-3]
    os.system(
        "adb -s " + device + " pull " + settings.MOTIFCORE_SCRIPT_PATH + " " + apk_dir + "/intermediate/" + script_name + ".init." + ts + "." + str(
            index))
    script = open(apk_dir + "/intermediate/" + script_name + ".init." + ts + "." + str(index))
    is_content = False
    is_skipped_first = False
    for line in script:
        line = line.strip()
        if line.find("start data >>") != -1:
            is_content = True
            continue
        if is_content and line != "":
            if is_skipped_first == False:
                is_skipped_first = True
                continue
            if is_skipped_first:
                ret.append(line)

    script.close()

    # deal with crash
    crash_handler.handle(device, apk_dir, apk_dir + "/intermediate/" + script_name + ".init." + ts + "." + str(index),
                         "init", ts, index, unique_crashes)

    return ret


# generate individual by running motifcore
def generate_individual(device, apk_dir, package_name):
    if settings.DEBUG:
        print "Generate Individual on device, ", device
    suite = get_suite(device, apk_dir, package_name)
    return creator.Individual(suite), device


# the suite coverage is accumulated
def evaluate_suite(individual, device, apk_dir, package_name, gen, pop):
    # for get_motifcore_suite_coverage
    script_path = []

    # for length objective
    suite_lengths = []
    for index, seq in enumerate(individual):
        # generate script file list
        script = open(apk_dir + "/intermediate/motifcore.evo.script." + str(gen) + "." + str(pop) + "." + str(index),
                      "w")
        script.write(settings.MOTIFCORE_SCRIPT_HEADER)

        length = 0
        for line in seq:
            script.write(line + "\n")
            length += 1

        suite_lengths.append(length)

        script.close()
        script_path.append(os.path.abspath(
            apk_dir + "/intermediate/motifcore.evo.script." + str(gen) + "." + str(pop) + "." + str(index)))

    # give a script and package, return the coverage by running all seqs
    # TODO: FIX ME
    if ".apk_output" in apk_dir:
        coverage, num_crashes = act_coverage.get_suite_coverage(script_path, device, apk_dir, package_name, gen, pop)
    else:
        coverage, num_crashes = emma_coverage.get_suite_coverage(script_path, device, apk_dir, package_name, gen, pop)
    print "### Coverage = ", coverage
    print "### Lengths = ", suite_lengths
    print "### #Crashes = ", num_crashes

    # 1st obj: coverage, 2nd: average seq length of the suite, 3nd: #crashes
    return pop, (coverage, numpy.mean(suite_lengths), num_crashes), device


def mut_suite(individual, indpb):
    # shuffle seq
    individual, = tools.mutShuffleIndexes(individual, indpb)

    # crossover inside the suite
    for i in range(1, len(individual), 2):
        if random.random() < settings.MUTPB:
            if len(individual[i - 1]) <= 2:
                print "\n\n### Indi Length =", len(individual[i - 1]), " ith = ", i - 1, individual[i - 1]
                continue  # sys.exit(1)
            if len(individual[i]) <= 2:
                print "\n\n### Indi Length =", len(individual[i]), "ith = ", i, individual[i]
                continue  # sys.exit(1)

            individual[i - 1], individual[i] = tools.cxOnePoint(individual[i - 1], individual[i])
            # individual[i - 1], individual[i] = tools.cxUniform(individual[i - 1], individual[i], indpb=0.5)

    # shuffle events
    for i in range(len(individual)):
        if random.random() < settings.MUTPB:
            if len(individual[i]) <= 2:
                print "\n\n### Indi Length =", len(individual[i]), "ith = ", i, individual[i]
                continue  # sys.exit(1)
            individual[i], = tools.mutShuffleIndexes(individual[i], indpb)

    return individual,


def select_most_diverse(population, mu):
    print "Selecting most diverse individuals"

    G = cm.build_graph(population, settings.MAX_DISTANCE)

    return find_distant_individuals(G, mu)


def find_distant_individuals(G, n):
    weights = list(range(0, settings.MAX_DISTANCE))
    first = 0
    last = len(weights) - 1
    found = False
    found_graph = nx.Graph()

    while first < last and not found:
        midpoint = (first + last) // 2
        found_graph = component_for_min_weight(G, midpoint)
        if len(found_graph) == n:
            found = True
        else:
            if len(found_graph) < n:
                last = midpoint - 1
            else:
                first = midpoint + 1

    selected = []
    for node in found_graph.nodes(data=True):
        selected.append(node[1]['ind'])

    # assert len(selected) == n

    return selected


def component_for_min_weight(H, min_weight):
    G = H.copy()

    largest_component = max(nx.connected_component_subgraphs(G), key=len)

    edges = largest_component.edges(data='weight')
    if len(edges) > 0:
        for edge in edges:
            if edge[2] <= min_weight:
                # if edge weight lower than min
                largest_component.remove_edge(edge[0], edge[1])

        largest_component = max(nx.connected_component_subgraphs(largest_component), key=len)
        return largest_component

    return 0


def return_as_is(a):
    return a


def initRepeat(container, func, n, device, apk_dir, package_name):
    return container(func(device, apk_dir, package_name) for _ in xrange(n))


def remove_duplicates(individuals):
    dup_indexes = []
    for i in range(len(individuals)):
        for j in range(i + 1, len(individuals)):
            distance = pm.distance_between_individuals(individuals[i], individuals[j])
            if distance == 0 and j not in dup_indexes:
                dup_indexes.append(j)

    no_duplicates = []
    for i in range(len(individuals)):
        if i not in dup_indexes:
            no_duplicates.append(individuals[i])

    return no_duplicates


def select_without_duplicates(individuals, k):
    if settings.REMOVE_DUPLICATES:
        individuals = remove_duplicates(individuals)

    return tools.selNSGA2(individuals, k)


### deap framework setup
creator.create("FitnessCovLen", base.Fitness, weights=(10.0, -0.5, 1000.0))
creator.create("Individual", list, fitness=creator.FitnessCovLen, distances=[], avg_dist=0)

toolbox = base.Toolbox()

toolbox.register("individual", generate_individual)

toolbox.register("population", initRepeatParallel.initPopulation, list, toolbox.individual)

toolbox.register("evaluate", evaluate_suite)
# mate crossover two suites
toolbox.register("mate", tools.cxUniform, indpb=0.5)
# mutate should change seq order in the suite as well
toolbox.register("mutate", mut_suite, indpb=0.5)
# toolbox.register("select", tools.selTournament, tournsize=5)
toolbox.register("select", select_without_duplicates)

toolbox.register("select_most_diverse", select_most_diverse)

toolbox.register("pareto_front", tools.sortNondominated)

# log the history
history = tools.History()
# Decorate the variation operators
toolbox.decorate("mate", history.decorator)
toolbox.decorate("mutate", history.decorator)


def get_package_name(path):
    apk_path = None
    if path.endswith(".apk"):
        apk_path = path
    else:
        for file_name in os.listdir(path + "/bin"):
            if file_name == "bugroid-instrumented.apk":
                apk_path = path + "/bin/bugroid-instrumented.apk"
                break
            elif file_name.endswith("-debug.apk"):
                apk_path = path + "/bin/" + file_name

    assert apk_path is not None

    get_package_cmd = "aapt d xmltree " + apk_path + " AndroidManifest.xml | grep package= | awk 'BEGIN {FS=\"\\\"\"}{print $2}'"
    # print get_package_cmd
    package_name = subprocess.Popen(get_package_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
    return package_name, apk_path


def main(instrumented_app_dir):
    """
	Test one apk
	:param instrumented_app_dir: The instrumentation folder of the app | apk file path for closed-source app
	"""

    host_system = platform.system()
    if host_system == "Darwin":
        print "Running on Mac OS"
        settings.TIMEOUT_CMD = "gtimeout"
    elif host_system == "Linux":
        print "Running on Linux"
    else:
        print "Runnning on unknown OS"

    package_name, apk_path = get_package_name(instrumented_app_dir)

    # check if an interrupted run available
    if settings.IGNORE_INTERRUPTED_RUNS:
        resume = False
    else:
        interrupted_output_dir = find_interrupted_run(instrumented_app_dir)
        resume = interrupted_output_dir is not None

    if not resume:
        # for css subjects
        if instrumented_app_dir.endswith(".apk"):
            instrumented_app_dir += "_output"
            i = 1
            tmp = instrumented_app_dir
            # avoid deleting output folder
            while os.path.isdir(tmp):
                tmp = instrumented_app_dir + "_" + str(i)
                i += 1
            instrumented_app_dir = tmp
            os.system("mkdir " + instrumented_app_dir)
    else:
        instrumented_app_dir = interrupted_output_dir

    print "### Working on apk:", package_name

    # get emulator device
    print "Preparing devices ..."

    if settings.USE_REAL_DEVICE:
        real_device.adb_root()
        # real_device.prepare_motifcore()
        devices = real_device.get_devices()
    else:
        # emulator.boot_genymotion_devices()
        emulator.boot_devices(wipe_data=True)
        emulator.prepare_motifcore()
        emulator.clean_sdcard()
        # log the devices
        devices = emulator.get_devices()

    # static analysis
    if settings.ENABLE_STRING_SEEDING:
        if ".apk_output" in instrumented_app_dir:
            output_dir = instrumented_app_dir
        else:
            output_dir = instrumented_app_dir + "/bin"
        static_analyser.decode_apk(apk_path, output_dir)
    # will use dummy 0 if disabled
    for device in devices:
        if ".apk_output" in instrumented_app_dir:
            decoded_dir = instrumented_app_dir + "/" + apk_path.split("/")[-1].split(".apk")[0]
        else:
            decoded_dir = instrumented_app_dir + "/bin/" + apk_path.split("/")[-1].split(".apk")[0]
        static_analyser.upload_string_xml(device, decoded_dir, package_name)

        os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
        # os.system("adb -s " + device + " uninstall " + package_name)
        os.system("adb -s " + device + " install " + apk_path)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    # axis = 0, the numpy.mean will return an array of results
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    stats.register("pop_fitness", return_as_is)

    # facebook_login(devices, package_name)

    if not resume:
        # intermediate should be in app folder
        os.system("rm -rf " + instrumented_app_dir + "/intermediate")
        os.system("mkdir " + instrumented_app_dir + "/intermediate")

        os.system("rm -rf " + instrumented_app_dir + "/crashes")
        os.system("mkdir " + instrumented_app_dir + "/crashes")

        os.system("rm -rf " + instrumented_app_dir + "/coverages")
        os.system("mkdir " + instrumented_app_dir + "/coverages")

        # generate initial population
        print "### Initialising population ...."

        n = settings.POPULATION_SIZE

        if settings.DIVERSE_INITIAL_POP:
            n = n * 2
        population = toolbox.population(n=n, apk_dir=instrumented_app_dir,
                                        package_name=package_name)

        if settings.DIVERSE_INITIAL_POP:
            population = select_most_diverse(population, settings.POPULATION_SIZE)

        print "### Individual Lengths: "
        for indi in population:
            for seq in indi:
                print len(seq),
            print ""

        history.update(population)

        # hof = tools.HallOfFame(6)
        # pareto front can be large, there is a similarity option parameter
        hof = tools.ParetoFront()

        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (
            stats.fields if stats else [])
    else:
        logbook, population, hof = eaMuPlusLambdaParallel.load_files(instrumented_app_dir)

    # evolve
    print "\n\n\n### Start to Evolve"
    population, logbook = eaMuPlusLambdaParallel.evolve(logbook, population, toolbox, settings.POPULATION_SIZE,
                                                        settings.OFFSPRING_SIZE,
                                                        cxpb=settings.CXPB, mutpb=settings.MUTPB,
                                                        ngen=settings.GENERATION,
                                                        apk_dir=instrumented_app_dir,
                                                        package_name=package_name,
                                                        stats=stats, halloffame=hof, verbose=True, resume=resume)

    # persistent
    logbook_file = open(instrumented_app_dir + "/intermediate/logbook.pickle", 'wb')
    pickle.dump(logbook, logbook_file)
    logbook_file.close()

    hof_file = open(instrumented_app_dir + "/intermediate/hof.pickle", 'wb')
    pickle.dump(hof, hof_file)
    hof_file.close()

    history_file = open(instrumented_app_dir + "/intermediate/history.pickle", 'wb')
    pickle.dump(history, history_file)
    history_file.close()

    draw_graphs(logbook, instrumented_app_dir)
    # draw history network
    # history_network.plot(history, instrumented_app_dir)
    # emulator.shutdown_genymotion_devices()
    emulator.destroy_devices()
    os.system(
        'cd ' + instrumented_app_dir + '/intermediate && pdfunite obj_0.pdf obj_1.pdf obj_2.pdf hv_standard.pdf proportion_pareto_optimal.pdf population_diameter.pdf rel_diameter.pdf population_diversity.pdf pconnec.pdf sing.pdf hvconnec.pdf avgconnec.pdf nconnec.pdf lconnec.pdf kconnec.pdf summary.pdf')

#TODO: boot devices and login
## TODO: handle logout?

def facebook_login(devices, package_name):
    print "login facebook"
    email = "steneawr@wegwerfemail.info"
    password = "abc123!"

    for d in devices:
        os.system("adb -s " + d + " shell monkey -p " + package_name + " 1")
        time.sleep(30)
        adb_shell.device = d
        adb_shell.send_click(360, 628)
        adb_shell.send_text(email)
        adb_shell.send_click(360, 740)
        adb_shell.send_text(password)
        adb_shell.sendKey(AndroidKey.ENTER)


def draw_graphs(logbook, instrumented_app_dir):
    # draw graphs
    two_d_line.plot(logbook, 0, instrumented_app_dir)
    two_d_line.plot(logbook, 1, instrumented_app_dir)
    two_d_line.plot(logbook, 2, instrumented_app_dir)
    two_d_line.plotProportionParetoOptimal(logbook, instrumented_app_dir)
    two_d_line.plotPopulationDiameter(logbook, instrumented_app_dir)
    two_d_line.plotRelativeDiameter(logbook, instrumented_app_dir)
    two_d_line.plotPopulationDiversity(logbook, instrumented_app_dir)
    two_d_line.plotGraphMetrics(logbook, instrumented_app_dir)
    two_d_line.plotHypervolume(logbook, instrumented_app_dir)


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def find_interrupted_run(apk_dir):
    apk = apk_dir.split('/')[-1]
    working_dir = apk_dir.replace(apk, '')
    for directory in get_immediate_subdirectories(working_dir):
        print 'Found dir: ' + directory
        output_dir = working_dir + directory
        # if intermediate folder exists
        if os.path.isdir(output_dir + '/intermediate'):
            # if not finished
            if not os.path.isfile(output_dir + '/intermediate/obj_0.pdf') \
                    and os.path.isfile(output_dir + '/intermediate/logbook.pickle'):
                print 'Found interrupted run in ' + output_dir
                return output_dir

    return None


if __name__ == "__main__":
    app_dir = sys.argv[1]
    main(app_dir)
    #while True:
     #   try:
      #      main(app_dir)
       #     sys.exit(0)
        #except SystemExit:
         #   break
        #except Exception as e:
         #   print e
          #  time.sleep(15)
