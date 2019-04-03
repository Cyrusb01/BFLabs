#!/usr/bin/env/python3
import sys
sys.path.append('../')
import glob
from sqlalchemy import create_engine
import psycopg2
from psycopg2.extras import DictCursor
import config as cf
import traceback
import datetime
from dateutil.parser import parse
import time
import pandas as pd
import numpy as np
import pytz

"""This script reads all csv files in the directory and dumps
   them into a local postgres database table """

def get_conn():
    not_done = True
    while not_done:
        try:
            connstr = "dbname='"+cf.dbname+"' user='"+cf.psql_user+\
                            "' host='"+cf.psql_host+\
                           "' password='"+cf.psql_pass+"'"
            conn = psycopg2.connect(connstr)
            estr = "postgresql://"\
                   +cf.psql_user+":"+cf.psql_pass+\
                   "@"+cf.psql_host+":5432/"+cf.dbname

            engine = create_engine(estr)
            not_done = False
            cur = conn.cursor(cursor_factory=DictCursor)
        except:
            traceback.print_exc()
            print("Trying to reconnect!")
            time.sleep(5)
            continue

        return conn, cur, engine

conn,cur,engine = get_conn()



def get_files_symbols():

    files = glob.glob("data/*.csv")

    slist = []
    for xf in files:
        symb = xf.split('_')[1]
        exid = xf.split('_')[-1].split('.')[0]
        sd = {}
        sd['symbol'] = symb
        sd['exid'] = int(exid)
        sd['fname'] = xf
        slist.append(sd)

    return slist

def process_file(sd):

    df = pd.read_csv(sd['fname'])

    del df['datetime']
    df['symbolpair'] = sd['symbol']
    df['exid'] = sd['exid']
    
    # delete old data
    query = "delete from coindata_day where "\
            f"symbolpair = '{sd['symbol']}' and "\
            f"exid = {sd['exid']}"
    cur.execute(query)
    conn.commit()

    # fill with new data
    df.to_sql('coindata_day',engine,
              if_exists='append',
              index=False)

    


if __name__ == "__main__":

    slist = get_files_symbols()

    for sd in slist:
        process_file(sd)


    

