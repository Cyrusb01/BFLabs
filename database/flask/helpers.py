import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json
from variables import IMG, RANGE, ANNOT, PLOT_CONFIG, XAXIS, YAXIS, COLORSCALE

def create_corr(pairs, db):
    vals = dict()
    for sp in pairs:
        data = get_coin_data(sp, db)
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
            source="/static/main-logo-black.png",
            xref="paper", yref="paper",
            x=1.2, y=1.1,
            sizex=0.32, sizey=0.32,
            xanchor="right", yanchor="bottom")],
        title=f'Return Correlation - {date}',
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
    print(graphJSON)
    return ids, graphJSON