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
from helpers import graph_heatmap, create_corr
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

def check_latest(db, coindata_day):
'''     
Find the highest value UNIX timestamp in database

Inputs
------
db - database connection
coindata_day - table in database

Outputs
-------
query (datetime.date) - object with most recent update  
'''
        query = db.session.query(func.max(coindata_day.timestamp))
	query_date = datetime.fromtimestamp(query, tz=pytz.utc).date()
        return query_date

pairs = ['BTC-USDT', 'BCHABC-USDT', 'TRX-USDT', 'IOTA-USDT', 'XLM-USDT', 'EOS-USDT','XRP-USDT', 'ADA-USDT','LTC-USDT', 'NEO-USDT', 'BNB-USDT', 'ETH-USDT']

ids_heatmap = None
graphJSON_heatmap=None
corr_df = None
LAST_UPDATE_DATE = datetime.datetime(2019,1,1, tz=pytz.utc).date()

def update_heatmap(d):
'''
Function called when there is new data in DB to rebuild heatmap plot
'''
    #define vars as in global namespace
    global corr_df
    global ids_heatmap
    global graphJSON_heatmap
    global LAST_UPDATE_DATE
 
    corr_df = create_corr(pairs, db, coindata_day)
    ids, graphJSON = graph_heatmap(corr_df, d.strftime('%Y-%m-%d'))
    ids_heatmap = ids
    graphJSON_heatmap = graphJSON
    LAST_UPDATE_DATE = d #update most recent update date

@app.route('/heatmap')
def heatmap():
    db_date = check_latest(db, coindata_day)

    if(LAST_UPDATE_DATE < db_date): #most recent date in DB newer than update
        update_heatmap(db_date)

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

