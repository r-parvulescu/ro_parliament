#Started May 26, 2017
#ThrowOutEmpties.py
#ran in Python 3.x

""" Tools for collecting data off the Romanian Chamber of Deputies website: scraping the HTML, extracting relevant information, and dumping everything into a postgreSQL database. """

import misc_utilities as mu
import utterance_regex_functions as urf
import scrapers
import psycopg2
import os
import natsort
import pprint 
  
def BuildUtteranceTable(src_fldr):
    """Reads files from a folder, extracts relevant info, and dumps them into a postgres table.."""

    #connect to postgres db
    conn = psycopg2.connect("dbname=romparl user=radu")
    cur = conn.cursor()

    file_counter = 0
    utterance_counter = 0
    commit_counter = 0

    for FILE in natsort.natsorted(os.listdir(src_fldr)):
        print(FILE)
        file_counter += 1 

        uht = mu.GetURL_HTML_Time(src_fldr + FILE)
        utterances = urf.UtternaceInfo(uht[0], uht[1])
    
        #loop over utterance list and dump into table
        for u in utterances:
            utterance_counter +=1
            text = u['utterance_text']
            mtrcs = mu.SimpleTextMetrics(text)

            #dump into table
            try: 
                cur.execute("INSERT INTO utterances_elemental (utterance_id_first, utterance_id_full, utterance_source_url, session_date, chamber, session_ID, session_name, section_num, section_name, subsection_num, subsection_name, idl, utterer_url, utterer_first_middle_name, utterer_last_name, utterer_extra_info, utterance_text, num_word, num_lines, avg_line_length) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (u['utterance_id_first'], u['utterance_id_full'], uht[0], u['date'], u['chamber'], u['session_ID'], u['session_name'], u['section_num'], u['section_name'], u['subsection_num'], u['subsection_name'], u['idl'], u['utterer_url'], u['utterer_first_middle_name'], u['utterer_last_name'], u['utterer_extra_info'], u['utterance_text'], mtrcs[0], mtrcs[1], mtrcs[2]))
                commit_counter += 1
                #commit every two hundred rows
                if commit_counter % 200 == 0:
                    conn.commit()

            except psycopg2.InterfaceError as e:
                print(e.message)
                conn = psycopg2.connect("dbname=romparl user=radu")
                cur = conn.cursor()   
          
        print (file_counter, utterance_counter)
        #if counter == 10000:
        #    cur.close()
        #    conn.close()
        #    break

    #commit and close connection
    conn.commit()
    cur.close()
    conn.close()

def CheckUtteranceList():
    """I suspect utterances should be in increasing order and it looks like I'm missing many, so I need to find the gaps in the order and check corresponding files."""

        #connect
    conn = psycopg2.connect("dbname=romparl user=radu")
    cur = conn.cursor()

    #read coloumn
    cur.execute('SELECT utterance_id_first FROM utterances_elemental ORDER BY utterance_id_first ASC')
    
    #load entries into list
    l = []
    for row in cur:
        l.append(row[0])

    #find gaps in order
    gaps = []
    gap_ranges = []
    for x in range(0, len(l)-1):
        gap = l[x+1] - l[x]
        if gap > 1:
            gap_ranges.append([l[x], l[x+1], gap])
            gaps.append(gap)

    gaps = sorted(gaps, key=int)

    print(gap_ranges[-20:])
    print(gaps[-20:])
    print(len(gaps))
    #return gaps 

    #commit and close connection
    conn.commit()
    cur.close()
    conn.close()

    return l


if __name__ == '__main__':

    #CheckUtteranceList()
    src_fldr = "/media/radu/My Passport/RomParl/CD/htmls/utterances/section_transcript_htmls/"
    BuildUtteranceTable(src_fldr)






    #make elemental utterance table
    #cur.execute("CREATE TABLE utterances_elemental(id serial PRIMARY KEY, utterance_id_first integer, utterance_id_full text, utterance_source_url text, session_date date, session_year_month char(7), chamber text, session_id text, session_name text, section_num text, section_name text, subsection_num text, subsection_name text, idl integer, utterer_url text, utterer_first_middle_name text[], utterer_last_name text, utterer_extra_info text, utterance_text varchar, num_word integer, num_lines integer, avg_line_length real);")

#add indexes
#alter table utterances_elemental add column session_year_month char(7) index, utterer url text index;


    #pretty print to eyeball
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(urls)



#7660-22--1.txt
#84946 525276

