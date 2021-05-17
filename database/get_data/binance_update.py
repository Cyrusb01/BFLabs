import json
import sys
import requests
import pandas as pd
import pytz
import datetime
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
sd['EOS'] = 'eos'


symbol = 'BTC-USDT'

def update_data(symbol):
    base,quote = symbol.split('-')

    baseId = sd[base]
    quoteId = sd[quote] 


    url = "https://api.coincap.io/v2/candles?exchange=binance&interval=d1"\
                                    f"&baseId={baseId}&quoteId={quoteId}"\
                                    #    f"&start={ts_start*1000}"\
                                    #    f"&end={ts_end*1000}"

    print(url)
        

    res = requests.get(url)
    res = res.json()

    #print(res['data'][-1])

    #res['data'] = res['data'][-1]

    #print(res['data'])

    if len(res['data']) > 0:
        df = pd.DataFrame(res['data'])
        
        df.rename(columns={'open':'price_open',
                            'close':'price_close',
                            'low':'price_low',
                            'high':'price_high',
                            'period':'timestamp'},inplace=True)

        df['timestamp'] = df['timestamp'] // 1000
        
        df['datetime'] = pd.to_datetime(df['timestamp'],unit='s',utc=True)

        df1 = df.tail(1)
        print(df1)
        filename = f'{symbol}_data.csv'
        with open(filename, 'a') as f:
            df1.to_csv(f, index = False, header=False)
        #print(df)

pairs = ['BTC-USDT', 'BCHABC-USDT', 'TRX-USDT', 'IOTA-USDT', 'XLM-USDT', 'EOS-USDT','XRP-USDT', 'ADA-USDT','LTC-USDT', 'NEO-USDT', 'BNB-USDT', 'ETH-USDT']
for pair in pairs:
    update_data(pair)
