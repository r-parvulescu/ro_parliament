#Started June 8, 2017
#scrapers.py
#built for python 3

"""Tools for scraping websites."""

import requests
import time
import random

def scrape(url):
    """Scrapes a website using the given url and returns a tuple with that url, its html and Unix time of the scrape."""

    #transparent and courteous scraping
    headers = {'user-agent' : 'Mozilla 53.0 (Linux Mint 17); Radu Parvulescu/Cornell University/rap348@cornell.edu'}
    time.sleep(1)
    html = requests.get(url, headers=headers).text
    time_retrieved = time.time()
    return (url, html, time_retrieved)

def list_scrape(lis, url_stem, elem = True):
    """Goes through a list of elements which, when appended to a stem, makes a valid url, scrapes the html of these urls, and returns of a list of tuples, each of the (url, html, time_retrieved) format."""

    uht_list = []
    for l in lis:
        url = url_stem + l
        url_html_time = scrape(url)
        #sometimes we want to associate with the element with its tuple
        if elem:
            uht_list.append((url_html_time, l))
    return uht_list

    
