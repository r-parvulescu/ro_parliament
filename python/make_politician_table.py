#Started June 16, 2017  
#make_politician_table.py
#built for python 3

"""Tools for scraping and storing information biographical information on members of the Romanian Chamber of Deputies, from the website of that entity."""

import psycopg2
import json
import os
import misc_utilities as mu
import scrapers as scrp
import politician_regex_functions as prf
import folder_table_tools as ftt
import scrapers as sc
import traceback
import time
import csv

def scrape_list_sites():
    """Scrapes the sites that list all the parliamentarians serving in a specific session, dumps the url, html, and scrape time in a file."""

    #scrape the sites that list the deputies by session start-year
    years = ['1990','1992','1996','2000','2004','2008','2012','2016']
    url_stem = "http://www.cdep.ro/pls/parlam/structura2015.de?leg="
    uht_list = scrp.list_scrape(years, url_stem)

    #dump data in folder
    fldr = "/media/radu/romparl/CD/htmls/politicians/session_lists/"
    for uht in uht_list:
        fil = str(uht[1]) + '-dep_list.txt'
        dictio = {'url':uht[0][0], 'html':uht[0][1], 
            'scrape_time_utc':uht[0][2]}
        ftt.json_file_dump(fldr, fil, dictio)
    

def scrape_dep_sites():
    """Scrapes two of the websites associated with deputy-sessions, the CV and overview sites, and dumps the htmls in folder."""

    scrape_counter = 0

    #load urls in list
    db_name_user = 'dbname=romparl user=radu'
    table_command = 'SELECT dep_name, dep_url FROM dep_name_url'
    urls = ftt.get_list_from_table(db_name_user, table_command)

    cv_fldr = "/media/radu/romparl/CD/htmls/politicians/cv_pages/" 
    smry_fldr = "/media/radu/romparl/CD/htmls/politicians/summary_pages/"
    err_fldr = "/media/radu/romparl/CD/errors/"

    #go thorugh urls and scrape, ignore 2016 session, no CVs yet
    for u in urls:
        if '2016' not in u[1]:
            session = u[1][-4:]
            scrape_counter += 1
            print(u[0], session, scrape_counter)
            cv_u = u[1] + '&pag=0'
            cv_file = str(u[0]) + '-' + session + '-cv.txt'
            smry_u = u[1] + '&pag=1'
            smry_file = str(u[0]) + '-' + session + '-summary.txt'

            try:
                cv_uht = sc.scrape(cv_u)
                cv_dictio = {'url':cv_uht[0], 'html':cv_uht[1], 
                    'scrape_time_utc':cv_uht[2]}
                ftt.json_file_dump(cv_fldr, cv_file, cv_dictio)

                smry_uht = sc.scrape(smry_u)
                smry_dictio = {'url':smry_uht[0], 'html':smry_uht[1], 
                    'scrape_time_utc':smry_uht[2]}
                ftt.json_file_dump(smry_fldr, smry_file, smry_dictio)

            except:
                err_file = str(u[0]) + '.txt'
                tb = traceback.format_stack()
                error = {'message':tb, 'error_index':scrape_counter, 
                    'list_element':u[0]}
                ftt.json_file_dump(err_fldr, err_file, error)
                continue

def fill_dep_url_table(conn, cur):
    """Reads files, extract name and url of deputy-session, dumps in postgres table. Needs valid connection and cursor."""
    
    sql = "INSERT INTO dep_name_url (dep_name, dep_url) VALUES (%s, %s)"

    #load files, dump relevant contents in table
    fldr = "/media/radu/romparl/CD/htmls/politicians/session_lists/"
    for FILE in os.listdir(fldr):
        uht = mu.GetURL_HTML_Time(fldr + FILE)
        deps = prf.get_dep_ses(uht[1])
        for dep in deps:
            url = 'http://www.cdep.ro' + dep[1]
            data = (dep[0], url)
            try:
                cur.execute(sql,data)
            except:
                cur.close()
                conn.close()

    #make table of deputy-sessions and urls
    #cur.execute("CREATE TABLE dep_name_url(id serial PRIMARY KEY, dep_name text, dep_url text);")

