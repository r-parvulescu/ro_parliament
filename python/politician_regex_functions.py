#Started June 16, 2017
#politician_regex_functions
#built for python 3

"""Tools for extracting regular expressions from htmls relating to politicians, all from the Romanian Chamber of Deputies.

For some reason this script isn't pinging PP-DD as admissible parties for deputy affiliation.

The flat HTML also tells me if they have been in the senate (or other CDEP mandates)."""

import regex as re
import misc_utilities as mu

def get_dep_ses(html):
    """Given an html that contains a list of deputies and their associated info, return a list of (name, url) tuples."""

    #extract deputy info
    all_dep_ses = []
    dep_inf_list = re.findall(r'<td width="5%" nowrap>(.*?)<td nowrap></td>', html, re.DOTALL)
    for d_inf in dep_inf_list:
        d_name = re.search(r'">(.*?)</A></b>',d_inf).group(1)
        d_url = re.search(r'<td><b><A HREF="(.*?)">', d_inf).group(1)
        all_dep_ses.append((d_name, d_url))
   
    return all_dep_ses

def bir_perm_info(html):
    """Checks if person is on the "birou permanent" and if so returns 
       a list with the roles they played and the associated date 
       ranges."""
    
    role_list = []
    bloc = re.search(r'<p><table border=0 width=\"100%\"><(.*?)</table></p>', html)
    if bloc != None:
        roles = re.findall(r'> - (.*?)</td><td style=\"padding: 2px;\">&', bloc.group(1))
        date_ranges = re.findall(r'[0-9]\">(.*?)</A>',bloc.group(1))
        out_of_term = re.findall(r'nbsp;- (.*?)</',bloc.group(1))
        for x in range(len(roles)):
            dt_rng = mu.convert_date_range(date_ranges[x])
            role_list.append((roles[x], dt_rng[0], dt_rng[1]))
        if len(out_of_term)>0:
            out_of_term = out_of_term.append("verify mid-term changes")
            role_list.append(out_of_term)

        if len(role_list)>0:
            list_skip = 0
            data_l =   ['',None,None,'',None,None,'',None,None,
                        '',None,None,'',None, None,'',None,None,
                        '',None,None,'',None,None,'',None,None,
                        '',None,None,[]]
            for x in range(len(role_list)):
                if isinstance(role_list[x], tuple):
                    data_l[list_skip] = role_list[x][0]
                    data_l[list_skip+1] = role_list[x][1]
                    data_l[list_skip+2] = role_list[x][2]
                    list_skip += 3
                else: 
                    data_l[-1] = role_list[x]    
            return data_l             
    else:
        data_l = ['',None,None,'',None,None,'',None,None,
                  '',None,None,'',None, None,'',None,None,
                  '',None,None,'',None,None,'',None,None,
                  '',None,None,[]]
        return data_l

def mandate_info(html):
    '''Gets info on the constituency the deputy represented, when their mandate was validated (this is only sometimes given) and when (if at all) their mandate ended before term.

    Returns a list of the form [constituency_name, constituency_number, constituency_legislature_url, mandate_validation_date, mandate_preterm_end_date]'''

    mandate_info = ['','','',None,None]
    dep_constit_bloc = re.search(r'<h3>DEPUTAT(.*?)</div>', html,re.DOTALL).group(1)
    mandate_info[0] = re.search(r'\">(.*?)</A>',dep_constit_bloc).group(1)
    constituency = re.search(r'nr.(.*?) <A',dep_constit_bloc)
    if constituency != None:
        mandate_info[1] = re.search(r'nr.(.*?) <A',
            dep_constit_bloc).group(1)       
    else:
        mandate_info[1] = 'minority seat'
    mandate_info[2] = re.search(r'HREF=\"(.*?)\">',
        dep_constit_bloc).group(1)
    validation_date = re.search(r'validarii: (.*?)<',
        dep_constit_bloc)
    if validation_date != None:
        mandate_info[3] = mu.convert_date_2(validation_date.group(1))
    preterm_end_date = re.search(r'\u00eencetarii mandatului: (.*?)<',
        dep_constit_bloc)
    if preterm_end_date != None:
        mandate_info[4] = mu.convert_date_2(preterm_end_date.group(1))
    return mandate_info

def party_info(html,start_leg, end_leg):
    '''Gets info on party(s) of which parliamentarian was a part, as well as the date ranges.

    Returns a list in the form [party_name_1, party_leg_url_1, affiliation_start_1, affiliation_end_1, party_name_2, party_leg_url_2, affiliation_start_2, affiliation_end_2, party_name_3, party_leg_url_3, affiliation_start_3, affiliation_end_3, party_name_4, party_leg_url_4, affiliation_start_4, affiliation_end_4, party_name_5, party_leg_url_5, affiliation_start_5, affiliation_end_5, party_name_6, party_leg_url_6, affiliation_start_6, affiliation_end_6]

    If dates for affiliation aren't given, we leave put in start and end dates of the legislature, which is the norm for party affiliation.'''

    prty_inf = ['','',None,None,'','',None,None,'','',None,None,
                '','',None,None, '','',None,None,'','',None,None]
    party_bloc = re.search(r'Formatiunea politica(.*?)</div>',
        html, re.DOTALL)
    if party_bloc == None:
        party_bloc = re.search(r'minoritatilor nationale:(.*?)</div>',html,re.DOTALL)
    p_cntr = 0
    parties = re.findall(r'"><td><A(.*?)</table',party_bloc.group(1))
    for p in parties:
        prty_inf[p_cntr] = re.search(r'">(.*?)</A>',p).group(1) #name
        prty_inf[p_cntr+1] = re.search(r'HREF=\"(.*?)\">',
            p).group(1) #url
        #party affiliation_start, if any
        p_start = re.search(r'din  (.*?)<',p)
        #party affiliation end, if any
        p_end = re.search(r'p\u00e2n\u0103 \u00een  (.*?)</td>',p)
        if p_start != None:
            prty_inf[p_cntr+2] = mu.convert_date(p_start.group(1))
        else:
            prty_inf[p_cntr+2] = start_leg
        if p_end != None:
            prty_inf[p_cntr+3] = mu.convert_date(p_end.group(1))
        else:
            prty_inf[p_cntr+3] = end_leg                 
        p_cntr += 4
    return prty_inf 


def get_name(html):
    """Extract deputy's name from summary page."""
    
    name = re.search(r'<title>(.*?)</title>',html).group(1)
    return name

def get_leg_dates(url):
    '''Given a certain url returns a tuple with the start and end dates of that legislature.''' 

    leg_dates = ''
    leg_1990 = ('19900521','19920927') #if on both dates 
    leg_1992 = ('19920928','19961015') #iffy on the start date
    leg_1996 = ('19961122','20001114')
    leg_2000 = ('20001211','20041206')
    leg_2004 = ('20041213','20081110')
    leg_2008 = ('20081215','20121120')
    leg_2012 = ('20121219','20161205')
    start_year = url[-10:-6]

    if start_year == '1990':
        leg_dates = leg_1992
    if start_year == '1992':
        leg_dates = leg_1992
    if start_year == '1996':
        leg_dates = leg_1996
    elif start_year == '2000':
        leg_dates = leg_2000
    elif start_year == '2004':
        leg_dates = leg_2004
    elif start_year == '2008':
        leg_dates = leg_2008
    elif start_year == '2012':
        leg_dates = leg_2012
    return leg_dates







    
