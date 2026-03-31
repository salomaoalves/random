import re
from Wiki1Link.ETL import connection
from bs4 import BeautifulSoup

DATA_ATUAL = connection.DATA_ATUAL


def get_links(lang):
    '''return "Philosophy" wikipedia link for a database type / wiki language
        @lang: database type / wiki language'''
    if lang not in ['en','pt','es']:
        lang = 'en'
    if lang == 'en':
        return 'https://en.wikipedia.org/wiki/Philosophy'
    elif lang == 'pt':
        return 'https://pt.wikipedia.org/wiki/Filosofia'
    elif lang == 'es':
        return 'https://es.wikipedia.org/wiki/Filosof%C3%ADa'


def check_link(lang, link):
    '''Checks a certain link - whether it is valid or not
       If a empty link is passed, the "Philosophy" link is returned
        @lang: database type
        @link: the link'''

    # Empty link
    if link=='':
        link = get_links(lang)

    # Verify link
    else:
        if not re.search('^https://'+lang+'.wikipedia.org/wiki|^http://'+lang +'.wikipedia.org/wiki|^'+lang+'.wikipedia.org/wiki|^'+lang+'.wikipedia.org', link):
            return -1
        if re.search('^'+lang+'.wikipedia.org', link):
            link = 'https://' + link
        if re.search('^'+lang+'.wikipedia.org', link):
            link = 'https://www.' + link

    return link


def extract_new_words(html):
    '''extract blue words (start words) from a given html
        @html: the data'''

    # Get all possible word
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find("div", {'class': 'mw-parser-output'}).find_all("p")
    tags_a = paragraphs.find_all('a')

    # Extract words and suffixes (end of a wiki link)
    words = [a.text for a in tags_a if 'citi_note' not in a['href']]
    suffixes = [a['href'].split('/')[-1] for a in tags_a if 'citi_note' not in a['href']]
    
    return words, suffixes



def main(lang, link):
    '''start to extract blue words from a given wiki link
        @lang: database type
        @link: the link'''

    # Verify link
    link = check_link(lang, link)
    if link==-1:
        return -1, -1

    # Get html
    html = connection.connect(lang, 'AutoIngest', '', link)

    return extract_new_words(html)