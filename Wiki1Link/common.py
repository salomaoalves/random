from ETL import neo4jFunc
import networkx as nx


def get_lang():
    '''return the Wikipedia language used'''

    print('Language:')
    print('\t1 - English\n\t2 - Portuguese')
    print('\t3 - Spanish\n\t4 - Fake Data')
    print('\t5 - Customize')
    lang_n = input('\tChoose: ')
    if lang_n == '1': return 'en'
    elif lang_n == '2': return 'pt'
    elif lang_n == '3': return 'es'
    elif lang_n == '4': return 'fake'
    elif lang_n == '5': 
        lang = input('\t\tCustomize Lang: ')    
        return lang
    else: exit('Wrong number')


def display(nodes):
    '''display a list of nodes in a pre-defined format
        @nodes: list of nodes'''
    str_display = ''
    for i, n in enumerate(nodes):
        if i==0:
            str_display += '|| '+str(n)+'--->'
        elif i==len(nodes)-1:
            str_display += str(n)+' ||'
        else:
            str_display += str(n)+'--->'
    print(str_display)


def get_graph(lang):
    '''create a nx DiGraph from a certain database type
        @lang: database type'''

    # Get raw graph - list of tuples/edges
    graph_raw = neo4jFunc.get_all(lang)

    # Build nx DiGraph
    G = nx.DiGraph()
    G.add_edges_from(graph_raw)

    return G

def get_loops(lang,node_dict):
    '''get all loops in the graph
        @lang: database type
        @node_dict: a dict with node id and name'''

    # Get all nodes that belong to some loop
    loops_node = neo4jFunc.get_loops(lang,node_dict)

    # Build a nx Graph for each loop
    loop_graphs = []
    for loop in loops_node:
        loop_graphs.append(nx.path_graph(loop))
    return loop_graphs