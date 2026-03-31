from ETL import autoWords, extractWords, neo4jFunc
import common


def getAttrIng(type):
    '''get attrs for auto and costum ingestion
        @type: type of ingestion'''

    # Get Wiki language used
    lang = common.get_lang()

    # Get attrs: word and url sufix for custom and wiki url for auto
    if type=='costum':
        word = input('Write the target word: ')
        suffix = input('Write the word suffix in url (PRESS Enter to None): ')
    elif type=='auto':
        word = ''
        suffix = input('Wikipedia URL (PRESS Enter to None): ')
    else:
        word, suffix = '', ''

    return lang, word, suffix


def costum_ingestion():
    # Get requires inputs
    lang, word, suffix = getAttrIng('costum')

    # Call the extract process
    print(f'\n\nStart custom ingestion for word: {word}')
    new_vert, word = extractWords.main(lang, word, suffix)
    
    # Handle the possible error cases of the extracted data, if there are none, perform the ingestion
    if new_vert=='':
        print(f'\tThe {word} has no nodes.')
        return ''
    elif new_vert==-1:
        print(f'\tWord {word} already ingested.')
        return -1
    elif new_vert==-2:
        print(f'\tWasn\'t able to connect with {word}.')
        return -2
    else:
        print(f'\tWord {word} founded, start ingestion')
        neo4jFunc.insert_nodes(new_vert)


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
    #  then, handle the possible error cases and perform the ingestion
    print('\n\nStarting Auto Ingestion process...')
    for w, s, i in words, suffixes, range(len(words)):
        print(f'\tWord: {w} - {i/len(words)}')
        new_vert = extractWords.main(lang, w, s)
        if new_vert=='':
            print(f'\t\tThe {w} has no nodes.')
        elif new_vert==-1:
            print(f'\t\tWord {w} already ingested.')
        elif new_vert==-2:
            print(f'\t\tWasn\'t able to connect with {w}.')
        else:
            print(f'\t\tWord {w} founded, start ingestion')
            neo4jFunc.insert_nodes(new_vert)