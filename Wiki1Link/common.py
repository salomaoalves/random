from ETL import neo4jFunc, common as commonETL
import networkx as nx


def get_lang():
    '''return the Wikipedia language used'''

    print('Language:')
    print('\t1 - English\n\t2 - Portuguese')
    print('\t3 - Spanish\n\t4 - Fake Data')
    print('\t5 - Customize')
    while True:
        lang_n = input('\tChoose: ').strip()
        if lang_n == '1': return 'en'
        elif lang_n == '2': return 'pt'
        elif lang_n == '3': return 'es'
        elif lang_n == '4': return 'fake'
        elif lang_n == '5':
            lang = input('\t\tCustomize Lang: ').strip()
            if lang: return lang
        print('\tWrong number - input again!!!')


def display(nodes):
    '''display a list of nodes in a pre-defined format
        @nodes: list of nodes'''
    print('|| ' + '--->'.join(str(n) for n in nodes) + ' ||')


def get_graph(lang):
    '''create a nx DiGraph from a certain database type
        @lang: database type'''

    # Get raw graph - list of tuples/edges
    graph_raw = neo4jFunc.get_all(lang)

    # Build nx DiGraph
    G = nx.DiGraph()
    G.add_edges_from(graph_raw)
    G.add_nodes_from(neo4jFunc.get_all_isolated(lang))

    return G

def get_loops(lang):
    '''get all loops in the graph
        @lang: database type'''

    # Get all nodes that belong to some loop
    loops_node = neo4jFunc.get_loops(lang)

    # Build a nx Graph for each loop
    loop_graphs = []
    for loop in loops_node:
        loop_graphs.append(nx.path_graph(loop))
    return loop_graphs

def get_philo_graph(graph, lang):
    '''select the Philosophy Graph - the "Philosophy" node and
        all nodes that have a path to it
        @graph: nx DiGraph
        @lang: database type'''
    philo_word = commonETL.get_stop_word(lang)
    if philo_word not in graph:
        return graph.subgraph([])
    return graph.subgraph(nx.ancestors(graph, philo_word) | {philo_word})
