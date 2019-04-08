
IMG = [dict(
            source="/static/main-logo-black.png",
            xref="paper", yref="paper",x=1.05, y=1.05,
            sizex=0.25, sizey=0.25,xanchor="right", yanchor="bottom")]

RANGE = dict(
                buttons=list([
                    dict(count=1,label='1m',step='month',stepmode='backward'),
                    dict(count=6,label='6m',step='month',stepmode='backward'),
                    dict(count=1,label='YTD',step='year',stepmode='todate'),
                    dict(count=1,label='1y',step='year',stepmode='backward'),
                    dict(step='all')]))
ANNOT = [
            dict(x=0.5,y=-0.18,xref='paper',yref='paper',showarrow=False,
                text=f'*Source: Binance', font=dict(size=12))
        ]

PLOT_CONFIG ={'showAxisDragHandles': False, 'toImageButtonOptions': {
        'format': 'png', #one of png, svg, jpeg, webp
        'filename': 'blockforcecapital_crypto_correlation',
        'height': 600,
        'width': 1000,
        'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
          }, 'showLink':False,
                'modeBarButtonsToRemove':['sendDataToCloud','zoomIn2d', 'zoomOut2d','zoom2d','pan2d','select2d',\
                                      'lasso2d','zoom3d','pan3d','orbitRotation','tableRotation']}

YAXIS = dict(hoverformat = '.2f',autorange=True,\
                    ticks='inside',  tickcolor='#53585f', ticklen=8, tickwidth=3,automargin=True, tickprefix="          ")

XAXIS= dict(title='Date', ticks='inside', ticklen=6, tickwidth=4,
            rangeselector=RANGE,
            rangeslider=dict(visible = False),
            automargin=True,
            type='date',
            tickcolor='#53585f')

COLORSCALE = [
        # Let first 10% (0.1) of the values have color rgb(0, 0, 0)
        [0, '#ebcd86'],[0.1, '#ebcd86'],
        # Let values between 10-20% of the min and max of z
        # have color rgb(20, 20, 20)
        [0.1, '#d6bd82'],[0.2, '#d6bd82'],
        # Values between 20-30% of the min and max of z
        # have color rgb(40, 40, 40)
        [0.2, '#c3ad7d'],[0.3, '#c3ad7d'],
        [0.3, '#af9e79'],[0.4, '#af9e79'],
        [0.4, '#9b8e74'],[0.5, '#9b8e74'],
        [0.5, '#877f6f'],[0.6, '#877f6f'],
        [0.6, '#73716a'],[0.7, '#73716a'],
        [0.7, '#606265'],[0.8, '#606265'],
        [0.8, '#4c5560'],[0.9, '#4c5560'],
        [0.9, '#37475b'],[1.0, '#37475b']
    ]

