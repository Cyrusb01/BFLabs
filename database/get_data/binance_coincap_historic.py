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

sd = {}
sd['ETH'] = 'ethereum'
sd['EOS'] = 'eos'
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

def get_data(symbol,ts_start,ts_end):

    base,quote = symbol.split('-')

    baseId = sd[base]
    quoteId = sd[quote]  
    
    url = "https://api.coincap.io/v2/candles?exchange=binance&interval=d1"\
                                   f"&baseId={baseId}&quoteId={quoteId}"\
                                   f"&start={ts_start*1000}"\
                                   f"&end={ts_end*1000}"

    print(url)
    
    try:
        res = requests.get(url)
        res = res.json()

        if 'data' not in res.keys():
            print(res)
        
    except:
        print("do something")
        return
    
    if len(res['data']) > 0:
        df = pd.DataFrame(res['data'])
        df.rename(columns={'open':'price_open',
                           'close':'price_close',
                           'low':'price_low',
                           'high':'price_high',
                           'period':'timestamp'},inplace=True)

        df['timestamp'] = df['timestamp'] // 1000
        
        df['datetime'] = pd.to_datetime(df['timestamp'],unit='s',utc=True)

        df.to_csv(f'data/daily_{symbol}_exid_0.csv',index=False,header=True)
        
        print(symbol)
        print(df.head(1))
        print("---")
    else:
        print(res)

        
if __name__ == '__main__':

    for sdd in sc.slist:

        if sdd['exid'] != 0:
            continue

        ts_start = int(parse('2017-01-01T00:00:00Z').timestamp())
        ts_end = int(parse('2019-01-01T00:00:00Z').timestamp())
#        ts_end = int(parse(datetime.datetime\
#                       .now(tz=pytz.utc).strftime('%Y-%m-%dT00:00:00Z')).timestamp())

        get_data(sdd['symb'],ts_start,ts_end)
        time.sleep(5)

