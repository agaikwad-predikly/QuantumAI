import sys
import psycopg2
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta, time
import math
from dateutil.relativedelta import relativedelta
import re

def get_connection_string():
	return "host=quantum-ai-db.cqmxufpxd5v3.us-west-1.rds.amazonaws.com dbname=quantum_ai_db user=quantum_admin password=Quantum#456"
#	return "dbname=quantum_ai_db user=postgres password=root"

def flatten(l):
    return map(lambda x: x[0], l)

def get_data(query):
	connection_string=get_connection_string()
	conn = psycopg2.connect(connection_string)
	ncurs = conn.cursor('csr')
	ncurs.execute(query)
	data =  ncurs.fetchall()
	ncurs.close()
	conn.commit()
	return data

def call_procedure(procedure_name, params):
	connection_string=get_connection_string()
	conn = psycopg2.connect(connection_string)
	try:
		ncurs = conn.cursor()
		ncurs.callproc(procedure_name,params)
		row = ncurs.fetchall()
		ncurs.close()
		conn.commit()
	finally:
		if conn is not None:
					conn.close()
	return row

def get_buy_ticker_fundamental_details():
	tickers = call_procedure("get_ticker_details_by_data_type","1")
	i = 0
	df = None
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_indicator_value_details",[ticker_id])
		if df is None:
			df = indicator
		else:
			df.append(indicator)
		i+=1
	return df

def get_nobuy_ticker_fundamental_details():
	tickers = call_procedure("get_ticker_details_by_data_type","2")
	i = 0
	df = None
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_indicator_value_details",[ticker_id])
		if df is None:
			df = indicator
		else:
			df.append(indicator)
		i+=1
	return df

def get_ticker_technical_details():
	tickers = call_procedure("get_ticker_details_by_data_type","0")
	i = 0
	df = None
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_technical_indicator_value_details",[ticker_id])
		if df is None:
			df = indicator
		else:
			df.append(indicator)
		i+=1
	return df