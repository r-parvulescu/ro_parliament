#Started June 8, 2017
#misc_utilities.py
#built for python 3

"""Miscellaneous utilities that I've found useful in the romparl project."""

import json
from collections import OrderedDict

def GetURL_HTML_Time(path):
    """Reads json file and returns the url, its html, and the Unix
       time of the scrape.

     PreC: Source must be some valid path string. 
           Reads line-delimited json file in current folder."""   

    f = open(path, 'r')
    for line in f:
        dictio = json.loads(line)
        url = dictio['url']
        html = dictio['html']
        scrape_time = dictio['scrape_time_utc']
    f.close()
        
    return (url, html, scrape_time)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""

    for i in range(0, len(l), n):
        yield l[i:i + n]

def StratifiedSample(lis,n,k):
    """Returns a stratified sample from a list "lis", where "n" is size of the stratum and "k" is sample size from each stratum."""

    #chunk
    index_chunks = list(chunks(range(0,len(lis)), n))  
    rand_indexes = []
    for l in index_chunks:
        rand_indexes.append(random.sample(l,k))

    #get list entries that correspond to those indexes
    rand_entries = []
    for samples in rand_indexes:
        for s in samples:
            rand_entries.append(ids[s])

    return rand_entries

def SplitName(text):

    """Splits name by space. First entry is the appellation (ex. "Mr."), which we throw out. Returns first/middle names and last name."""

    stripped = text.replace(':','').rstrip()
    names = stripped.split(" ")[1:]
    first_middle = names[:-1]
    last = names[-1]
    
    return(first_middle, last)

def SimpleTextMetrics(text):
    """Returns a tuple with simple metrics on a block of text."""

    #count the number of paragraphs/lines
    line_list = text.split("\n")
    num_lines = len(line_list)

    #count total number of words per paragraph/line
    num_words = 0
    num_word_per_p = []
    for l in line_list:
        l_word_list = l.split()
        l_num_words = len(l_word_list)
 
        num_words += l_num_words

    #average number of words per paragraph/line
    avg_line_length = num_words/num_lines

    return (num_words, num_lines, avg_line_length)   


def GetIDs(url):
    """The session, section, and subsection indentifiers are written in the url proper. This function gets and returns them as a tuple.

    A typical url: http://www.cdep.ro/pls/steno/steno2015.stenograma?ids=7791&idm=1,005&idl=1. The ids are "7791", "1,005" and "1". """

    id_section = url[50:]
    IDs = id_section.split("&")
    session_ID = IDs[0][4:]
    #a section (e.x., "2") might have a subsestion of the form "2,12"
    section_IDs = IDs[1][4:].split(",")
    if len(section_IDs) == 2:
        section_num = section_IDs[0]
        subsection_num = section_IDs[1]
    else:
        section_num = section_IDs[0]
        subsection_num = ""
    
    idl = IDs[2][4:] 

    return (session_ID, section_num, subsection_num, idl)

def GetSectionURLs(urls):
    """Reduces a list of cdep urls to one of only section urls, no duplicates."""

    #the html contains info for two levels of section ID, 
    #"1" then "1,10, 1,11, etc.". Keep only the lower level.
    reduced = []
    for x in range(1, (len(urls)-2)):

        #look at current
        id_section_a = urls[x][50:]
        IDs_a = id_section_a.split("&")
        ID_a = IDs_a[1][4:]

        #look at next
        id_section_b = urls[x+1][50:]
        IDs_b = id_section_b.split("&")
        ID_b = IDs_b[1][4:]

        #when "1" is followed by "1,01", "1,02", etc, how to include 
        #only the latter two, no duplication
        if (((",") not in ID_a) and (("," in ID_b) and (ID_a[0] == ID_b[0]))):
            reduced.append(urls_1[x+1])
        else:
           reduced.append(urls_1[x])

    #still have some duplicates, dedup   
    reduced = list(OrderedDict.fromkeys(urls_2))

    return reduced

def convert_date(text):
    '''Takes a date like "ian. 2010" and converts it to "20100101". Assumes that date begins on first of month.'''

    month_abbrev = ['ian', 'feb', 'mar', 'apr', 'mai', 'iun', 
                'iul', 'aug', 'sep', 'oct', 'noi', 'dec']
    mon_num = ['01', '02', '03', '04', '05', '06', '07',
                 '08', '09', '10', '11', '12'] 
    
    date_parts = text.split('. ')
    if len(date_parts) < 2:
        date_parts = text.split(' ')
    date_mon_num = mon_num[month_abbrev.index(date_parts[0])]
    date = date_parts[1] + date_mon_num + '01'
    return date

def convert_date_2(text):
    '''Take a date like "30 iunie      2004 - " and converts it to '20040630'. Unless otherwise specified, assumes the date starts on the first of the month.'''

    mon_name = ['ianuarie', 'februarie', 'martie', 'aprilie', 'mai', 
            'iunie', 'iulie', 'august', 'septembrie', 
            'octombrie', 'noiembrie', 'decembrie']
    mon_num = ['01', '02', '03', '04', '05', '06', '07',
                     '08', '09', '10', '11', '12'] 

    date_parts = text.split()
    date_mon_num = mon_num[mon_name.index(date_parts[1])]
    if len(date_parts[0]) == 1:
        date_parts[0] = '0' + date_parts[0]
    date = date_parts[2] + date_mon_num + date_parts[0]
    return date

def convert_date_range(date_range):
    """Takes a date range like "feb. - sep. 2014" or 
    'sep. 2014 - ian. 2015' and returns tuple like (20140201,20140901) 
    or (20140901, 20150101) respectively. Assumes that date begins on 
    first of month."""

    month_abbrev = ['ian', 'feb', 'mar', 'apr', 'mai', 'iun', 
            'iul', 'aug', 'sep', 'oct', 'noi', 'dec']
    mon_num = ['01', '02', '03', '04', '05', '06', '07', '08',
                 '09', '10', '11', '12'] 

    dt_rng = date_range.split(' - ')
    beta = dt_rng[1].split('.')
    end_mon_num = mon_num[month_abbrev.index(beta[0])]
    end_date = beta[1] + str(end_mon_num) + '01'

    alpha = dt_rng[0].split('.')
    start_mon_num = mon_num[month_abbrev.index(alpha[0])]
    if alpha[1]=='':
        start_date = beta[1] + str(start_mon_num)+'01'
    else:
        start_date = alpha[1] + str(start_mon_num) + '01'
    
    return (start_date, end_date)



def survival_rate(l,max_len):
    '''Given a list of tuples (deputy, [# and info on legislatures]), return multi-legislature survival lengtj of deputies.'''

    #figure out the longest term possible
    #max_len = 0
    #for dep in l:
    #    max_len = max(max_len,len(dep[1]))   

    num_deps = len(l)
    surv_len = []
    for x in range(2,max_len+1):
        counter = 0
        for dep in l:
            if len(dep[1]) == x:
                counter +=1
        #        print(dep)
        #print('der')
        surv_len.append((counter,'saw ' +str(x-1)+ ' more legislatures'))
    return(surv_len)
              
#the problem i have to solve here some other time is that it doesn't account for skipping legislatures, so that it would thing that ('Nicolaescu Gheorghe-Eugen', [(2000, '>=90'), (2008, '>=90'), (2012, '>=90')]) is just this guy serving three legislatures in a row. Since this is quite minor for now and I don't have time to deal, I'll ignore it.
