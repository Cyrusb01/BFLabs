#!/usr/bin/env python3
import sys
sys.path.append("../")
import pandas as pd
import numpy as np
import sqlite3
import helpers as hp
import datetime
import pytz
from dateutil.parser import parse
import fred_range as fr

sqlite_db = '../backtest.sqlite'
conn = sqlite3.connect(sqlite_db)
conn.row_factory = hp.dict_factory
cur = conn.cursor()

query = "SELECT name FROM sqlite_master WHERE type='table' AND name='btc'"
cur.execute(query)
res = cur.fetchone()

if res == None:

    query = "create table btc (date INTEGER PRIMARY KEY,"\
            "price REAL, strategy_return REAL,"\
            "market_return REAL, treasury REAL, backtest_id INTEGER)"
    cur.execute(query)
    conn.commit()

# load data
    
df = pd.read_csv('master.csv')
df = df[ ['assets','timestamp','price'] ]
df['date'] = (df['timestamp']*1000).astype(int)
df['strategy_return'] = df['assets']/100.0
df['market_return'] = df['price'] * 100 / df.iloc[0]['price']
df['backtest_id'] = 0
df = df[ ['date','price','strategy_return','market_return','backtest_id'] ]

# now downsample the data to daily
tstart = df.iloc[0]['date']
tend = df.iloc[-1]['date']
nn = int((tend - tstart) / (3600*24*1000) + 1)

dates = np.linspace(tstart,tend,nn)

print(dates[0],
      datetime.datetime.fromtimestamp(dates[0]/1000,tz=pytz.utc))
print(dates[-1],
      datetime.datetime.fromtimestamp(dates[-1]/1000,tz=pytz.utc))

df = df.set_index('date')
df = df.loc[ dates, : ]
df = df.reset_index(drop=False)
df = df.drop_duplicates(subset='date')

# get treasury data
time_start = tstart // 1000
time_end = tend // 1000
period = '1D'
res = fr.rate_time_period(time_start,time_end,period)
df['treasury'] = res['percent']

df.to_sql('btc',conn,index=False,if_exists='append')



print(df.head(5))


    
