#!/usr/bin/env python3
import os
import sys
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import config as cf

# this requires that the relevant users have been
# set up in postgres, including dbreader


all_read_users =['dbreader']

dbname = "bflabs_ohlcv"
xdbname = "postgres"
psql_user = cf.psql_user
psql_pass = cf.psql_pass
psql_host = 'localhost'
connection_string = ("dbname='%s' "
                     "user='%s' "
                     "host='%s' "
                     "password='%s'" % (xdbname,
                                        psql_user, psql_host, psql_pass))
conn = psycopg2.connect(connection_string)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor(cursor_factory=DictCursor)
query = f"create database {dbname}"
cur.execute(query)
conn.commit()

# now connect to our table
psql_user = cf.psql_user
psql_pass = cf.psql_pass
psql_host = 'localhost'
connection_string = ("dbname='%s' "
                     "user='%s' "
                     "host='%s' "
                     "password='%s'" % (dbname,
                                        psql_user, psql_host, psql_pass))
conn = psycopg2.connect(connection_string)
cur = conn.cursor(cursor_factory=DictCursor)

table_name = "coindata_day"
query = ("CREATE TABLE %s ("
                          "ID SERIAL PRIMARY KEY, "
                          "symbolpair VARCHAR(30) NOT NULL, "
                          "exid INT NOT NULL,"
                          "timestamp INT NOT NULL, "
                          "price_open DOUBLE PRECISION NOT NULL, "
                          "price_high DOUBLE PRECISION NOT NULL, "
                          "price_low DOUBLE PRECISION NOT NULL, "
                          "price_close DOUBLE PRECISION NOT NULL, "
                          "volume DOUBLE PRECISION NOT NULL, "
                          "n_trades INT NOT NULL)" % table_name)

cur.execute(query)
index = "CREATE INDEX %s_ts_idx ON %s(timestamp)" % (table_name,table_name)
cur.execute(index)
index = "CREATE INDEX %s_symb_idx ON %s(symbolpair)" % (table_name,table_name)
cur.execute(index)
index = "CREATE INDEX %s_ex_idx ON %s(exid)" % (table_name, table_name)
cur.execute(index)
index = "CREATE INDEX %s_comb_idx ON %s(timestamp,symbolpair,exid)" % (table_name, table_name)
cur.execute(index)
conn.commit()

for user in all_read_users:
    query = "GRANT USAGE ON SCHEMA public to %s" % user
    cur.execute(query)
    query = "GRANT SELECT ON %s to %s" % (table_name, user)
    cur.execute(query)

conn.commit()
    
