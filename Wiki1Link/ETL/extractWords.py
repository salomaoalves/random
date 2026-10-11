from urllib.parse import unquote
from ETL import neo4jFunc, connection, common
from bs4 import BeautifulSoup, NavigableString

# Wikipedia namespaces (en, pt, es) - links to them aren't articles
NAMESPACES = {
    'file', 'image', 'ficheiro', 'arquivo', 'imagem', 'archivo', 'imagen',
    'help', 'ajuda', 'ayuda', 'wikipedia', 'wikipédia', 'wp',
    'category', 'categoria', 'categoría', 'template', 'predefinição', 'plantilla',
    'portal', 'special', 'especial', 'talk', 'discussão', 'discusión',
    'user', 'usuário', 'usuario', 'utilizador', 'module', 'módulo',
    'mediawiki', 'anexo', 'wiktionary', 'wikcionário', 'wikcionario', 'draft',
}


def title_from_suffix(suffix):
    '''transform a wiki link suffix in the page title
        e.g. "Oi_(empresa)" -> "Oi (empresa)"'''
    return unquote(suffix.split('#')[0]).replace('_', ' ')


def get_content(soup):
    '''return the article body of a wiki page'''
    content = soup.select_one('#mw-content-text .mw-parser-output')
    if content is None:
        content = soup.find("div", {'class': 'mw-parser-output'})
    return content


def get_page_title(soup):
    '''return the title of a wiki page - after any redirect'''
    canonical = soup.find('link', {'rel': 'canonical'})
    if canonical is not None and '/wiki/' in canonical.get('href', ''):
        return title_from_suffix(canonical['href'].split('/wiki/')[-1])
    heading = soup.find(id='firstHeading')
    if heading is not None:
        return heading.get_text().strip()
    return ''


def is_article_link(tag):
    '''check if a <a> tag links to another wikipedia article'''
    href = tag.get('href', '')
    if not href.startswith('/wiki/') or 'new' in tag.get('class', []): #external or red link
        return False
    title = title_from_suffix(href[len('/wiki/'):])
    if title == '':
        return False
    if ':' in title and title.split(':')[0].strip().lower() in NAMESPACES:
        return False
    return True


def first_valid_link(paragraph):
    '''return the first article link of a paragraph that isn't inside a parenthesis
        @paragraph: the <p> tag'''
    depth = 0
    for el in paragraph.descendants:
        if isinstance(el, NavigableString):
            # Text inside links (e.g. "Oi (empresa)") and styles doesn't open/close parenthesis
            if el.parent.name in ['style', 'script'] or el.find_parent('a') is not None:
                continue
            for c in el:
                if c == '(':
                    depth += 1
                elif c == ')' and depth > 0:
                    depth -= 1
        elif el.name == 'a' and depth == 0 and is_article_link(el) \
                and el.find_parent(['sup', 'small']) is None:
            return el
    return None


def get_word(html):
    '''try to find the first valid blue word / node - it'll try per paragrah in the page
        @html: the page'''

    soup = BeautifulSoup(html, "html.parser")
    content = get_content(soup)
    if content is None:
        return '', '', False

    for paragraph in content.find_all("p"):
        if paragraph.find_parent('table') is not None: #skip infobox/tables
            continue
        tag = first_valid_link(paragraph)
        if tag is not None:
            suffix = tag['href'][len('/wiki/'):].split('#')[0]
            return title_from_suffix(suffix), suffix, True

    return '', '', False


def main(lang, word, suffix):
    '''extract nodes from a given word to be ingested
        @lang: database type
        @word: start word
        @suffix: wiki link suffix of the word'''

    # Get attributes
    new_vert, stop_word = [], common.get_stop_word(lang)
    ingested_word = neo4jFunc.get_all_nodes(lang)

    # If empty, find a possible suffix
    if suffix=='':
        suffix = connection.get_suffix(lang, word)
        if suffix=='':
            return -2, word

    # Get all words/vertices
    while True:

        # Make connection and treat any error
        html = connection.connect(lang, word, suffix)
        if html=='':
            if len(new_vert)==0:
                return -2, word
            break

        # The node name is the page title - so redirects/different texts are the same node
        title = get_page_title(BeautifulSoup(html, "html.parser")) or word

        # Check if the start word is already ingested
        if len(new_vert)==0 and title in ingested_word:
            return -1, title

        # Find Philosophy word - Stop Cond 1
        cond_word = title == stop_word

        # Word already ingested or to be ingested - Stop Cond 2
        cond_loop = title in new_vert or title in ingested_word

        # Add new vert in the list of vert
        new_vert.append(title)

        # Verify 'Stop Conditions'
        if cond_word or cond_loop:
            break

        # Find the next node (blue word)
        word, suffix, found = get_word(html)
        if not found: #page without any valid link - end of the path
            break

    if len(new_vert) < 2:
        return '', new_vert[0] if new_vert else word
    return new_vert, ''
