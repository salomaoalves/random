import matplotlib.pyplot as plt
import networkx as nx
import common

def show_graphics(): 
    # Get requires inputs
    lang = common.get_lang()
    print(f'Start Graphs with Wikipidea in {lang}')

    # Get the total graph and it's loops and Philo graph
    graph = common.get_graph(lang)
    if graph.order()==0:
        print(f'\tThere is no word ingested for {lang}!!!')
        return
    loop_graph = common.get_loops(lang)
    philo_graph = common.get_philo_graph(graph, lang)

    # Plot graphs - first the Philosophy
    if philo_graph.order()==0:
        print('There is no Philosophy graph.')
    else:
        print('Philosophy graph - Planar Form')
        if nx.is_planar(philo_graph):
            nx.draw_planar(philo_graph, with_labels=True, font_size=6)
            plt.show()
        else:
            print('\tThe graph isn\'t planar.')
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