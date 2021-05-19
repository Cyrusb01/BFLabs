#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import json
import flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple



from flask import Flask,jsonify,request,Response,render_template,redirect
#from flask_restplus import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.middleware.proxy_fix import ProxyFix
from helpers import graph_heatmap, create_corr, volatility, calc_volatility, graph_volatility, get_coin_data, graph_timeline
from variables import IMG, RANGE, ANNOT, PLOT_CONFIG, XAXIS, YAXIS, COLORSCALE
import datetime
import pytz
#import config as cf
import shutil
app = Flask(__name__)
#-----------------------------------------------------------------------------------------DASH STUFF ---------------------------------------------------------------------------------------------
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from plotly import graph_objs
import plotly.express as px
from jupyter_dash import JupyterDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app_dash = dash.Dash(__name__, server = app, url_base_pathname = '/dashboard/', external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

#Pricing Data 
df = pd.read_csv("C:\Onramp\BFLabs(Cyrus CSV)\datafiles\Slider_data.csv", usecols = ['Date','TraditionalOnly', 'SP500Only', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
df['Date'] = pd.to_datetime(df['Date'], unit = 'ms')
df = df.set_index('Date')

#Stats Data
df_stats = pd.read_csv("C:\Onramp\BFLabs(Cyrus CSV)\datafiles\Slider_data.csv", usecols = ['AnnReturn',	'AnnRisk','SharpeRatio','SortinoRatio','ReturnTraditional','ReturnSP500','RiskTraditional',	'RiskSP500','SharpeTraditional','SharpeSP500','SortinoTraditional',	'SortinoSP500'])
df_stats = df_stats.dropna()


colors = ['#a90bfe', '#7540ee', '#3fb6dc'] 


app_dash.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='Onramp Research Dashboard', style = {'text-align': 'center'})
    ], className='row'),
    html.Br(),
    html.Div([
        html.Div([
        
        ], className='one columns'),
        html.Div([
            
            dcc.Graph(
                id='pie_chart'
            ),  
        ], className='three columns'),
        html.Div([
           

            dcc.Graph(
                id='line_chart'
            ),  
        ], className='four columns'),
        html.Div([
            dcc.Graph(
                id='scatter_plot'
            ),  
        ], className='three columns'),
    ], className='row'),
    # New Div for all elements in the new 'row' of the page
    html.Br(),
    html.Br(),
    html.Div([
        html.Div([
            html.H3(children='100% 60/40'),
        ], className='two columns'),
        
        html.Div([
            dcc.Slider(
            id = "slider_num",
            min = 0,
            max = 5,
            value = 0,
            step = 1
            )
        ], className='eight columns'),
        html.Div([
            html.H3(children='5% Bitcoin'),
        ], className='two columns'),
    ], className='row'),
    
    #html.Div(id='slider-output-container'),
    html.Div([
        html.Div([
            html.H3(children=''),
            
        ], className='two columns'),
        html.Div([
            
            dcc.Graph(
                id='bar_chart_rr'
            ),  
        ], className='four columns'),
        html.Div([
           

            dcc.Graph(
                id='bar_chart_ss'
            ),  
        ], className='four columns'),
        # html.Div([
           
        # ], className='two columns'),
    ], className='row'),
    #-----------New row 
    html.Div([
        html.Div([
            html.H3(children=''),
            
        ], className='one columns'),
        html.Div([
            
            html.A('HEATMAP', href='/api/heatmap')
        ], className='two columns'),
        html.Div([
           

             html.A('DASHBOARD', href='/dashboard/')
        ], className='two columns'),
        html.Div([
           

             html.A('HEATMAP TIMELINE', href='/api/heatmap_timeline')
        ], className='two columns'),
        html.Div([
           

             html.A('VOLATILITY CHART', href='/api/volatility')
        ], className='two columns'),
        html.Div([
           

             html.A('Navigate to heatmap', href='/api/heatmap')
        ], className='two columns'),
    ], className='row'),
])