def make_dep_table(conn,cur):
    """Reads files, extracts relevant info, dumps in postgres table. 
    Needs valid connection and cursor."""

    sql_0 = "INSERT INTO parliamentarians_elemental (name, legislature_start, chamber, url_stem, summary_url_suffix, summary_scrape_time, summary_html) VALUES (%s, %s, %s, %s, %s, %s, %s)"
   
    commit_counter = 0

    fldr = "/media/radu/romparl/CD/htmls/politicians/summary_pages/"
    for FILE in os.listdir(fldr):
        print(FILE)
        uht = mu.GetURL_HTML_Time(fldr + FILE)
        
        url_stem = uht[0][18:-6]
        summary_url_suffix = '&pag=1'
        leg_dates = prf.get_leg_dates(uht[0])
        name = prf.get_name(uht[1])
        chamber = 'CD'
        gnrl_info = [name, leg_dates[0], chamber, url_stem, 
            summary_url_suffix, uht[2], uht[1]]
        bir_perm_role_info = prf.bir_perm_info(uht[1])      
        mandate_info = prf.mandate_info(uht[1])  
        party_info = prf.party_info(uht[1],leg_dates[0],leg_dates[1])

        sql_1 = "UPDATE parliamentarians_elemental SET (constituency_name, constituency_number, constituency_legislature_url, mandate_validation_date, mandate_preterm_end_date) = (%s, %s, %s, %s, %s) WHERE name =" + "'" + name + "'" + ";"

        sql_2 = "UPDATE parliamentarians_elemental SET (party_name_1, party_leg_url_1, party_1_start, party_1_end, party_name_2, party_leg_url_2, party_2_start, party_2_end, party_name_3, party_leg_url_3, party_3_start, party_3_end, party_name_4, party_leg_url_4, party_4_start, party_4_end, party_name_5, party_leg_url_5, party_5_start, party_5_end, party_name_6, party_leg_url_6, party_6_start, party_6_end) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE name =" + "'" + name + "'" + ";"

        sql_3 = "UPDATE parliamentarians_elemental SET (bir_perm_role_1, brp_1_start, brp_1_end, bir_perm_role_2, brp_2_start, brp_2_end, bir_perm_role_3, brp_3_start, brp_3_end, bir_perm_role_4, brp_4_start, brp_4_end, bir_perm_role_5, brp_5_start, brp_5_end, bir_perm_role_6, brp_6_start, brp_6_end, bir_perm_role_7, brp_7_start, brp_7_end, bir_perm_role_8, brp_8_start, brp_8_end, bir_perm_role_9, brp_9_start, brp_9_end, bir_perm_role_10, brp_10_start, brp_10_end, brp_term_changes) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s) WHERE name =" + "'" + name + "'" + ";"

        #try:
        cur.execute(sql_0, gnrl_info)
        cur.execute(sql_1, mandate_info)
        cur.execute(sql_2, party_info)
        cur.execute(sql_3, bir_perm_role_info)
        #except:
        #    cur.close()
        #    conn.close()

        #commit_counter += 1
        #if commit_counter % 50 == 0:
            #conn.commit()

        # note that your code doubles up the number of poeple in the 1992 legislature for some reason

#sql code to make the 'parliamentarians_elemental' table
#CREATE TABLE parliamentarians_elemental(id serial PRIMARY KEY, name text, legislature_start text, chamber text, url_stem text, summary_url_suffix text, summary_scrape_time bigint, summary_html text, constituency_name text, constituency_number text, constituency_legislature_url text, mandate_validation_date date, mandate_preterm_end_date date, party_name_1 text, party_leg_url_1 text, party_1_start date, party_1_end date, party_name_2 text, party_leg_url_2 text, party_2_start date, party_2_end date, party_name_3 text, party_leg_url_3 text, party_3_start date, party_3_end date, party_name_4 text, party_leg_url_4 text, party_4_start date, party_4_end date, party_name_5 text, party_leg_url_5 text, party_5_start date, party_5_end date, party_name_6 text, party_leg_url_6 text, party_6_start date, party_6_end date, bir_perm_role_1 text, brp_1_start date, brp_1_end date, bir_perm_role_2 text, brp_2_start date, brp_2_end date, bir_perm_role_3 text, brp_3_start date, brp_3_end date, bir_perm_role_4 text, brp_4_start date, brp_4_end date, bir_perm_role_5 text, brp_5_start date, brp_5_end date, bir_perm_role_6 text, brp_6_start date, brp_6_end date, bir_perm_role_7 text, brp_7_start date, brp_7_end date, bir_perm_role_8 text, brp_8_start date, brp_8_end date, bir_perm_role_9 text, brp_9_start date, brp_9_end date, bir_perm_role_10 text, brp_10_start date, brp_10_end date, brp_term_changes text[]);

