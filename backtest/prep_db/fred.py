#!/usr/bin/env python
# coding: utf-8

import requests
import json
import pandas as pd

def fed_reserve(ticker,time_start,time_end,drop_blanks=False):
    """
    This function is used to pull data from the Federal Reserve Bank of St. Louis Api.
    There are four arguements.
    
    ticker: Ticker String, specifies the ticker in which to pull data from. 
            For the Maturity Rates:
            DGS3MO: 3-Month Treasury Constant Maturity Rate
            DGS1MO: 1-Month Treasury Constant Maturity Rate
            DGS2:   2-year Treasury Constant Maturity Rate
    
    time_start:String in the format 'YYYY-MM-DD', specifies the start of the observation period
    
    time_end: String in the format 'YYYY-MM-DD', specifies the end of the observation period
    
    drop_blanks: If True, removes rows where the value is '.' 
    
    The data is returned in the form of a pandas dataframe, containing two columns. A date and the value of the 
    percent change on that date. 
    
    If there is no data within the date period or input is not in the correct format, returns None. 
    """
    
    url='https://api.stlouisfed.org/fred/series/observations?series_id=%s'% (ticker)+        '&api_key=fae776c1c6d3d5e6324f507f62a43928&file_type=json&frequency=d'+        '&observation_start=%s&observation_end=%s' % (time_start,time_end)
    content=requests.get(url).json()
    if 'error code' not in content:
        ticker_data=pd.DataFrame(content['observations']).dropna()
        if len(ticker_data)!=0:
            ticker_data.drop('realtime_end', axis=1,inplace=True)
            ticker_data.drop('realtime_start', axis=1,inplace=True)
            if drop_blanks==True:
                ticker_data=ticker_data[ticker_data.value != '.']
            ticker_data.rename(index=str, columns={"date": "Date", "value": "Percent"},inplace=True)
        else:
            ticker_data=None
    else:
        ticker_data=None
    return ticker_data

