from datetime import datetime, timedelta, timezone

DATA_ATUAL = datetime.now(timezone(timedelta(hours=-3)))
USER_AGENT = 'Wiki1Link/1.0 (https://github.com/salomaoalves/random)'

def get_stop_word(lang):
    '''return stop word ("Philosophy" node)
        @lang: database type'''
    if lang == 'en':
        return 'Philosophy'
    elif lang == 'pt':
        return 'Filosofia'
    elif lang == 'es':
        return 'Filosofía'
    else:
        return 'Philosophy'


def get_wiki_lang(lang):
    '''return the Wikipedia language for a database type - "fake" and unknown ones use English
        @lang: database type'''
    if lang not in ['en','pt','es']:
        return 'en'
    return lang
