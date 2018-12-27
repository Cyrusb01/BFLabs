#!/usr/bin/env python
# coding: utf-8

import requests
import json
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
from fred import *
import numpy as np

def rate_time_period(time_start,time_end,period):
    """
    This function takes in two unix time stamps, and a period.
    
    time_start: Unix timestamp
    time_end: Unix timestamp
    
    Period: Interval between the two timstamps. Input is a string xT. Where X is the number of minutes
    in each period. Example: '30T' for a 30 minute period, or '1T' for a minute period. Any Frequency from
    the pandas library is acceptable.
    
    Returns a Data Frame with 2 columns. Timestamp and the 2 Year Treasury Rate at that timestamp.
    
    """
    
    rate_table=pd.DataFrame()
    
    start=pd.to_datetime(time_start, unit='s',utc=True)
    end=pd.to_datetime(time_end, unit='s',utc=True)
    
    time_range=pd.date_range(start, end,freq=period)
    rate_table['timestamps']=time_range.to_series()
    rate_table['day_of_week'] = rate_table['timestamps'].dt.day_name()
    rate_table['date'] = rate_table['timestamps'].dt.floor('D').dt.date
    
    first_day_buffer=rate_table['date'].iloc[0] - pd.Timedelta(days=7) 
    
    rate_table['date'] = (rate_table['date'].astype(str))
    rate_table['percent']=0.0
    
    rate_table.reset_index(drop=True,inplace=True)
    
    rates=fed_reserve('DGS2',str(first_day_buffer),rate_table['date'].iloc[-1])
    rates['Percent']=pd.to_numeric(rates.Percent, errors='coerce')

    for x in rates['Date']:
        value=rates.loc[rates['Date']==x,'Percent'].values
        rate_table.loc[(rate_table['date']==x),'percent']=value[0]
    
    rate_table=rate_table.fillna(0.0)

    if rate_table.iloc[0]['percent'] == 0:
        rate_dates=pd.to_datetime(rates['Date'])
        first_table_day=pd.to_datetime(rate_table.iloc[0]['date'])
        starting_days=rates['Date'].loc[(rate_dates<first_table_day) & (rates['Percent'] != np.nan)]
        comparison_day=starting_days.iloc[-1]
    
    rates=rates.rename(str.lower, axis='columns')
    
    previous_day=rates.loc[rates['date']==comparison_day]

    for y in rate_table['date'].unique():
        day=rate_table.loc[rate_table['date']==y]
        if day['percent'].all()==0 and (previous_day['percent'].all())!=0:
            rate_table.loc[rate_table['date']==y,'percent']=previous_day['percent'].iloc[0]
        previous_day=rate_table.loc[rate_table['date']==y]
    
    rate_table.drop('day_of_week',axis=1,inplace=True)
    rate_table.drop('date',axis=1,inplace=True)

    rate_table['timestamp'] = rate_table['timestamps'].apply(lambda x: int(x.timestamp()))
    rate_table.drop('timestamps',axis=1,inplace=True)
    rate_table['percent'] = rate_table['percent']/100.0
    
    
    return rate_table




#time_start = int(parse('2018-01-01T00:00:00Z').timestamp())
#time_end = int(parse('2018-12-01T00:00:00Z').timestamp())
#period = '30T'

#res = rate_time_period(time_start,time_end,period)

#print(len(res))

#print( (time_end - time_start) // (30*60) )

#print(res.head(10))

