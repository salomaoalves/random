from ETL import neo4jFunc, common

def fake_data():
    vert_fake = [ #list of path to ingest
        ['W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','W14','Philosophy'],
        ['W15','W16','W17','W18','W19','W20','W10'],
        ['W21','W22','W23','W24','W20'],
        ['W25','W26','W27','W16'],
        ['W208','W209','W200','W201','W202','W203','W204','205','206','207','W208'],
        ['W108','W109','W100','W101','W102','W103','W104','105','106','107','W108'],
        ['W35','W36','W37','W38','W39','W40','W41','W42','W43','W44','W45','W46','W47','Philosophy'],
        ['W48','W49','W50','W51','W52','W53','W54','W55','W56','W57','W58','W59','W60','W45'],
        ['W61','W62','W63','W64','W65','W66','W67','W68','W69','Philosophy'],    
    ]
    driver = neo4jFunc.create_drive()
    with driver.session() as session:
        session.write_transaction(neo4jFunc.create_node, 'Philosophy', common.DATA_ATUAL, 'fake')
    for vert in vert_fake:
        neo4jFunc.insert_nodes(vert, 'fake')
fake_data()