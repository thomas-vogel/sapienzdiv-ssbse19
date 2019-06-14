# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import pickle

import matplotlib.pyplot as plt


def print_pop_fitness(file_folder_path):
    logbook_file = open(file_folder_path + "logbook.pickle")

    logbook = pickle.load(logbook_file)

    for gen_pop in logbook.select("pop_fitness"):
        print gen_pop


def draw_pop_fitness(file_folder_path):
    coverages = []
    lengths = []
    colors = []  # color stands for the ith gen

    logbook_file = open(file_folder_path + "logbook.pickle")

    logbook = pickle.load(logbook_file)

    gen_size = len(logbook.select("pop_fitness"))
    for gen, gen_pop in enumerate(logbook.select("pop_fitness")):
        for indi in gen_pop:
            coverages.append(indi[0])
            lengths.append(indi[1])
            colors.append(int(gen + 1))

    # print coverages, lengths, colors

    fig, ax = plt.subplots()
    ax.set_xlabel("Length")
    ax.set_ylabel("Coverage")

    # ax.scatter(lengths, coverages, color="red", marker="^")
    im = ax.scatter(lengths, coverages, c=colors, cmap=plt.cm.jet, marker=".", s=100)

    fig.colorbar(im, ax=ax, ticks=range(1, gen_size + 1))
    im.set_clim(1, gen_size)

    fig.savefig(file_folder_path + "logbook_pop_fitness.png")
    plt.show()


if __name__ == "__main__":
    file_folder_path = "/media/kemao/Windows7_OS/bak_p500/emma_run_results/sapienz_open_p/19/com.brocktice.JustSit_17_src/intermediate/"

    print_pop_fitness(file_folder_path)
    draw_pop_fitness(file_folder_path)
