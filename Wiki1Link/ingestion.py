from ETL import autoWords, extractWords, neo4jFunc
import common


def getAttrIng(type):
    '''get attrs for auto and costum ingestion
        @type: type of ingestion'''

    # Get Wiki language used
    lang = common.get_lang()

    # Get attrs: word and url sufix for custom and wiki url for auto
    if type=='costum':
        word = input('Write the target word: ').strip()
        suffix = input('Write the word suffix in url (PRESS Enter to None): ').strip()
    elif type=='auto':
        word = ''
        suffix = input('Wikipedia URL (PRESS Enter to None): ').strip()
    else:
        word, suffix = '', ''

    return lang, word, suffix


def ingest(lang, word, suffix, tab='\t'):
    '''call the extract process for a word, then handle the possible
        error cases and, if there are none, perform the ingestion'''
    new_vert, title = extractWords.main(lang, word, suffix)
    if new_vert=='':
        print(f'{tab}The {title} has no nodes.')
        return ''
    elif new_vert==-1:
        print(f'{tab}Word {title} already ingested.')
        return -1
    elif new_vert==-2:
        print(f'{tab}Wasn\'t able to connect with {title}.')
        return -2
    else:
        print(f'{tab}Word {word} founded, start ingestion')
        print(tab, end='')
        common.display(new_vert)
        neo4jFunc.insert_nodes(new_vert, lang)
        return new_vert


def costum_ingestion():
    # Get requires inputs
    lang, word, suffix = getAttrIng('costum')
    while word=='' and suffix=='':
        word = input('Write the target word: ').strip()

    # Call the extract process
    print(f'\n\nStart custom ingestion for word: {word}')
    return ingest(lang, word or suffix, suffix)


def auto_ingestion():
    # Get requires inputs
    while True:
        lang, _, link = getAttrIng('auto')
        words, suffixes = autoWords.main(lang, link)
        if words!=-1: #check for link error
            break
        else:
            print('!!!!!! WRONG LINK - need to be a wikipedia link!!!')

    # For each 'blue' word finded, call the extract process
    print('\n\nStarting Auto Ingestion process...')
    for i, (w, s) in enumerate(zip(words, suffixes)):
        print(f'\tWord: {w} - {i+1}/{len(words)}')
        ingest(lang, w, s, '\t\t')
