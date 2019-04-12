#!/usr/bin/env python3
import sys
import pandas as pd
import json
from flask import Flask,jsonify,request,Response,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.contrib.fixers import ProxyFix
from helpers import graph_heatmap, create_corr, volatility, calc_volatility, graph_volatility, get_coin_data, graph_timeline
from variables import IMG, RANGE, ANNOT, PLOT_CONFIG, XAXIS, YAXIS, COLORSCALE
import datetime
import pytz
import config as cf

cstr = f"postgresql://{cf.psql_user}:{cf.psql_pass}@"\
       f"{cf.psql_host}/{cf.dbname}"

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)

app.config['SQLALCHEMY_DATABASE_URI'] = cstr
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.Model = automap_base()
db.Model.prepare(db.engine,reflect=True)
coindata_day = db.Model.classes.coindata_day

pairs = ['BTC-USDT', 'BCHABC-USDT', 'TRX-USDT', 'IOTA-USDT', 'XLM-USDT', 'EOS-USDT','XRP-USDT', 'ADA-USDT','LTC-USDT', 'NEO-USDT', 'BNB-USDT', 'ETH-USDT']

LAST_UPDATE_HEATMAP = datetime.datetime(2019,1,1).date()
LAST_UPDATE_VOLATILITY = datetime.datetime(2019,1,1).date()

ids_heatmap = None
graphJSON_heatmap= None
ids_timeline = None
graphJSON_timeline= None
corr_df = None

ids_volatility = None
graphJSON_volatility = None

def update_heatmap(d):
    #define vars as in global namespace
    global corr_df
    global ids_heatmap
    global graphJSON_heatmap
    global ids_timeline
    global graphJSON_timeline
    global LAST_UPDATE_HEATMAP
 
    corr_df = create_corr(pairs, db, coindata_day)

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

def update_volatility(d):
    global corr_df
    global LAST_UPDATE_VOLATILITY
    global ids_volatility
    global graphJSON_volatility
    
    df = calc_volatility(pairs, db, coindata_day)

    # since we're using UTF time, we'll need to use
    # the close of the previous day.
    xd = d - datetime.timedelta(days=1)
    
    ids, graphJSON = graph_volatility(df, pairs, xd.strftime('%Y-%m-%d'))
    ids_volatility = ids
    graphJSON_volatility = graphJSON
    LAST_UPDATE_VOLATILITY = d #update last update

@app.route('/volatility')
def vol():
    today = datetime.datetime.now(tz=pytz.utc).date()
    
    if(LAST_UPDATE_VOLATILITY < today):
        update_volatility(today)

    return render_template('volatility.html', ids=ids_volatility, graphJSON=graphJSON_volatility)


@app.route('/heatmap_timeline')
def heatmap_timeline():
    today = datetime.datetime.now(tz=pytz.utc).date()
    
    if(LAST_UPDATE_HEATMAP < today):
        update_heatmap(today)

    return render_template('heatmap_timeline.html', ids=ids_timeline, graphJSON=graphJSON_timeline)
    
@app.route('/heatmap')
def heatmap():
    today = datetime.datetime.now(tz=pytz.utc).date()
    
    if(LAST_UPDATE_HEATMAP < today):
        update_heatmap(today)


    return render_template('heatmap.html', ids=ids_heatmap, graphJSON=graphJSON_heatmap)
	

@app.route('/api/v1/load_daily',methods=['GET'])
def load_daily():

    # get parameters
    symbol = None
    if request.args.get('symbol') is not None:
        symbol = request.args['symbol']
        
    if symbol is not None:
        query = db.session.query(coindata_day)\
                .filter(coindata_day.symbolpair == symbol.upper())\
                .order_by(coindata_day.timestamp)
    else:
        query = db.session.query(coindata_day)\
                          .order_by(coindata_day.timestamp)

    try:
        df = pd.read_sql(query.statement, query.session.bind)
    
    except:
        rd = {'msg': 'database query failed'}
        return Response(json.dumps(rd),503)
        
    if df is None or len(df) < 1:
        rd = {'msg': 'no data'}
        return Response(json.dumps(rd),200)

    res = df[ ['timestamp','price_open','price_high',\
               'price_low','price_close','n_trades',\
               'volume' ]].to_dict(orient='list')
    
    return jsonify(res)
    
if __name__ == "__main__":
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.run(debug=False,host='127.0.0.1',port='5005')

