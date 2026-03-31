from ETL import common as commonETL, neo4jFunc
import matplotlib.pyplot as plt
import networkx as nx
import common

def get_philo(node):
    '''auxiliar function used to select the Philosophy Graph.
        Will verify if the node belong to the philo graph
        for that, try to find a path between the @node and "Philosophy"'''
    philo_word = commonETL.get_stop_word(lang)
    node_dict = neo4jFunc.get_all_id_nodes(lang)
    pathToPhilo = neo4jFunc.get_path_between(node, philo_word, node_dict, lang)
    if node==philo_word:
        in_philo = True
    else:
        in_philo = pathToPhilo!='not_found'
    return in_philo

def show_graphics(): 
    print(f'Start Graphs with Wikipidea in ')

    # Get requires inputs
    global lang
    lang = 'fake'#common.get_lang()
    node_dict = neo4jFunc.get_all_id_nodes(lang)

    # Get the total graph and it's loops and Philo graph
    graph = common.get_graph(lang)
    loop_graph = common.get_loops(lang, node_dict)
    philo_graph = nx.subgraph_view(graph, filter_node=get_philo)

    # Plot graphs - first the Philosophy
    print('Philosophy graph - Planar Form')
    nx.draw_planar(philo_graph, with_labels=True, font_size=6)
    plt.show()
    print('Philosophy graph - Kamada Kawai Form')
    nx.draw_kamada_kawai(philo_graph, with_labels=True, font_size=6)
    plt.show()
    print('Philosophy graph - Default Form')
    nx.draw(philo_graph, with_labels=True, font_size=6)
    plt.show()
    for i, loop in enumerate(loop_graph): #then, the loops
        print(f'Loop graph {i}')
        nx.draw_circular(loop, with_labels=True, font_size=6)
        plt.show()