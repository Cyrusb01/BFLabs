#!/usr/bin/env/python3
import sys
sys.path.append('../')
from sqlalchemy import create_engine
import psycopg2
from psycopg2.extras import DictCursor
import vpcconfig as cf
import traceback
import datetime
from dateutil.parser import parse
import time
import pandas as pd
import numpy as np
import pytz
import symbolconfig as sc

''' This script pulls all available 30 minute data
    from the RDS instance for a given symbol. It then
    build daily candlesticks from them and writes a CSV.'''


def get_conn():
    not_done = True
    while not_done:
        try:
            connstr = "dbname='blockforce' user='"+cf.psql_user+\
                            "' host='"+cf.psql_host+\
                           "' password='"+cf.psql_pass+"'"
            conn = psycopg2.connect(connstr)
            estr = "postgresql://"\
                   +cf.psql_user+":"+cf.psql_pass+\
                   "@"+cf.psql_host+":5432/blockforce"

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


def handle_symbol(symb,exid,start):

    period_secs = 86400
    periods_per_day = 48
    
    ts_start = int(start.timestamp())
    
    query = f"select * from coindata_30minute where exid={exid} "\
            f" and symbolpair='{symb}' and timestamp >= {ts_start} "\
            f"order by timestamp"

    df = pd.read_sql(query,engine)
    df['datetime'] = pd.to_datetime(df['timestamp'],unit='s',utc=True)

    if start != df.iloc[0]['datetime']:
        msg = f"{symb} data don't go back far enough: {start} {df.iloc[0]['datetime']}"
        raise Exception(msg)

    t0 = time.time()
    
    # check to see if start is exactly the start of a day
    # we do this to avoid starting in the middle of the day
    # and only capturing half of the day or so
    xs = start.strftime("%Y-%m-%d") + "T00:00:00Z"
    yt = parse(xs)

    if yt == start:
        start += datetime.timedelta(days=1)
    elif yt < start:
        start += datetime.timedelta(days=2)
    
    # Remember that the time is always the closing time, so
    # if our start date here is 2017-01-02, then that's all trades
    # happening in 2017-01-01.
    
    end = df.iloc[-1]['datetime']
    xs = end.strftime("%Y-%m-%d") + "T00:00:00Z"
    end = parse(xs)

    # now get the timestamps
    ts_start = int(start.timestamp())
    ts_end = int(end.timestamp())

    nn = periods_per_day
    n = (ts_end - ts_start) // (period_secs) + 1
    xtimes = np.linspace(ts_start,ts_end,n,dtype=np.int64)

    tdf = df.copy()
    tdf = tdf.set_index('timestamp')

    xdf = tdf.loc[xtimes,['price_close']]
    xdf.reset_index(drop=False,inplace=True)

    # set up the other columns
    xdf['price_open'] = 0.0
    xdf['price_low'] = 0.0
    xdf['price_high'] = 0.0
    xdf['n_trades'] = 0.0
    xdf['volume'] = 0.0

    xtimes = np.array(xdf['timestamp'],dtype=np.int64)
    indata = np.array(df[ ['price_open','price_high','price_low', 'n_trades',
                              'volume'] ] )
    intimes = np.array(df['timestamp'],dtype=np.int64)

    # 0 -- open
    # 1 -- high
    # 2 -- low
    xopen = np.zeros(len(xtimes))
    xhigh = np.zeros(len(xtimes))
    xlow = np.zeros(len(xtimes))
    xtrades = np.zeros(len(xtimes))
    xvol = np.zeros(len(xtimes))

    ind = np.where( (intimes > ts_start - period_secs) & \
                      (intimes <= ts_start) )
    
    xopen[0] = indata[ ind[0][0] , 0]
    xhigh[0] = indata[ ind[0] , 1].max()
    xlow[0] = indata[ ind[0] , 2].min()
    xtrades[0] = indata[ ind[0], 3].sum()
    xvol[0] = indata[ ind[0], 4].sum()

    j = 0
    for i in range(1,len(xtimes)):
        j_old = j
        j = j+nn
        ts = xtimes[i]
        try:
            xopen[i] = indata[j_old+1,0]
            xhigh[i] = indata[j_old+1:j,1].max()
            xlow[i] = indata[j_old+1:j,2].min()
            xtrades[i] = indata[j_old+1:j,3].sum()
            xvol[i] = indata[j_old+1:j,4].sum()
        except:
            print(len(intimes))
            print(j,j_old+1,j_old)
            print(xtimes[i])
            print(xtimes[i-1])
            print(xtimes[-1])
            raise Exception("Bad error in downsampling!")
            
    # reassign
    xdf.loc[:,'price_open'] = xopen
    xdf.loc[:,'price_high'] = xhigh
    xdf.loc[:,'price_low'] = xlow
    xdf.loc[:,'n_trades'] = xtrades
    xdf.loc[:,'volume'] = xvol

    t1 = time.time()

    xdf['datetime'] = pd.to_datetime(xdf['timestamp'],\
                                     unit='s',utc=True)
    
    xdf.to_csv(f'daily_{symb}_exid_{exid}.csv',index=False,header=True)

    

if __name__ == "__main__":

    
    for sd in sc.slist:
        handle_symbol(sd['symb'],sd['exid'],sd['start'])
