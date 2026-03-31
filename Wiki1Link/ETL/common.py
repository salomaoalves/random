import pytz
from datetime import datetime, timedelta

DATA_ATUAL = datetime.now(pytz.utc) + timedelta(hours=-3)
IS_FIREFOX = True
IS_CHROME = False

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