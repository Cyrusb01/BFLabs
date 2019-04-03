#!/usr/bin/env python3
import json
import sys
import requests
import pandas as pd
import pytz
import datetime
import symbolconfig as sc
import time
from dateutil.parser import parse
from sqlalchemy import create_engine
import psycopg2
from psycopg2.extras import DictCursor
import config as cf


sd = {}
sd['ETH'] = 'ethereum'
sd['USDT'] = 'tether'
sd['TRX'] = 'tron'
sd['IOTA'] = 'iota'
sd['XLM'] = 'stellar'
sd['XRP'] = 'ripple'
sd['LTC'] = 'litecoin'
sd['ADA'] = 'cardano'
sd['NEO'] = 'neo'
sd['BCHABC'] = 'bitcoin-cash'
sd['BNB'] = 'binance-coin'
sd['BTC'] = 'bitcoin'

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


def get_data(symbol,ts_start,ts_end):

    base,quote = symbol.split('-')

    baseId = sd[base]
    quoteId = sd[quote]  
    
    url = "https://api.coincap.io/v2/candles?exchange=binance&interval=d1"\
                                   f"&baseId={baseId}&quoteId={quoteId}"\
                                   f"&start={ts_start*1000}"\
                                   f"&end={ts_end*1000}"

    try:
        res = requests.get(url)
        res = res.json()

        if 'data' not in res.keys():
            print(res)

        
    except:
        print("do something")
        return None
    

    
    if len(res['data']) > 0:
        df = pd.DataFrame(res['data'])
        df.rename(columns={'open':'price_open',
                           'close':'price_close',
                           'low':'price_low',
                           'high':'price_high',
                           'period':'timestamp'},inplace=True)

        df['timestamp'] = df['timestamp'] // 1000
        
        df['datetime'] = pd.to_datetime(df['timestamp'],unit='s',utc=True)

        return df
        
    else:
        # print(res)
        return None

def fill_data(sdd):

    symb = sdd['symb']
    exid = sdd['exid']
    query = f"select * from coindata_day where exid = {exid} "\
            f"and symbolpair = '{symb}' order by timestamp desc limit 1"                                         

    cur.execute(query)
    res = cur.fetchone()

    if res is None:
        print("Can't update, have no data. ",symb)
        return

    day = 86400
    ts_start = res['timestamp'] + day

    ts_end = parse(datetime.datetime\
                   .now(tz=pytz.utc).strftime("%Y-%m-%dT00:00:00Z"))
    ts_end = ts_end + datetime.timedelta(days=1)
    ts_end = int(ts_end.timestamp())

    df = get_data(symb,ts_start,ts_end)

    if df is not None and len(df) > 0:
        del df['datetime']
        df['symbolpair'] = sdd['symb']
        df['exid'] = sdd['exid']
        df['n_trades'] = -1
        df.to_sql('coindata_day',engine,
                  if_exists='append',
                  index=False)
    
        
if __name__ == '__main__':

    for sdd in sc.slist:
        if sdd['exid'] != 0:
            continue
        print(sdd['symb'])
        fill_data(sdd)

