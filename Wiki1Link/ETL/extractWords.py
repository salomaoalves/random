import re
from ETL import neo4jFunc, connection, common
from bs4 import BeautifulSoup


def from_str_to_list(string):
    '''each caracther is a element'''
    l_parag = []
    l_parag[:0] = string
    return l_parag

def from_list_to_str(l_parag):
    '''inverse of the above'''
    return ''.join(l_parag)



def delete_paren_text(l_parag, open_paren, close_paren):
    '''return the paragh without a certain parenthesis and that same parenthesis'''

    # Get parenthesis text
    paren_parag = l_parag[open_paren:close_paren+1]
    
    # Delete the parenthesis text from the paragraph
    del(l_parag[open_paren:close_paren+1])

    return l_parag, paren_parag


def get_all_text_paren(l_parag):
    '''return all string between any parenthesis in a paragraph
        @l_parag: the paragraph in list format'''

    parag_with_paren, is_done = [], False

    while True:
        # Get parenthesis coordenation
        try:
            open_paren = l_parag.index('(')
        except ValueError:
            is_done = True
        try:
            close_paren = l_parag.index(')')
        except ValueError:
            is_done = True

        # While exist, extract text between parenthesis
        if not is_done:
            current_parenthesis = l_parag[open_paren+1:close_paren+1]
            while re.search("\(", ' '.join(current_parenthesis)):
                l_parag[current_parenthesis.index('(')] = '.'
                close_paren = l_parag[close_paren+1:].index(')')
            l_parag, parag_with_paren_temp = delete_paren_text(l_parag, open_paren, close_paren)
            parag_with_paren.append(parag_with_paren_temp)
        else:
            return parag_with_paren

def check_match(possible_word, l_parag_with_paren):
    '''Verify if a possible blue word belongs to a text between some parenthesis
        @possible_word: possible blue words - str format
        @l_parag_with_paren: list of the text in a paragraph'''

    l_parag = re.sub("[;:.,><\[\]{}/][ \xa0]", " ", from_list_to_str(l_parag_with_paren[1:-1])).split(' ')
    l_possible_word = re.sub("[;:.,><\[\]{}/] ", " ", possible_word).split(' ')
    qty_word, match_sum = len(l_possible_word), 0
    for i in range(qty_word):
        if l_possible_word[i] in l_parag:
            match_sum += 1
        elif l_possible_word[i][-1] in ['v']:
            if l_possible_word[i][:-1] in l_parag:
                match_sum += 1
    if match_sum == qty_word:
        return True
    else:
        return False

def verify_word(ll_parag_with_paren, l_possible_word, l_possible_suffix):
    '''Try to find the node word - blue words inside of any parenthesis are invalid
        @ll_parag_with_paren: list of list with the text in the parenteshis
        @l_possible_word: list of blue words
        @l_possible_suffix: list of the blue words suffix'''

    # Check if the possibles words are valid. Start from the first blue word finded,
    #   it'll test if it's belongs to any parenthesis text; if it's True, delete the current one
    #   and try the next possible blue word, if Not, verify in the next parenthesis
    word_index, parag_index = 0, 0
    while True:
        next_paren = True
        if parag_index == len(ll_parag_with_paren): #no more paragraph to verify - exit
            break
        if check_match(l_possible_word[word_index], ll_parag_with_paren[parag_index]): #if belongs to the parenthesis text
            del(l_possible_word[word_index])
            del(l_possible_suffix[word_index])
            next_paren = False
        if next_paren: #if go to next parenthesis
            parag_index += 1

    # Return the fisrt possible blue word - if any is left
    if len(l_possible_word) == 0:
        return '', '', False
    else:
        return l_possible_word[0], l_possible_suffix[0], True


def get_word(html, parag_numb=0):
    '''try to find some valid blue word / node - it'll try per paragrah in the page
        @html: the page
        @parag_numb: paragraph to try'''

    possible_word, possible_suffix, parag_with_paren = [], [], []

    # Get the paragraph and transform in list format
    soup = BeautifulSoup(html, "html.parser")
    paragraph = soup.find("div", {'class': 'mw-parser-output'}).find_all("p")[parag_numb]
    tags_a = paragraph.find_all('a')
    convert_parag = from_str_to_list(paragraph.text)

    # Get all blue words in the parag
    for tag in tags_a:
        if '[' not in tag.text:
            possible_word.append(tag.text)
            possible_suffix.append(tag['href'].split('/')[-1])
    
    # Exit if find nothing
    if len(possible_word) == 0:
        return '', '', False, parag_numb+1
    
    # Check if any blue word is valid
    parag_with_paren = get_all_text_paren(convert_parag)
    word, suffix, found = verify_word(parag_with_paren, possible_word, possible_suffix)
    
    if found: #valid
        return word, suffix, True, -1
    else:     #invalid
        return '', '', False, parag_numb+1



def main(lang, word, suffix):
    '''extract nodes from a given word to be ingested
        @lang: database type
        @word: start word
        @suffix: wiki link suffix of the word'''

    # Get attributes
    new_vert, stop_word = [word], common.get_stop_word(lang)
    cond_word, cond_loop = False, False
    ingested_word = neo4jFunc.get_all_nodes(lang)

    # If empty, find a possible suffix
    if suffix=='':
        suffix = connection.get_suffix(lang, word)

    # Check if word is already ingested
    if word in ingested_word:
        return -1, word

    # Get all words/vertices
    while True:

        # Make connection and treat any error
        html = connection.connect(lang, word, suffix)
        if html=='':
            return -2, word
        
        # Find the next node (blue word) - try until find
        new_word, suffix, found, parag_numb = get_word(html)
        while not found:
            new_word, suffix, found, parag_numb = get_word(html, parag_numb)
        
        # Find Philosophy word - Stop Cond 1
        if suffix == stop_word:
            cond_word = True

        # Word already ingested or to be ingested - Stop Cond 2
        if new_word in new_vert + ingested_word:
            cond_loop = True
        
        # Add new vert in the list of vert
        new_vert.append(new_word)

        # Verify 'Stop Conditions'
        if cond_word or cond_loop:
            break
        else:
            word = new_word
    
    return new_vert, ''
