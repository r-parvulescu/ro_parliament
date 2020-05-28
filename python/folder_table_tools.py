#Started June 8, 2017
#folder_table_tools.py
#built for python 3

"""Tools for reading from and writing to folders, i.e., when I want to 
   organise data in files, in some folder structure."""

import json
import os
import psycopg2

def json_file_dump(fldr_path, file_name, dictio):
    """Dumps dictionary in line-delimited json file."""

    f = open(fldr_path + file_name, 'w')
    f.write(json.dumps(dictio))
    f.write('\n')
    f.close

def acs_db(db_name_user, func, com=True):
    """Open and close connection to postgres db, give it valid connection and cursor,
       then execute function. By default will also commit to db."""
    conn = psycopg2.connect(db_name_user)
    cur = conn.cursor()

    func(conn, cur)

    if com:
        conn.commit()
    cur.close()
    conn.close()
    

def get_list_from_table(db_name_user, table_command):
    """Return a postgres table's column as a python list.
       PreC: db_name_user must be in format "dbname=XXXX user=XXXX" and 
        table_command must come as 'SELECT xx(column)xx FROM xx     
        (table)xx'."""

    conn = psycopg2.connect(db_name_user)
    cur = conn.cursor()
    #read coloumn
    try:
        cur.execute(table_command)
    except:
        cur.close()
        conn.close()         
    #load entries into list
    l = []
    for row in cur:
        l.append((row[0],row[1]))

    cur.close()
    conn.close()
    return l
        
def tbl_op(conn, cur, tbl_cmnd, data=None):
    """Executes an operation on a postgres table using psycopg2.
    PreC: connection to db established. Parameters are
        conn = valid connection 
        cur = valid cursor
        tbl_cmnd = valid postgres command to pass to psycopg2
        data = valid data structure to pass to psycopg2, if needed """

    #try:
    #    if data:
    #        cur.execute(tbl_cmnd)
    #    else:
    cur.execute(tbl_cmnd,data) 
#except:
    conn.commit()
    cur.close()
    conn.close()
#    return
        

    
