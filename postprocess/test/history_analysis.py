# author: Thomas Vogel

import pickle

from deap import creator, base

'''
The History class helps to build a genealogy of all the individuals produced in the evolution. 
It contains two attributes, the genealogy_tree that is a dictionary of lists indexed by individual, 
the list contain the indices of the parents. The second attribute genealogy_history contains every 
individual indexed by their individual number as in the genealogy tree.
'''

creator.create("FitnessCovLen", base.Fitness, weights=(10.0, -0.5, 1000.0))
creator.create("Individual", list, fitness=creator.FitnessCovLen)


def show_history(history):
    import matplotlib.pyplot as plt
    import networkx

    graph = networkx.DiGraph(history.genealogy_tree)
    graph = graph.reverse()  # Make the grah top-down
    networkx.draw(graph, node_color='red')
    plt.show()


if __name__ == "__main__":
    file_path = "../apks/repeated_results/1/a2dp.Vol_93_src/intermediate/"
    history_file = open(file_path + "history.pickle")

    history = pickle.load(history_file)

    print history
    show_history(history)

