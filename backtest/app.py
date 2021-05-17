#!/usr/bin/env python3
import sys
import json
import collections
from flask import g,Flask,render_template,jsonify,request,Response,url_for,\
    redirect
from flask_cors import CORS
from flask_basicauth import BasicAuth
import pandas as pd
import numpy as np
import sqlite3
import helpers as hp

app = Flask(__name__)
CORS(app)

app.config['BASIC_AUTH_USERNAME'] = 'make'
app.config['BASIC_AUTH_PASSWORD'] = 'more money'
app.config['BASIC_AUTH_FORCE'] = True
app.config['SECRET_KEY'] = 'guenniform'

basic_auth = BasicAuth(app)


sqlite_db = 'backtest.sqlite'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(sqlite_db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')


@app.route('/data/btc/<btid>',methods=["GET"])
@basic_auth.required
def btdata(btid):

    conn = get_db()
    conn.row_factory = hp.dict_factory
    cur = conn.cursor()
    
    query = f"select * from btc where backtest_id = {int(btid)} "\
             "order by date"
    cur.execute(query)
    res = cur.fetchall()

    if len(res) == 0:
        return jsonify({})

    # prepare results dict
    DataStore = {}
    DataStore['date'] = [x['date'] for x in res]
    DataStore['strategy'] = [ [x['date'],x['strategy_return']] for \
                              x in res ]
    DataStore['market'] = [ [x['date'],x['market_return']] for \
                            x in res ]
    DataStore['treasury'] = [ [x['date'],x['treasury']] for \
                            x in res ]
    
    DataStore['price'] = [ [x['date'],x['price']] for \
                            x in res ]

    return jsonify(DataStore)

