from __future__ import division

import networkx as nx
import settings
from metrics import non_dominated_metrics as ndm
from metrics import population_metrics as pm

metrics = {'nconnec': 'Number of connected components',
           'pconnec': 'Percentage of vertices in clusters',
           'sing': 'Proportion of singletons in the graph',
           'lconnec': 'Number of vertices in the largest cluster',
           'avgconnec': 'Average distance between solutions of the largest component',
           'hvconnec': 'Proportion of hypervolume covered by the largest component',
           'kconnec': 'Minimum distance necessary for a connected graph'}


def build_graph(pareto_front, max_edge_weight):
    G = nx.Graph()
    if len(pareto_front) == 1:
        G.add_node(0)
        G.node[0]['ind'] = pareto_front[0]
        return G

    for i in range(len(pareto_front)):
        for j in range(i + 1, len(pareto_front)):
            first_ind = pareto_front[i]
            second_ind = pareto_front[j]
            G.add_node(i)
            G.add_node(j)
            G.node[i]['ind'] = first_ind
            G.node[j]['ind'] = second_ind
            distance = pm.distance_between_individuals(first_ind, second_ind)
            if distance <= max_edge_weight:
                G.add_edge(i, j, weight=distance)
    return G


def analyze_graph(pareto_front, front_hv, max_edge_weights):
    results = []

    G = build_graph(pareto_front, settings.SUITE_SIZE * settings.SEQUENCE_LENGTH_MAX)
    kconnec = minimal_connection_distance(G)
    result = {"kconnec": kconnec}
    results.append(result)
    print "Minimum distance necessary for a connected graph: " + str(kconnec)

    for weight in max_edge_weights:
        result = {}
        G = build_graph(pareto_front, weight)
        nconnec, pconnec, sing = proportion_cluster_vertices_and_singletons(G)
        lconnec, hvconnec, avgconnec = analyze_largest_component(G, front_hv)

        result["nconnec_" + str(weight)] = nconnec
        result["pconnec_" + str(weight)] = pconnec
        result["sing_" + str(weight)] = sing
        result["lconnec_" + str(weight)] = lconnec
        result["hvconnec_" + str(weight)] = hvconnec
        result["avgconnec_" + str(weight)] = avgconnec

        results.append(result)

        print "Percentage of vertices in cluster: " + str(pconnec)
        print "Percentage of singletons: " + str(sing)
        print "Proportion of hypervolume covered by the largest component: " + str(hvconnec)
        print "Average distance between solutions of the largest component: " + str(avgconnec)
        print "Number of connected components: " + str(nconnec)
        print "Number of vertices in the largest cluster: " + str(lconnec)

    return results


def proportion_cluster_vertices_and_singletons(G):
    total_nodes = len(G.nodes())

    # build component graphs
    components = list(nx.connected_component_subgraphs(G))

    nodes_in_components = 0
    number_of_singletons = 0
    for c in components:
        if len(c.nodes()) > 1:
            nodes_in_components += len(c.nodes())
        else:
            number_of_singletons += 1

    proportion_cluster_vertices = nodes_in_components / total_nodes
    proportion_singletons = number_of_singletons / total_nodes

    return len(components), proportion_cluster_vertices, proportion_singletons


def analyze_largest_component(G, front_hv):
    components = list(nx.connected_component_subgraphs(G))
    if len(components) == 0:
        print "Error: no graph components found"
        return 0.0

    largest_component = components[0]
    largest_component_length = 0
    for i in range(1, len(components)):
        if len(components[i].nodes()) > largest_component_length:
            largest_component = components[i]

    proportion_largest_cluster_hv = 0.0
    if front_hv > 0:
        # get all individuals in nodes of largest component
        pop_largest_component = nx.get_node_attributes(largest_component, 'ind').values()
        print "Individuals in largest component: " + str(len(pop_largest_component))
        largest_component_hyperv = ndm.hypervolume(pop_largest_component)
        print "Largest component hypervolume: " + str(largest_component_hyperv)
        proportion_largest_cluster_hv = largest_component_hyperv / front_hv

    total_dist = 0
    for edge in list(largest_component.edges_iter(data='weight', default=0)):
        total_dist += edge[2]

    avg_dist = 0
    if len(largest_component.edges()) > 0:
        avg_dist = total_dist / len(largest_component.edges())

    return len(largest_component.nodes()), proportion_largest_cluster_hv, avg_dist


def minimal_connection_distance(G):
    graph = G.copy()

    min_weight = 0
    while nx.is_connected(graph):
        edges = graph.edges(data='weight')
        edge_count = len(edges)
        # print "minimal_connection_distance: edge count: " + str(edge_count)
        if edge_count > 0:
            min_weight = min(nx.get_edge_attributes(graph, 'weight').values())
            for edge in edges:
                # print "minimal_connection_distance: edge weight: " + str(edge[2])
                if edge[2] == min_weight:
                    graph.remove_edge(edge[0], edge[1])
                    # print "minimal_connection_distance: Removing edge " + str(edge[0]) + " -> " + str(edge[1])
        else:
            print "minimal_connection_distance: no edges in graph"
            break

    return min_weight