def make_r_table():
    '''Since I can't write FOR loops in sql I have to shit here.'''

    db_name_user = "dbname=romparl user=radu"    

    sql_1 = "SELECT name, legislature_start, percentile FROM dep_leg_perc ORDER BY name, legislature_start, percentile"

    #load a dictionary into python from dep_leg_perc
    conn = psycopg2.connect(db_name_user)
    cur = conn.cursor()
    #read coloumn
    try:
        cur.execute(sql_1)
    except:
        cur.close()
        conn.close()         
    #load entries into list
    d = {}
    for row in cur:
        if row[0] in d:
           d[row[0]].append((row[1],row[2])) 
        else:
            d[row[0]] = []
            d[row[0]].append((row[1],row[2]))

    cur.close()
    conn.close()

    """ 
All of this works well for putting into postgres but I have some permission problem where I can't export the postgres file so fuck it, we'll just dump in a csv through python.
   #then insert into another table thusly
    sql_2 = "INSERT INTO r_export (name, _1996, _2000, _2004, _2008, _2012) VALUES (%s, %s, %s, %s, %s, %s)"

    for key, value in d.items():
        data = ['','nil','nil','nil','nil','nil']
        data[0] = key 
        for sub in value:
            if sub[0] == 1996:
                data[1] = sub[1]
            elif sub[0] == 2000:
                data[2] = sub[1]
            elif sub[0] == 2004:
                data[3] = sub[1]
            elif sub[0] == 2008:
                data[4] = sub[1]
            elif sub[0] == 2012:
                data[5] = sub[1]
        #print(data)    

        try:
            cur.execute(sql_2,data)
        except:
            cur.close()
            conn.close()

    conn.commit()
    cur.close()
    conn.close()
    #print(l)
    #return l
    """

    #f =  open('/media/radu/romparl/CD/csv/dep_leg_word_perc.csv','w')
    #wr = csv.writer(f, quoting=csv.QUOTE_ALL)

    ID = 0
    headers = ['name', '_1996', '_2000', '_2004', '_2008', '_2012', 'ID']
    #wr.writerow(headers)
    for key, value in d.items():
        print(value)
        ID += 1
        data = ['','nil','nil','nil','nil','nil',ID]
        data[0] = key 
        for sub in value:
            if sub[0] == 1996:
                data[1] = sub[1]
            elif sub[0] == 2000:
                data[2] = sub[1]
            elif sub[0] == 2004:
                data[3] = sub[1]
            elif sub[0] == 2008:
                data[4] = sub[1]
            elif sub[0] == 2012:
                data[5] = sub[1]
        #print(data)
    #    wr.writerow(data)
    #f.close()

def get_big_talkers():
    '''Now I have to get all the people who spoke in the big two categories'''

    db_name_user = "dbname=romparl user=radu"    

    sql_1 = "SELECT name, legislature_start, percentile FROM dep_leg_perc ORDER BY name, legislature_start, percentile"

    #load a dictionary into python from dep_leg_perc
    conn = psycopg2.connect(db_name_user)
    cur = conn.cursor()
    #read coloumn
    try:
        cur.execute(sql_1)
    except:
        cur.close()
        conn.close()         
    #load entries into list
    d = {}
    for row in cur:
        if row[0] in d:
           d[row[0]].append((row[1],row[2])) 
        else:
            d[row[0]] = []
            d[row[0]].append((row[1],row[2]))

    cur.close()
    conn.close() 

    start_96 = []
    start_00 = []
    start_04 = []
    start_08 = []
    for key, value in d.items():
        #if value[0][1] == ('>=90'): #or value[0][1] == ('50-89'):
        if value[0][0] == 1996:
            start_96.append((key,value))
        elif value[0][0] == 2000:
            start_00.append((key,value))
        elif value[0][0] == 2004:
            start_04.append((key,value))
        elif value[0][0] == 2008:
            start_08.append((key,value))

    #print(start_00)
    sr_96 = mu.survival_rate(start_96,5)
    sr_00 = mu.survival_rate(start_00,4)
    sr_04 = mu.survival_rate(start_04,3)
    sr_08 = mu.survival_rate(start_08,2)
    print('num_deps in category: ' + str(len(start_96)),sr_96)
    print('num_deps in category: ' + str(len(start_00)),sr_00)
    print('num_deps in category: ' + str(len(start_04)),sr_04)
    print('num_deps in category: ' + str(len(start_08)),sr_08)

    print(len(d.items()))

 

    '''
    #sort by multi-legislature survival rate
    surv_96_1 =[]
    surv_96_2 = []
    surv_96_3 = []
    surv_96_4 = []
    surv_96_5 = []
    for dep in start_96:
        if len(dep[1]) == 1:
            surv_96_1.append(dep)
        elif len(dep[1]) == 2:
            surv_96_2.append(dep)
        elif len(dep[1]) == 3:
            surv_96_3.append(dep)
        elif len(dep[1]) == 4:
             surv_96_4.append(dep)
        elif len(dep[1]) == 5:
            surv_96_5.append(dep)

    print(len(surv_96_1))
    print(len(surv_96_2))
    print(len(surv_96_3))            
    print(len(surv_96_4))
    print(len(surv_96_5))  

    surv_00_1 =[]
    surv_00_2 = []
    surv_00_3 = []
    surv_00_4 = []
    for dep in start_2000:
        if len(dep[1]) == 1:
            surv_00_1.append(dep)
        elif len(dep[1]) == 2:
            surv_00_2.append(dep)
        elif len(dep[1]) == 3:
            surv_00_3.append(dep)
        elif len(dep[1]) == 4:
             surv_00_4.append(dep)

 

 
  

    #print(start_96)
    #print(len(start_96))
    #print(len(start_2000))
    #print(len(start_2004))
    #print(len(start_2008))
    #print(len(start_2012))
    '''    



if __name__ == '__main__':
    
    db_name_user = "dbname=romparl user=radu"    
    #ftt.acs_db(db_name_user,fill_dep_url_table)
    ftt.acs_db(db_name_user,make_dep_table)
    #make_dep_table()
    #make_r_table()
    #get_big_talkers()




#I'm missing three people, in the scrape, need to find out which
