import pandas as pd
import time

from ETL import common
from bs4 import BeautifulSoup

from selenium.webdriver import Chrome, Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def save_bq(df):
    '''save possibles connection erros in a CSV file - ConnectError
        @df: dataframe with the erros'''
    stored_err = pd.read_csv('./ConnectError.csv')
    new_df = pd.concat([df,stored_err])
    new_df.to_csv('./ConnectError.csv',index=False)


def connect(lang, word, suffix, url=''):
    '''make a connection within a given link or with a wiki link suffix
        @lang: database type / wiki language
        @word: word to be search
        @suffix: last word of a wiki link - related with the word
        @url: a possible url to use - if empty, use suffix'''

    # Check lang
    if lang not in ['en','pt','es']:
        lang = 'en'

    # Get the link
    if url=='':
        url = 'https://' + lang + '.wikipedia.org/wiki/' + suffix
    print(f'\tBegining search on {word} on url - {url}')

    # Make the connection - it'll try 3 times (every 120 seconds), if didn't work it'll
    #   save a error in the CSV file and return empty - no connection make
    if common.IS_FIREFOX:
        options = FirefoxOptions()
        options.set_headless()
        with Firefox(executable_path=r'/home/salomao/DSProject/Wiki1Link/ETL/geckodriver', firefox_options=options) as browser:
            counter = 0
            while counter<3:
                browser.get(url)
                counter += 1
                try:
                    WebDriverWait(browser, 500).until(EC.visibility_of_element_located((By.ID, "bodyContent")))
                except TimeoutException:
                    if counter == 3: #save errors and return empty
                        df = pd.DataFrame({'word': word, 'href': suffix, 'language': lang, 
                                        'data': common.DATA_ATUAL, 'url': url,
                                        'err': 'TimeoutException'}, index=[0])
                        save_bq(df)
                        print('Erros salvos em: err')
                        return ''
                    time.sleep(120)
                    continue
                break 
            return browser.page_source
    if common.IS_CHROME:
        options = Options()
        options.add_argument('--headless')
        with Chrome('chromedriver', options=options) as browser:
            counter = 0
            while counter<3:
                browser.get(url)
                counter += 1
                try:
                    WebDriverWait(browser, 500).until(EC.visibility_of_element_located((By.ID, "bodyContent")))
                except TimeoutException:
                    if counter == 3: #save errors and return empty
                        df = pd.DataFrame({'word': word, 'href': suffix, 'language': lang, 
                                        'data': common.DATA_ATUAL, 'url': url,
                                        'err': 'TimeoutException'}, index=[0])
                        save_bq(df)
                        print('Erros salvos em: err')
                        return ''
                    time.sleep(120)
                    continue
                break 
            return browser.page_source

def get_possible_pages(browser, word):
    # Search for the possible page
    browser.find_element_by_name('search').send_keys(word)
    time.sleep(3)
    browser.find_element_by_name('search').send_keys(Keys.ENTER)
    time.sleep(3)
    
    # Extract the possible suffix from the page
    soup = BeautifulSoup(browser.page_source, "html.parser")
    suffix = soup.find("link", {'rel': 'alternate'})['href'].split('/')[-1]
    
    return suffix

def get_suffix(lang, word):
    '''search for the wikipedia suffix from a given word
        @lang: database type / wiki language
        @word: word to be search'''

    # Check lang
    if lang not in ['en','pt','es']:
        lang = 'en'

    # Get main wikipedia link
    url = 'https://' + lang + '.wikipedia.org'
    print(f'\tBegining search for the {word}\'s code...')

    # Make the connection with Firefox - has three chances and save the erros (same as above)
    if common.IS_FIREFOX:    
        options = FirefoxOptions()
        options.set_headless()
        with Firefox(executable_path=r'/home/salomao/DSProject/Wiki1Link/ETL/geckodriver', firefox_options=options) as browser:
            counter = 0
            while counter<3:
                browser.get(url)
                counter += 1
                try:
                    WebDriverWait(browser, 500).until(EC.visibility_of_element_located((By.ID, "searchform")))
                except TimeoutException:
                    if counter == 3: #save errors and return empty
                        df = pd.DataFrame({'word': word, 'href': '', 'language': lang, 
                                        'data': common.DATA_ATUAL, 'url': url,
                                        'err': 'TimeoutException'}, index=[0])
                        save_bq(df)
                        print('Erros salvos em: err')
                        return ''
                    time.sleep(120)
                    continue
                break
            
            return get_possible_pages(browser, word)
    
    # Make the connection with Chrome- has three chances and save the erros (same as above)
    if common.IS_CHROME:
        options = Options()
        options.add_argument('--headless')
        with Chrome('./chromedriver1', options=options) as browser:
            counter = 0
            while counter<3:
                browser.get(url)
                counter += 1
                try:
                    WebDriverWait(browser, 500).until(EC.visibility_of_element_located((By.ID, "searchform")))
                except TimeoutException:
                    if counter == 3: #save errors and return empty
                        df = pd.DataFrame({'word': word, 'href': '', 'language': lang, 
                                        'data': common.DATA_ATUAL, 'url': url,
                                        'err': 'TimeoutException'}, index=[0])
                        save_bq(df)
                        print('Erros salvos em: err')
                        return ''
                    time.sleep(120)
                    continue
                break
            
            return get_possible_pages(browser, word)
