import csv
import os
import time
from urllib.parse import unquote

import requests

from ETL import common

ERROR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ConnectError.csv')
N_TRIES, WAIT_SECONDS, TIMEOUT = 3, 10, 30


def save_bq(row):
    '''save possibles connection erros in a CSV file - ConnectError
        @row: dict with the error'''
    fields = ['word', 'href', 'language', 'data', 'url', 'err']
    write_header = not os.path.exists(ERROR_FILE)
    with open(ERROR_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def request(lang, word, suffix, url, params=None):
    '''make a GET request - it'll try 3 times, if didn't work it'll
        save a error in the CSV file and return None
        @lang: database type / wiki language
        @word: word to be search
        @suffix: last word of a wiki link - related with the word
        @url: the url
        @params: query string params'''
    err = ''
    for counter in range(N_TRIES):
        try:
            resp = requests.get(url, params=params, timeout=TIMEOUT,
                                headers={'User-Agent': common.USER_AGENT})
            if resp.status_code == 200:
                return resp
            err = f'HTTP {resp.status_code}'
            if resp.status_code == 404: #page doesn't exist, no reason to try again
                break
        except requests.RequestException as e:
            err = type(e).__name__
        if counter < N_TRIES-1:
            time.sleep(WAIT_SECONDS)

    save_bq({'word': word, 'href': suffix, 'language': lang,
             'data': common.DATA_ATUAL, 'url': url, 'err': err})
    print(f'\tErros salvos em: {ERROR_FILE}')
    return None


def connect(lang, word, suffix, url=''):
    '''make a connection within a given link or with a wiki link suffix
        @lang: database type / wiki language
        @word: word to be search
        @suffix: last word of a wiki link - related with the word
        @url: a possible url to use - if empty, use suffix'''

    lang = common.get_wiki_lang(lang)

    # Get the link
    if url=='':
        url = 'https://' + lang + '.wikipedia.org/wiki/' + suffix
    print(f'\tBegining search on {word} on url - {url}')

    resp = request(lang, word, suffix, url)
    return resp.text if resp is not None else ''


def get_suffix(lang, word):
    '''search for the wikipedia suffix from a given word - uses the
        Wikipedia search, that redirects to the article when it exists
        @lang: database type / wiki language
        @word: word to be search'''

    lang = common.get_wiki_lang(lang)
    url = 'https://' + lang + '.wikipedia.org/w/index.php'
    print(f'\tBegining search for the {word}\'s code...')

    resp = request(lang, word, '', url, params={'search': word, 'go': 'Go'})
    if resp is None or '/wiki/' not in resp.url:
        return ''
    suffix = resp.url.split('/wiki/')[-1].split('#')[0]
    if unquote(suffix).startswith('Special:'): #search result page - no article found
        return ''
    return suffix
