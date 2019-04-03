#!/usr/bin/env python3
import sys
import pandas as pd
import json
from flask import Flask,jsonify,request,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import config as cf

cstr = f"postgresql://{cf.psql_user}:{cf.psql_pass}@"\
       f"{cf.psql_host}/{cf.dbname}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = cstr
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.Model = automap_base()
db.Model.prepare(db.engine,reflect=True)
coindata_day = db.Model.classes.coindata_day



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
    



