import common
from ETL import common as commonETL, neo4jFunc
import networkx as nx


def getAttrSummary():
    '''get the required attrs for the feature'''

    # Wiki language
    lang = common.get_lang()
    
    # Inputs words
    n_word, words = int(input('How many words:')), []
    for i in range(n_word):
        words.append(input(f'\tWord{i+1}: '))

    return lang, words, n_word

def get_philo(node):
    '''auxiliar function used to select the Philosophy Graph.
        Will verify if the node belong to the philo graph
        for that, try to find a path between the @node and "Philosophy"
        If node=Philosophy, return True'''
    philo_word = commonETL.get_stop_word(lang)
    node_dict = neo4jFunc.get_all_id_nodes(lang)
    pathToPhilo = neo4jFunc.get_path_between(node, philo_word, node_dict, lang)
    if node==philo_word:
        in_philo = True
    else:
        in_philo = pathToPhilo!='not_found'
    return in_philo


def graph_info(word, philo_word, node_dict, lang):
    '''show graph info related to a certain node
        @word: reference node
        @philo_word: node "Philosophy"
        @node_dict: a dict with node id and name
        @lang: database type'''

    # Search a path for the node inside the Philosophy graph
    path_WordtoPhilo = neo4jFunc.get_path_between(word, philo_word, node_dict, lang)
    
    # Print graph info
    if path_WordtoPhilo=='not_found':
        if word==philo_word:
            print('\t\t\tThis is the "Philosophy" node.')
        else:
            loop = neo4jFunc.get_path_between(word, word, node_dict, lang)
            print('\t\t\tBelongs to a "Loop Graph"!!')
            print(f'\t\t\tPath: ',end='')
            common.display(loop[0])
            print(f'\t\t\tSize of: {len(loop[0])-1}')
    else:
        print('\t\t\tBelongs to the "Philosophy Graph"!!')
        print(f'\t\t\tPath: ',end='')
        common.display(path_WordtoPhilo[0])
        print(f'\t\t\tSize of: {len(path_WordtoPhilo[0])-1}')


def succ_pred_nodes(graph, word):
    '''show successors and predecessors nodes
        @graph: 
        @word: reference node'''

    # Get all pred and succ nodes
    pred_nodes = list(graph.predecessors(word))
    succ_nodes = list(graph.successors(word))

    # Print info
    for nodes, name in [[pred_nodes,'Predecessors'],[succ_nodes,'Successors']]:
        print(f'\t\t\t{name} words: | ',end='')
        if len(nodes)==0: print('No word |')
        else:
            for n in nodes:
                if n == nodes[-1]:
                    print(f'{n} |')
                else:
                    print(f'{n} - ',end='')


def summary_stats():
    # Get required inputs
    global lang
    lang, words, n_word = getAttrSummary()
    philo_word = commonETL.get_stop_word(lang)
    node_dict = neo4jFunc.get_all_id_nodes(lang)
    graph = common.get_graph(lang)
    print(f'\n\nStart Summary Statistics with Wikipidea in {lang}')
    
    
    print('\tGeneral Graph Info')
    
    # Number of nodes and edges for each graph
    loop_graph = common.get_loops(lang, node_dict)
    philo_graph = nx.subgraph_view(graph, filter_node=get_philo)
    print(f'\t\tNumber of nodes: {graph.order()}')
    print(f'\t\tNumber of edges: {graph.size()}')
    print(f'\t\tNumber of nodes (Philo): {philo_graph.order()}')
    print(f'\t\tNumber of edges (Philo): {philo_graph.size()}')
    for i, loop in enumerate(loop_graph):
        print(f'\t\tNumber of nodes (Loop{i}): {loop.order()}')
        print(f'\t\tNumber of edges (Loop{i}): {loop.size()}')
    
    # Max degree, if there is isolate nodes or selfloops
    print(f'\t\tMax degree: {max(dict(graph.degree).values())}')
    if nx.number_of_isolates(graph)>0:
        print(f'\t\tisolates {list(nx.isolates(graph))}')
    else:
        print('\t\tThere is no isolates nodes.')
    if nx.number_of_selfloops(graph)>0:
        for i, self_loop in enumerate(list(nx.selfloop_edges(graph))):
            print(f'\t\tSelfLoop{i}: ',end='')
            common.display(list(self_loop))
    else:
        print('\t\tThere is no self loops.')


    print('\tSummary per word')
    for i in range(len(words)):
        print(f'\t\tWord: {words[i]}')

        # Get successor and predecessors words
        succ_pred_nodes(graph, words[i])

        # Get word's degress
        in_degree = graph.in_degree(words[i])
        out_degree = graph.out_degree(words[i])
        print(f'\t\t\tNumber of edges pointing to the word: {in_degree}')
        print(f'\t\t\tNumber of edges pointing out of the word: {out_degree}')

        # Get graph info related to the word
        graph_info(words[i], philo_word, node_dict, lang)


    print('\tPath between the words inputed')
    # It'll test the path between all possible pairs of nodes inputed
    if n_word>1:
        for i in range(n_word):
            for j in range(i,n_word):
                if words[i]!=words[j]:
                    print(f'\t\tPath between nodes {words[i]} and {words[j]}')
                    path_between = neo4jFunc.get_path_between(words[i], words[j], node_dict, lang)
                    if path_between=='not_found':
                        print(f'\t\t\tThere is no directed path between nodes {words[i]} and {words[j]}!!')
                        print('\t\t\t\t-put this two nodes in the "View Path" feature to verify which graph they belongs.')
                    else:
                        print('\t\t\t',end='')
                        common.display(path_between[0])
