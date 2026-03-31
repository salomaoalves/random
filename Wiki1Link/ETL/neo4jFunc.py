from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from ETL import common

def create_drive():
    '''create connection with local database'''

    # Database information
    connectionString = "neo4j://localhost:7687"
    username, psw = '***', '****'

    # Make and test the connection
    driver = GraphDatabase.driver(connectionString, auth=(username,psw))
    try:
        driver.verify_connectivity()
    except ServiceUnavailable as err:
        print(err)
        exit()

    return driver


# Auxiliar Write Transactions 
def create_node(tx, word, date, lang):
    '''create one simple node'''
    tx.run(
        f"CREATE (:{lang} "+"{word: $word, date: $date})",
        word=word, date=date
    )

def create_rel(tx, snode, dnode, lang):
    '''creates a directed relantionship between two nodes'''
    tx.run(
        f"MATCH (ns:{lang}) WHERE ns.word=$snode "
        f"MATCH (dn:{lang}) WHERE dn.word=$dnode "
        f"CREATE (ns)-[r:{lang}_link]->(dn)",
    snode=snode,dnode=dnode)


# Auxiliar Read Transactions
def read_all_node(tx, lang):
    '''read all graph nodes'''
    word = []
    for r in tx.run(f"MATCH (node:{lang}) "
                     "RETURN node"):
        word.append(r['node']['word'])
    return word

def read_path_between(tx, word1, word2, dict_node, lang):
    '''find a path between two nodes and return a list of nodes
        (the path) and the numb of edges; if not, return "not_found"'''
    path = [word1]
    try:
        for resp in tx.run(f"MATCH (n1:{lang}) "
                        f"MATCH (n2:{lang}) "
                        f"MATCH (n1)-[r:{lang}_link*]->(n2) "
                            "WHERE n1.word=$w1 "
                            "AND n2.word=$w2 "
                            "RETURN r",w1=word1,w2=word2):
            size = len(resp['r'])
            for rr in resp['r']: # to get the nodes name in the path
                path.append(dict_node[rr.end_node.id])
        return path, size
    except UnboundLocalError:
        return 'not_found'

def read_all_id_node(tx, lang):
    '''read all nodes id and create a dict from it
        *keys: node id
        *value: node name'''
    nodes = {}
    for resp in tx.run(f"MATCH (n1:{lang}) "
                        "RETURN n1, ID(n1) AS id"):
        nodes.update({resp['id']: resp['n1']['word']})
    return nodes

def read_all(tx, lang):
    '''read all edges (pair of nodes) of the graph'''
    edges = []
    for resp in tx.run( f"MATCH (n1:{lang}) "
                        f"MATCH (n2:{lang}) "
                        f"MATCH (n1)-[r:{lang}_link]->(n2) "
                        "RETURN n1, n2"):
        edges.append((resp['n1']['word'],resp['n2']['word']))
    return edges

def read_loops(tx, dict_node, lang):
    '''read all loops find in the graph'''
    loops = [[]]
    for resp in tx.run( f"MATCH (n1:{lang}) "
                        f"MATCH (n2:{lang}) "
                        f"MATCH (n1)-[r:{lang}_link*]->(n2) "
                        f"WHERE n2.word=n1.word "
                        "RETURN n1, r"):
        loop, check_loop = [resp['n1']['word']], True
        for rr in resp['r']: #get loops nodes
            loop.append(dict_node[rr.end_node.id])
        for i in range(len(loops)): #eliminates duplicates
            check_loop = check_loop and (loop[0] not in loops[i])
        if check_loop:
            loops.append(loop)
    return loops[1:]


# Auxiliar Delete Transactions
def del_node(tx, lang, word):
    '''delete a specific node'''
    tx.run(
        f"MATCH (node:{lang}) WHERE node.word=$word "
        "DELETE node;"
    , word=word)


# Write Custom Funcs
def creat_stopWord_nodes():
    '''create Stop Word node for each database type - en, pt and es'''
    driver = create_drive()
    with driver.session() as session:
        session.write_transaction(create_node, common.get_stop_word('en'), common.DATA_ATUAL, 'en')
        session.write_transaction(create_node, common.get_stop_word('pt'), common.DATA_ATUAL, 'pt')
        session.write_transaction(create_node, common.get_stop_word('es'), common.DATA_ATUAL, 'es')
        session.close()

def insert_nodes(vert, lang):
    '''do the ingestion of some words
        @vert: list of words/nodes
        @lang: database type'''

    # Start ingestion
    driver = create_drive()
    with driver.session() as session:

        # Create the node for the first word
        session.write_transaction(create_node, vert[0], common.DATA_ATUAL, lang)
        
        # Create the relationships and the nodes for the destiny node
        for i in range(1,len(vert)-1):
            session.write_transaction(create_node, vert[i], common.DATA_ATUAL, lang)
            session.write_transaction(create_rel, vert[i-1], vert[i], lang)
        session.write_transaction(create_rel, vert[-2], vert[-1], lang)

        session.close()


# Read Custom Funcs
def get_all_nodes(lang):
    '''read all graph nodes
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        result = session.read_transaction(read_all_node, lang)
        session.close()

    return result

def get_path_between(word1, word2, dict_node, lang):
    '''read path between two defined nodes
        @word1/word2: start and end node of the path
        @dict_node: a dict with node id and name
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        result = session.read_transaction(read_path_between, word1, word2, dict_node, lang)
        session.close()

    return result

def get_all_id_nodes(lang):
    '''read all id nodes, creating a dict with it's id (key) and name (value)
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        result = session.read_transaction(read_all_id_node, lang)
        session.close()

    return result

def get_all(lang):
    '''read all the edges, useful to create the total graph
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        result = session.read_transaction(read_all, lang)
        session.close()

    return result

def get_loops(lang, dict_node):
    '''read all graph loops
        @lang: database type
        @dict_node: a dict with node id and name'''

    driver = create_drive()
    with driver.session() as session:
        result = session.read_transaction(read_loops, dict_node, lang)
        session.close()

    return result
