#Started June 8, 2017
#regex_functions.py
#built for python 3

"""Tools for extracting text of interest from html of sites of Romanian Chamber of Deputies."""

import regex as re
import misc_utilities as mu
from bs4 import BeautifulSoup as bs

def GetSectionInfo(html):

    """Extracts the date, chamber, session, section, and subsection names (if they exist) from an html."""

    date = ''
    chamber = ''
    session_name = ''
    section_name = ''
    subsection_name = ''

    date = convert_date(re.search(r'defaultDate: \"(.*?)\"', 
        html).group(1))
    session_name = re.search(r'<title>(.*?)</title>',html).group(1)
    chamber = 'CD'
    if "Senat" in session_name:
        chamber = 'CD+S'
    section_name = re.search((r'colspan=3 bgcolor=\"#fef9c2\"><b>(.*?)</b></td>'), html, re.DOTALL).group(1)

    subsection = re.search(r'<td width="100%" bgcolor="#fffef2"><b>(.*?);</b></td>', html)
    if subsection != None:
       subsection_name = subsection.group(1)

    return (date, chamber, session_name, section_name, subsection_name)

def convert_date(text):
    '''Takes a date like 1998-02-03 and returns 19980203.'''

    if '-' in text:
        parts = text.split('-')
        date = parts[0]+parts[1]+parts[2]
        return date
    else:
        return text

def GetSpeech(text):

    """Extract a parliamentary speech from text."""

    raw_text = text.partition('-->\n')[2]
    soup = bs(raw_text, 'html.parser')
    txt = soup.get_text()    

    return txt
    
def GetUttererNameURL(html,s):

    """Get utterer name and url to parliamentarian website. These can ocurr in irregular places, if at all.

    Note: the parameter "s" is a predefined bloc of text."""

    utterer_first_middle = ''
    utterer_last = ''
    utterer_url = ''
    utterer_extra_info = ''

    #normally all info is the bloc defined by the "s" parameter, 
    #get name, if any
    name = re.search((r'F\">Do(.*?)</font'), s)
    if name != None:
        full_name = mu.SplitName(name.group(1))
        utterer_first_middle = full_name[0]
        utterer_last = full_name[1]

    #if it's not in the bloc, it's outside. Seek it there.
    elif name == None:
        out_name = re.search((r'F\">Do(.*?)</font'), html) 
        out_name_beta = re.search((r'F\">Do(.*?):</td>'), html)

        if out_name != None:   
            full_name = mu.SplitName(out_name.group(1))
            utterer_first_middle = full_name[0]
            utterer_last= full_name[1]

        elif out_name_beta != None: 
            full_name = mu.SplitName(out_name_beta.group(1))
            utterer_first_middle = full_name[0]
            utterer_last = full_name[1]   

    #get URL, if any
    url = re.search(r'<p align="justify"><B><A HREF="(.*?)"', s)
    if url != None:
        utterer_url = url.group(1)
    elif url == None:
        possible_url = re.search(r'<td><P><B><a href="(.*?)" target', html)
        if possible_url != None:
            utterer_url = possible_url.group(1)
    
    #get extra info, if any
    extra_info = re.search(r'<I>(.*?)</I>:', s)
    if extra_info != None:
        utterer_extra_info = extra_info.group(1)

    #when there is no speaker info in the first bloc, seek it here
    #f re.search((r'F\">Do(.*?)</font'), s) == None:
        #re.search(r'<td><P><B><a href=(.*?) target', html) != None:

    #f_m_n needs to be a list so I can pass it on without error
    if isinstance(utterer_first_middle, list) == False:
        utterer_first_middle = [utterer_first_middle]

    return (utterer_first_middle, utterer_last, utterer_url, 
               utterer_extra_info)

def GetUtteranceID(text):
    """Gets the unique ID associated with an utterance."""
    
    id_full = re.search(r'T=(.*?) -->', text).group(1)
    #this first chunk of the id looks like the most sensical 
    id_first = int(id_full.split(',')[0])

    return (id_first, id_full)

def UtternaceInfo(url, html):
    """Returns a list of dictionaries, each of which contains the text of and info about one cdep transcript elemental utterance.

    PreC: Input is some html plus the url from which it was scraped."""

    all_elem_utterances = []
    IDs = mu.GetIDs(url)
    se_inf = GetSectionInfo(html)

    #the elemental unit is usually the one defined by this regex
    #need to split this number by comma
    utterances = re.findall(r'<!-- STAR(.*?)<!-- END -->',
                   html, re.DOTALL)
    for s in utterances:
        utterance = {}
        ut_id = GetUtteranceID(s)  
        ut_inf = GetUttererNameURL(html,s)
        text = GetSpeech(s)

        #dump in dict
        utterance.update({'utterance_id_first':ut_id[0], 
            'utterance_id_full':ut_id[1],
            'utterer_url':ut_inf[2], 
            'utterer_first_middle_name':ut_inf[0],
            'utterer_last_name':ut_inf[1],
            'utterer_extra_info':ut_inf[3],'utterance_text':text,
            'date':se_inf[0], 'chamber':se_inf[1],  
            'session_ID':IDs[0], 'session_name':se_inf[2], 
            'section_name':se_inf[3], 'section_num':IDs[1], 
            'subsection_name':se_inf[4], 'subsection_num':IDs[2], 
            'idl':IDs[3]})

        all_elem_utterances.append(utterance) 

    return all_elem_utterances


#keys in utterance dict: utterer_url, utterer_name, utterer_extra_info, utterance_id, text, date, chamber, session_ID, session_name, section_name, section_num, subsection_name, subsection_num
