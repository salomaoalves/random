import re
from ETL import connection, common
from ETL.extractWords import get_content, is_article_link, title_from_suffix
from bs4 import BeautifulSoup


def get_links(lang):
    '''return "Philosophy" wikipedia link for a database type / wiki language
        @lang: database type / wiki language'''
    lang = common.get_wiki_lang(lang)
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
    link = link.strip()
    if link=='':
        return get_links(lang)

    # Verify link
    lang = common.get_wiki_lang(lang)
    if not re.search('^(https?://)?(www\\.)?'+lang+'\\.(m\\.)?wikipedia\\.org/wiki/.+', link):
        return -1
    if not re.search('^https?://', link):
        link = 'https://' + link

    return link


def extract_new_words(html):
    '''extract blue words (start words) from a given html
        @html: the data'''

    # Get all possible word
    soup = BeautifulSoup(html, "html.parser")
    content = get_content(soup)
    if content is None:
        return [], []
    tags_a = [a for p in content.find_all("p") if p.find_parent('table') is None #skip infobox/tables
              for a in p.find_all('a') if is_article_link(a)]

    # Extract words and suffixes (end of a wiki link) - without duplicates
    words, suffixes = [], []
    for a in tags_a:
        suffix = a['href'].split('/wiki/')[-1].split('#')[0]
        word = title_from_suffix(suffix)
        if word not in words:
            words.append(word)
            suffixes.append(suffix)

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
    if html=='':
        return [], []

    return extract_new_words(html)
