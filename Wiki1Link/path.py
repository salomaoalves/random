import common
from ETL import neo4jFunc, common as commonETL


def print_info(path, word1, word2):
    '''Print information about a path between the two inputed nodes
        @path: path list
        @word1 and word2: inputed nodes'''
    print(f'\tPath between word {word1} and {word2}:')
    print(f'\t\tSize of {path[1]} - number of edges.')
    print(f'\t\tThere are {len(path[0])} nodes in this path.')
    print(f'\t\tPath: ',end='')
    common.display(path[0])


def check_path2Philo(path, word):
    '''See if exist path between the inputes nodes and the node Philosophy
        @path: 2-list of path list
        @word: 2-list with the inputed nodes'''

    # Check path for the first node
    if path[0]!='not_found':
        print_info(path[0], word[0], 'Philosophy')
    else:
        print(f'\tThere is no path between {word[0]} and Philosophy.')

    # Check path for the second node
    if path[1]!='not_found':
        print_info(path[1], word[1], 'Philosophy')
    else:
        print(f'\tThere is no path between {word[1]} and Philosophy.')


def getAttrPaths():
    '''get the required attrs for the feature'''

    # Wiki language
    lang = common.get_lang()

    # See all words already ingested
    ingested_words = neo4jFunc.get_all_nodes(lang)
    see_all_words = input('Before insert the words, wanna see all words in the graphic? (Y/N):')
    if(str.upper(see_all_words)=='Y'):
        print(ingested_words)
    
    # Get the two words/nodes
    word1 = input("First word: ")
    while not word1 in ingested_words:
        print("\nWord not Found - Input Again!!!")
        word1 = input("First word: ")
    word2 = input("Second word: ")
    while not word2 in ingested_words:
        print("\nWord not Found - Input Again!!!")
        word2 = input("Second word: ")

    return lang, word1, word2


def view_paths():
    # Get required inputs
    lang, word1, word2 = getAttrPaths()
    philo_word = commonETL.get_stop_word(lang)
    node_dict = neo4jFunc.get_all_id_nodes(lang)
    print(f'\n\nStart Path Comparison for word {word1} to {word2} in {lang}')

    # Get paths - between the nodes and from each node to the Philosophy node
    path_between = neo4jFunc.get_path_between(word1, word2, node_dict, lang)
    path_w1toPhilo = neo4jFunc.get_path_between(word1, philo_word, node_dict, lang)
    path_w2toPhilo = neo4jFunc.get_path_between(word2, philo_word, node_dict, lang)
    
    # Display paths infos
    if path_between=='not_found':
        # Path Info
        print(f'\tThere is no path between {word1} and {word2}.')
        check_path2Philo([path_w1toPhilo,path_w2toPhilo],[word1,word2])

        # Which graph the path belongs
        print(f'\tThe nodes {word1} and {word2} maybe are in different graphs - at least, ',end='')
        print(f'{word2} it isn\'t ahead of {word1} in it\'s. Let\'s see!!!')
        if path_w1toPhilo!='not_found' and path_w2toPhilo!='not_found':
            print(f'\t\tNodes {word1} and {word2} belongs to the main graph Philosophy.')
        elif path_w1toPhilo=='not_found' and path_w2toPhilo!='not_found':
            print(f'\t\tNode {word1} belongs to a loop graph.')
            print(f'\t\tNode {word2} belongs to the main graph Philosophy.')
        elif path_w1toPhilo!='not_found' and path_w2toPhilo=='not_found':
            print(f'\t\tNode {word1} belongs to the main graph Philosophy.')
            print(f'\t\tNode {word2} belongs to a loop graph.')
        elif path_w1toPhilo=='not_found' and path_w2toPhilo=='not_found':
            print(f'\t\tNodes {word1} and {word2} belongs to two differents loop graphs.')
    else:
        # Path Info
        print_info(path_between, word1, word2)
        check_path2Philo([path_w1toPhilo,path_w2toPhilo],[word1,word2])

        # Which graph path belongs
        if path_w1toPhilo!='not_found' and path_w2toPhilo!='not_found':
            print(f'\tNodes {word1} and {word2} belongs to the main graph Philosophy.')
        else:
            print(f'\tThe path between nodes {word1} and {word2} is in a loop.')

