import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json
from variables import IMG, RANGE, ANNOT, PLOT_CONFIG, XAXIS, YAXIS, COLORSCALE

def get_coin_data(symbol, db, coindata_day):
    query = db.session.query(coindata_day)\
            .filter(coindata_day.symbolpair == symbol.upper())\
            .order_by(coindata_day.timestamp)
    try:
        df = pd.read_sql(query.statement, query.session.bind)
    
    except:
        rd = {'msg': 'database query failed'}
        return json.dumps(rd)
        
    if df is None or len(df) < 1:
        rd = {'msg': 'no data'}
        return json.dumps(rd)

    res = df[ ['timestamp','price_open','price_high',\
               'price_low','price_close','n_trades',\
               'volume' ]].to_dict(orient='list')
    return res

def volatility(price,period_value, data_interval):
    """
    This function is used to calculate the annualized volatility for a given set of prices.
    Inputs:
       price: a pandas series/column of prices
       period_value: Number of days volatility is measured over (int). e.g 1,5,10,14,30
    returns:
       a pandas series of volatility measures
    """

    if data_interval not in ['1T', '30T', '1D']:
        raise ValueError
    
    if data_interval == '1T':
        trading_periods = 60*24
    elif data_interval == '30T':
        trading_periods = 2*24
    else:
        trading_periods = 1

    percent_change=price.pct_change()*100
    standard_deviation = percent_change.rolling(period_value*trading_periods).std()
    #formula sqrt(to_hour * daily_hours * days)
    volatility = standard_deviation*((trading_periods*365)**0.5)
    return volatility

def graph_volatility(df, coins):
    source='Binance'
    yaxis_dict = dict(title='Rolling 30-Day Volatility', hoverformat = '.2f',\
                    ticks='outside', tickcolor='#53585f',ticklen=8, tickwidth=3,\
                    automargin=False, tick0=0, tickprefix="          ")
    vols = [14,30,90]
    
    data=[]
    for i in df.columns:
        data.append(go.Scatter(x=list(df.index),
                       y=list(df[i]), name=i.split('_',1)[0], visible=False))

    num_coins = len(coins)
    
    vis_init = [False]*len(vols)
    vis_vol = dict()
    for i,v in enumerate(list(vols)):
        tmp = vis_init.copy()
        tmp[i]=True
        vis_vol[v]=tmp.copy()
        
    updatemenus = list([
    dict(type="dropdown",
         active=1,
         x=-0.12,
         y=1.09,
         buttons=[dict(label = f'{v}-Day',
                 method = 'update',
                 args = [{'visible': vis_vol[v]*num_coins},
                         {'yaxis': dict(yaxis_dict, title=f'Rolling {v}-Day Volatility')}]) for v in list(vols)]
        )
    ])
    
    #set initial to 0
    for i, b in enumerate(vis_vol[30]*num_coins):
        if b == True:
            data[i].visible=b
    
    layout = dict(
        images=[dict(
            source="/static/main-logo-black_small.png",
            xref="paper", yref="paper",
            x=1.05, y=1.05,
            sizex=0.21, sizey=0.21,
            xanchor="right", yanchor="bottom")],
        height=800, width=1200,\
        dragmode='zoom',
        title='Volatility',
        xaxis=dict(
            title='Date', ticks='inside', ticklen=6, tickwidth=3,
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                        label='YTD',
                        step='year',
                        stepmode='todate'),
                    dict(count=1,
                        label='1y',
                        step='year',
                        stepmode='backward'),
                    dict(step='all')
                ])
            ),
            type='date',
            tickcolor='#53585f'
        ),
        yaxis = yaxis_dict,
        margin=dict(pad=3),
        updatemenus=updatemenus,
        annotations=[
            dict(x=-.1,y=-0.18,xref='paper',yref='paper',showarrow=False,
                text=f'*Source: {source}', font=dict(size=12))
        ]
    )
        
    graph = {
            'data':data,
            'layout':layout
        }
    graphs=[graph]
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return ids, graphJSON

def calc_volatility(pairs, db, coindata_day):
    '''
    Get Graph For Each Coin You Want
    '''
    #create visuals

    df_all = dict()
    for sp in pairs:
        #calculate vol for each coin and graph
        tmp = pd.DataFrame(get_coin_data(sp, db, coindata_day))
        tmp = tmp[['price_close', 'timestamp']]
        tmp.timestamp = pd.to_datetime(tmp.timestamp, unit='s')
        tmp.set_index('timestamp', inplace=True)
        for t in [14,30,90]:
            df_all[f'{sp.split("-",1)[0]}_vol_{t}']=volatility(tmp.price_close, t, data_interval='1D')

    return pd.DataFrame(df_all).dropna(how='all')

def create_corr(pairs, db, coindata_day):
    vals = dict()
    for sp in pairs:
        data = get_coin_data(sp, db, coindata_day)
        if(len(data)<7): #bad data
            continue
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        vals[sp]=df.price_close
        
    df_ = pd.DataFrame(vals)
    df_.index = pd.to_datetime(df_.index, unit='s')
    df_ = df_.pct_change(1).fillna(0)
    df_.columns = [col.split("-",1)[0] for col in df_.columns]
    df_ = df_.round(3).rolling(180).corr().dropna(how='all')
    
    return df_

def graph_heatmap(df, date):
    corr_mtx = df.loc[date].values
    text_info = np.round(corr_mtx, decimals=5).astype(str)

    x = 0
    for i in range(len(text_info)):
        for j in range(len(text_info[0])):
            if(text_info[i,j]=='1.0'):
                text_info[i,j]=''
                corr_mtx[i,j]=np.nan
        
    labels=df.columns
    layout = go.Layout(images=[dict(
            source="/static/main-logo-black_small.png",
            xref="paper", yref="paper",
            x=1.15, y=1.1,
            sizex=0.32, sizey=0.32,
            xanchor="right", yanchor="bottom")],
        title=f'Return Correlation - Close {date}',
        annotations=[
        dict(x=.5,y=-.18,xref='paper',yref='paper',showarrow=False,
            text=f'*6-Month Rolling Correlation of Daily Returns; Source: Binance', font=dict(size=10))
        ],
        autosize=False,
        width=600,
        height=600,
        xaxis=dict(ticklen=1, tickcolor='#fff'),
        yaxis=dict(ticklen=1, tickcolor='#fff'),
        margin=dict(pad=0),
    )

    #create visuals
    graphs=[
        {
            'data':[go.Heatmap(z=corr_mtx, x=labels, y=labels, text = text_info,\
                    hoverinfo='text',colorscale=[[0.,'#ebcd86'],[1,'#37475b']])],
            'layout': layout
        }
    ]
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return ids, graphJSON