@app_dash.callback(

    [dash.dependencies.Output('pie_chart', 'figure'),
     dash.dependencies.Output('line_chart', 'figure'),
     dash.dependencies.Output('scatter_plot', 'figure'),
     dash.dependencies.Output('bar_chart_rr', 'figure'),
     dash.dependencies.Output('bar_chart_ss', 'figure')
     ],
    [dash.dependencies.Input('slider_num', 'drag_value')]
)
def update_graphs(value):
    
    #------------------------------------------------------------------------------Pie Chart ---------------------------------------------------------------------------

    percent_dict = {'60/40' : 1-float(value)/100, 'Bitcoin': float(value)/100}

    def graph_pie(percent_dictionary):

        colors_pie = ['#a90bfe', '#f2a900'] #BTC Orange
        assets = list(percent_dictionary.keys())

        percents = list(percent_dictionary.values())
        #print(percents)
        
        fig = px.pie( values = percents, names = assets, color = assets,
                                color_discrete_sequence= colors_pie,
                                title="Portfolio Allocation",
                                width = 400, height = 400
                                )
        fig.update_traces(hovertemplate='%{value:.0%}')
        #print("plotly express hovertemplate:", fig.data[0].hovertemplate)
        fig.update_layout(
        title={
            'text': "<b>Portfolio Allocation<b>",
            'y':1,
            'x':0.49,
            'xanchor': 'center',
            'yanchor': 'top'},
        font = dict(
            family="Circular STD",
            color="black"
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-.2,
        xanchor="left",
        x=0.30))
        fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        fig.update_traces(marker=dict(line=dict(color='white', width=1.3)))
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_layout(margin = dict(l=10, r=20, t=40, b=0))
        
        return fig


    #------------------------------------------------------------------------------Line Chart ---------------------------------------------------------------------------

    choice = 'd' + str(value + 1)
    def graph_line_chart(df, choice):

        df = df[['TraditionalOnly', 'SP500Only', choice]]
        df.columns = ['Traditional Only', 'SP500 Only', "Combined Portfolio"]
        color_dict = {}
        color_dict['Traditional Only'] = colors[0]
        color_dict['SP500 Only'] = colors[1]
        color_dict['Combined Portfolio'] = colors[2]
        
    
        fig = px.line(df, labels={
                                "value": "",
                                "Date": "",
                                "color" : "",
                                "variable": ""
                                },
                        title="Portfolio Performance",
                        color_discrete_map=color_dict,
                        template="simple_white",
                        width = 500, height = 450
                        )
        
        fig.update_yaxes( # the y-axis is in dollars
            tickprefix="$", showgrid=True
        )
        x = .82
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y= -.25,
            xanchor="right",
            x=.86
        ),
        font = dict(
            family="Circular STD",
            color="black"
        ),
        title={
                'text': "<b>Portfolio Performance<b>",
                'y':1,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},)
        fig.update_yaxes(side = "right", nticks = 4)
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_layout(margin = dict(l=10, r=20, t=20, b=0))
        return fig


    #------------------------------------------------------------------------------Scatter Plot ---------------------------------------------------------------------------
    risk_dic = {'60/40': float(df_stats.iloc[0][6])/100, 'S&P 500 Total Return': float(df_stats.iloc[0][7])/100, 'Combined Portfolio': float(df_stats.iloc[value][1])/100}
    return_dic = {'60/40': float(df_stats.iloc[0][4])/100, 'S&P 500 Total Return': float(df_stats.iloc[0][5])/100, 'Combined Portfolio': float(df_stats.iloc[value][0])/100}
    
    def graph_scatter_plot(risk_dic, return_dic):
        labels = list(risk_dic.keys())

        xaxis_vol = list(risk_dic.values())
        yaxis_return = list(return_dic.values())


        size_list = [3, 3, 3]
        symbols = [1, 2, 0] #this makes the symbols square diamond and circle in order
        fig = px.scatter( x= xaxis_vol, y= yaxis_return, size = size_list, color = labels, 
                                #color_discrete_sequence=['#A90BFE','#FF7052','#66F3EC', '#67F9AF'],
                                color_discrete_sequence= colors,
                                template = 'plotly_white',
                                labels={
                                "x": "Annual Risk",
                                "y": "Annual Return",
                                "color" : "",
                                "symbol": ""

                                },
                                title="Risk vs. Return",
                                width = 450, height = 450)
        fig.update_xaxes(showgrid = False)
        #print("plotly express hovertemplate:", fig.data[0].hovertemplate)
        fig.update_traces(hovertemplate='Annual Risk = %{x:.0%}<br>Annual Return = %{y:.0%}')
        
        fig.update_layout( 
        title={
            'text': "<b>Risk vs. Return<b>",
            'y':1,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font = dict(
            family="Circular STD",
            color="black"
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-.3,
        xanchor="left",
        x=0.1
        ))
        fig.update_yaxes(side = "right")
        fig.update_layout({
        'plot_bgcolor': 'rgba(255, 255, 255, 0)',
        'paper_bgcolor': 'rgba(255, 255, 255, 0)',
        })
        fig.update_layout(yaxis_tickformat = '%')
        fig.update_layout(xaxis_tickformat = '%')
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_xaxes( title_font = {"size": 20})
        fig.update_yaxes( title_font = {"size": 20})
        fig.update_layout(margin = dict(l=10, r=0, t=20, b=0))

        return fig
    
    #------------------------------------------------------------------------------Bar Chart ---------------------------------------------------------------------------

    x_axis_rr = ['Ann. Return', 'Ann. Risk']
    x_axis_ss = ['Sharpe', 'Sortino']
    
    y_combined_rr = [float(df_stats.iloc[value][0])/100, float(df_stats.iloc[value][1])/100]
    y_6040_rr = [float(df_stats.iloc[0][4])/100, float(df_stats.iloc[0][6])/100]
    y_spy_rr = [float(df_stats.iloc[0][5])/100, float(df_stats.iloc[0][7])/100]

    y_combined_ss = [float(df_stats.iloc[value][2])/100, float(df_stats.iloc[value][3])/100]
    y_6040_ss = [float(df_stats.iloc[0][8])/100, float(df_stats.iloc[0][10])/100]
    y_spy_ss = [float(df_stats.iloc[0][9])/100, float(df_stats.iloc[0][11])/100]

    def graph_barchart(x_axis_rr_ss, y_combined, y_6040, y_spy):
        

        if(x_axis_rr_ss[0] == 'Ann. Return'):
            title = "<b>Ann. Return & Risk<b>"
        else:
            title = "<b>Sharpe & Sortino Ratio<b>"

        x_axis_rr_ss *= 3
        y_vals = []
        y_vals += y_6040
        y_vals += y_spy
        y_vals += y_combined
    
        
        strat = ['60/40 Only', '60/40 Only', 'S&P 500 Total Return', 'S&P 500 Total Return', 'Combined Portfolio', 'Combined Portfolio']

        df = pd.DataFrame(list(zip(x_axis_rr_ss, y_vals, strat)),
                columns =['Type', 'Values', 'Strategy'])
        #print(df)

        fig = px.bar(df, x="Type", y="Values",
                color='Strategy', barmode='group',
                color_discrete_sequence = colors, template= 'plotly_white', 
                labels={
                    "Type": "",
                    "Values": "",
                    "Strategy" : ""
                    }, width= 500, height = 550)
        fig.update_traces(texttemplate='%{y:.2%}', textposition='outside')
        fig.update_layout(uniformtext_minsize=16, uniformtext_mode='hide')
        fig.update_traces(hovertemplate='%{y:.0%}')
        fig.update_yaxes(showticklabels = False)
        fig.update_layout( 
        title={
            'text': title,
            'y': 1,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font = dict(
            family="Circular STD",
            color="black"
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-.3,
        xanchor="left",
        x=0.11
        ),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
        )
        fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        fig.update_layout(xaxis_tickfont_size=19)
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_layout(margin = dict(l=10, r=0, t=100, b=0))

        return fig



    pie_fig     = graph_pie(percent_dict)
    line_fig    = graph_line_chart(df, choice)
    scatter_fig = graph_scatter_plot(risk_dic, return_dic)
    bar_rr_fig  = graph_barchart(x_axis_rr, y_combined_rr, y_6040_rr, y_spy_rr)
    bar_ss_fig  = graph_barchart(x_axis_ss, y_combined_ss, y_6040_ss, y_spy_ss)
    return pie_fig, line_fig, scatter_fig, bar_rr_fig, bar_ss_fig


#----------------------------------------------------------------------------END DASH STUFF--------------------------------------------------------------------------------------------------
# from dash_def import add_dash_yield

# cstr = f"postgresql://{cf.psql_user}:{cf.psql_pass}@"\
#        f"{cf.psql_host}/{cf.dbname}"


#app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)

# app.config['SQLALCHEMY_DATABASE_URI'] = cstr
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# db.Model = automap_base()
# db.Model.prepare(db.engine,reflect=True)
# coindata_day = db.Model.classes.coindata_day

# dash_app = add_dash_yield(app)

pairs = ['BTC-USDT', 'BCHABC-USDT', 'TRX-USDT', 'IOTA-USDT', 'XLM-USDT', 'EOS-USDT', 'ADA-USDT','LTC-USDT', 'NEO-USDT', 'BNB-USDT', 'ETH-USDT']
price_data={}
timestamp_data={}
LAST_UPDATE_HEATMAP = datetime.datetime(2019,1,1).date()
LAST_UPDATE_VOLATILITY = datetime.datetime(2019,1,1).date()
LAST_UPDATE_REL_PERF = datetime.datetime(2019,1,1).date()

ids_heatmap = None
graphJSON_heatmap= None
ids_timeline = None
graphJSON_timeline= None
corr_df = None

ids_volatility = None
graphJSON_volatility = None

def update_df(d):
    #update df 
    global price_data
    global timestamp_data
    global LAST_UPDATE_REL_PERF

    for sp in pairs:    
        x = get_coin_data(sp, 'Nothing', "nothing")
        price_data[sp] = x['price_close']
        timestamp_data[sp] = [ts*1000.0 for ts in x['timestamp']]

    LAST_UPDATE_REL_PERF = d

def update_heatmap(d):
    #define vars as in global namespace
    global corr_df
    global ids_heatmap
    global graphJSON_heatmap
    global ids_timeline
    global graphJSON_timeline
    global LAST_UPDATE_HEATMAP
 
    corr_df = create_corr(pairs, 'Nothing', 'Nothing')

    # since we're using UTF time, we'll need to use
    # the close of the previous day.
    xd = d - datetime.timedelta(days=1)

    ids, graphJSON = graph_heatmap(corr_df, xd.strftime('%Y-%m-%d'))
    ids_heatmap = ids
    graphJSON_heatmap = graphJSON

    ids, graphJSON = graph_timeline(corr_df, xd.strftime('%Y-%m-%d'))
    ids_timeline = ids
    graphJSON_timeline = graphJSON

    LAST_UPDATE_HEATMAP = d #update last update

def update_pie(d):
    #define vars as in global namespace
    global ids_pie
    global graphJSON_pie

    ids, graphJSON = graph_pie(d)
    ids_pie = ids
    graphJSON_pie = graphJSON

def update_scatter(d):
    #define vars as in global namespace
    global ids_pie
    global graphJSON_pie

    ids, graphJSON = graph_pie(d)
    ids_pie = ids
    graphJSON_pie = graphJSON

def update_bar(d):
    #define vars as in global namespace
    global ids_pie
    global graphJSON_pie

    ids, graphJSON = graph_pie(d)
    ids_pie = ids
    graphJSON_pie = graphJSON


def update_volatility(d):
    global corr_df
    global LAST_UPDATE_VOLATILITY
    global ids_volatility
    global graphJSON_volatility
    
    df = calc_volatility(pairs, 'Nothing', 'Nothing')

    # since we're using UTF time, we'll need to use
    # the close of the previous day.
    xd = d - datetime.timedelta(days=1)
    
    ids, graphJSON = graph_volatility(df, pairs, xd.strftime('%Y-%m-%d'))
    ids_volatility = ids
    graphJSON_volatility = graphJSON
    LAST_UPDATE_VOLATILITY = d #update last update

@app.errorhandler(404)
def page_not_found(e):
    #404 status handler
    return render_template('404.html'), 404

@app.route('/api/volatility')
def vol():
    today = datetime.datetime.now(tz=pytz.utc).date()
    
    if(LAST_UPDATE_VOLATILITY < today):
        update_volatility(today)

    return render_template('volatility.html', ids=ids_volatility, graphJSON=graphJSON_volatility)

@app.route('/api/cumulative_returns')
def cum_perf():
    today = datetime.datetime.now(tz=pytz.utc).date()

    if(LAST_UPDATE_REL_PERF < today):
        update_df(today)
    
    return render_template('cumulative_performance.html', 
                            pairs=pairs, prices=json.dumps(price_data),
                            timestamps = json.dumps(timestamp_data))

@app.route('/api/heatmap_timeline')
def heatmap_timeline():
    today = datetime.datetime.now(tz=pytz.utc).date()
    
    if(LAST_UPDATE_HEATMAP < today):
        update_heatmap(today)

    return render_template('heatmap_timeline.html', ids=ids_timeline, graphJSON=graphJSON_timeline)
    
@app.route('/api/heatmap')
def heatmap():
    today = datetime.datetime.now(tz=pytz.utc).date()
    
    if(LAST_UPDATE_HEATMAP < today):
        update_heatmap(today)


    return render_template('heatmap.html', ids=ids_heatmap, graphJSON=graphJSON_heatmap)
# @app.route('/api/piechart')
# def piechart():
#     dic = {'60/40' : .95, 'Bitoin': .05}
#     update_pie(dic)
@app.route('/dashboard')
def render_dashboard():
    return flask.redirect('/dash')
  
app_ = DispatcherMiddleware(app, {
    '/dash': app_dash.server
})

#run_simple('0.0.0.0', 8080, app_, use_reloader=True, use_debugger=True)
#     return render_template('piechart.html', ids=ids_pie, graphJSON=graphJSON_pie)
	

# @app.route('/api/v1/load_daily',methods=['GET'])
# def load_daily():

#     # get parameters
#     symbol = None
#     if request.args.get('symbol') is not None:
#         symbol = request.args['symbol']
        
#     if symbol is not None:
#         query = db.session.query(coindata_day)\
#                 .filter(coindata_day.symbolpair == symbol.upper())\
#                 .order_by(coindata_day.timestamp)
#     else:
#         query = db.session.query(coindata_day)\
#                           .order_by(coindata_day.timestamp)

#     try:
#         df = pd.read_sql(query.statement, query.session.bind)
    
#     except:
#         rd = {'msg': 'database query failed'}
#         return Response(json.dumps(rd),503)
        
#     if df is None or len(df) < 1:
#         rd = {'msg': 'no data'}
#         return Response(json.dumps(rd),200)

#     res = df[ ['timestamp','price_open','price_high',\
#                'price_low','price_close','n_trades',\
#                'volume' ]].to_dict(orient='list')
    
#     return jsonify(res)

@app.route('/_download_GARCH',methods=['GET'])
def _download_GARCH():
    return redirect("/api/static/data/btc_30_minute.csv")

# if __name__ == "__main__":
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     app.logger.handlers = gunicorn_logger.handlers
#     app.run(debug=False,host='127.0.0.1',port='5005')
#for local dev
if __name__ == "__main__":
   print('dev server')
   app.run(debug=True,host='0.0.0.0', port=8001)
