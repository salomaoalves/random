import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from ETL import common

_driver = None

def create_drive():
    '''create connection with local database - only once, then reuse it
        set NEO4J_URI, NEO4J_USER and NEO4J_PASSWORD to change the defaults'''
    global _driver
    if _driver is not None:
        return _driver

    # Database information
    connectionString = os.environ.get('NEO4J_URI', 'neo4j://localhost:7687')
    username = os.environ.get('NEO4J_USER', 'neo4j')
    psw = os.environ.get('NEO4J_PASSWORD', 'neo4j')

    # Make and test the connection
    driver = GraphDatabase.driver(connectionString, auth=(username,psw),
                                  notifications_min_severity='OFF')
    try:
        driver.verify_connectivity()
    except (ServiceUnavailable, AuthError) as err:
        print(err)
        exit(f'Could not connect to Neo4j at {connectionString} - check NEO4J_URI, NEO4J_USER and NEO4J_PASSWORD.')

    _driver = driver
    return driver


def label(lang):
    '''node label for a database type - escaped to be used in Cypher'''
    return '`' + lang.replace('`', '') + '`'


def rel_type(lang):
    '''relationship type for a database type - escaped to be used in Cypher'''
    return '`' + lang.replace('`', '') + '_link`'


# Auxiliar Write Transactions
def create_node(tx, word, date, lang):
    '''create one simple node - if it doesn't exist'''
    tx.run(
        f"MERGE (n:{label(lang)} "+"{word: $word}) "
        "ON CREATE SET n.date = $date",
        word=word, date=date
    )

def create_rel(tx, snode, dnode, lang):
    '''creates a directed relantionship between two nodes - if it doesn't exist'''
    tx.run(
        f"MATCH (ns:{label(lang)}) WHERE ns.word=$snode "
        f"MATCH (dn:{label(lang)}) WHERE dn.word=$dnode "
        f"MERGE (ns)-[r:{rel_type(lang)}]->(dn)",
    snode=snode,dnode=dnode)


# Auxiliar Read Transactions
def read_all_node(tx, lang):
    '''read all graph nodes'''
    word = []
    for r in tx.run(f"MATCH (node:{label(lang)}) "
                     "RETURN node.word AS word"):
        word.append(r['word'])
    return word

def read_path_between(tx, word1, word2, lang):
    '''find a path between two nodes and return a list of nodes
        (the path) and the numb of edges; if not, return "not_found"'''
    resp = tx.run(f"MATCH p=(n1:{label(lang)})-[:{rel_type(lang)}*1..]->(n2:{label(lang)}) "
                   "WHERE n1.word=$w1 "
                   "AND n2.word=$w2 "
                   "RETURN [n IN nodes(p) | n.word] AS path "
                   "ORDER BY length(p) LIMIT 1",w1=word1,w2=word2).single()
    if resp is None:
        return 'not_found'
    return resp['path'], len(resp['path'])-1

def read_all(tx, lang):
    '''read all edges (pair of nodes) of the graph'''
    edges = []
    for resp in tx.run( f"MATCH (n1:{label(lang)})-[r:{rel_type(lang)}]->(n2:{label(lang)}) "
                        "RETURN n1.word AS n1, n2.word AS n2"):
        edges.append((resp['n1'],resp['n2']))
    return edges

def read_all_isolated(tx, lang):
    '''read all nodes without any relationship'''
    return [r['word'] for r in tx.run(f"MATCH (n:{label(lang)}) "
                                      f"WHERE NOT (n)-[:{rel_type(lang)}]-() "
                                      "RETURN n.word AS word")]

def read_loops(tx, lang):
    '''read all loops find in the graph'''
    loops = []
    for resp in tx.run( f"MATCH p=(n1:{label(lang)})-[:{rel_type(lang)}*1..]->(n1) "
                        "RETURN [n IN nodes(p) | n.word] AS loop"):
        loop = resp['loop']
        if all(loop[0] not in l for l in loops): #eliminates duplicates
            loops.append(loop)
    return loops


# Auxiliar Delete Transactions
def del_node(tx, lang, word):
    '''delete a specific node'''
    tx.run(
        f"MATCH (node:{label(lang)}) WHERE node.word=$word "
        "DETACH DELETE node;"
    , word=word)


# Write Custom Funcs
def creat_stopWord_nodes():
    '''create Stop Word node for each database type - en, pt and es'''
    driver = create_drive()
    with driver.session() as session:
        for lang in ['en', 'pt', 'es']:
            session.execute_write(create_node, common.get_stop_word(lang), common.DATA_ATUAL, lang)

def insert_nodes(vert, lang):
    '''do the ingestion of some words
        @vert: list of words/nodes
        @lang: database type'''

    # Start ingestion
    driver = create_drive()
    with driver.session() as session:

        # Create the nodes and the relationships between them
        session.execute_write(create_node, vert[0], common.DATA_ATUAL, lang)
        for i in range(1,len(vert)):
            session.execute_write(create_node, vert[i], common.DATA_ATUAL, lang)
            session.execute_write(create_rel, vert[i-1], vert[i], lang)


# Read Custom Funcs
def get_all_nodes(lang):
    '''read all graph nodes
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        return session.execute_read(read_all_node, lang)

def get_path_between(word1, word2, lang):
    '''read path between two defined nodes
        @word1/word2: start and end node of the path
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        return session.execute_read(read_path_between, word1, word2, lang)

def get_all(lang):
    '''read all the edges, useful to create the total graph
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        return session.execute_read(read_all, lang)

def get_all_isolated(lang):
    '''read all nodes without relationship, they aren't in the edges
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        return session.execute_read(read_all_isolated, lang)

def get_loops(lang):
    '''read all graph loops
        @lang: database type'''

    driver = create_drive()
    with driver.session() as session:
        return session.execute_read(read_loops, lang)
