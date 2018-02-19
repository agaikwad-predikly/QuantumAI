import sys
import psycopg2
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta, time
import math
from dateutil.relativedelta import relativedelta
import re
import os 

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

def get_short_sell_ticker_fundamental_details():
	tickers = call_procedure("get_ticker_details_by_data_type","3")
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

def generate_ticker_technical_details_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","0")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\technical"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_technical_indicator_value_details",[ticker_id])
		df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name','ticker_symbol',	'target',	'date',	'14_day_close_price_sma',	'14_day_close_price_high',	'14_day_close_price_low',	'14_day_50_day_sma',	'14_day_100_day_sma',	'14_day_200_day_sma'])
		df.to_csv(directory + "\\" + ticker_sym+".csv",  index=False, encoding='utf-8')
		i+=1
	return directory

def generate_ticker_fundamental_details_csv():	tickers = call_procedure("get_ticker_details_by_data_type","0")	i = 0	df = None	directory = os.path.dirname(os.path.realpath(__file__)) + "\\fundamental"	if not os.path.exists(directory):		os.makedirs(directory)	while i < len(tickers):		ticker_sym = tickers[i][1]		ticker_id = tickers[i][2]		indicator = call_procedure("get_ticker_indicator_value_details",[ticker_id])		df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name',	'ticker_symbol',	'target',	'date',	'analyst_estimate_earning_per_share_high_annual_value',	'analyst_estimate_earning_per_share_high_quarterly_value',	'analyst_estimate_earning_per_share_low_annual_value',	'analyst_estimate_earning_per_share_low_quarterly_value',	'analyst_estimate_earning_per_share_mean_annual_value',	'analyst_estimate_earning_per_share_mean_quarterly_value',	'analyst_estimate_gross_profit_margin_high_annual_value',	'analyst_estimate_gross_profit_margin_high_quarterly_value',	'analyst_estimate_gross_profit_margin_low_annual_value',	'analyst_estimate_gross_profit_margin_low_quarterly_value',	'analyst_estimate_gross_profit_margin_mean_annual_value',	'analyst_estimate_gross_profit_margin_mean_quarterly_value',	'analyst_estimate_net_income_high_annual_value',	'analyst_estimate_net_income_high_quarterly_value',	'analyst_estimate_net_income_low_annual_value',	'analyst_estimate_net_income_low_quarterly_value',	'analyst_estimate_net_income_mean_annual_value',	'analyst_estimate_net_income_mean_quarterly_value',	'analyst_estimate_revenue_high_annual_value',	'analyst_estimate_revenue_high_quarterly_value', 'analyst_estimate_revenue_low_annual_value',	'analyst_estimate_revenue_low_quarterly_value',	'analyst_estimate_revenue_mean_annual_value',	'analyst_estimate_revenue_mean_quarterly_value',	'company_estimate_earning_per_share_mean_annual_value',	'company_estimate_earning_per_share_mean_quarterly_value',	'company_estimate_net_income_mean_annual_value',	'company_estimate_net_income_mean_quarterly_value',	'company_estimate_revenue_mean_annual_value',	'company_estimate_revenue_mean_quarterly_value',	'company_estimate_gross_profit_margin_mean_annual_value',	'company_estimate_gross_profit_margin_mean_quarterly_value',	'earning_per_share_annual_value',	'earning_per_share_quarterly_value',	'net_income_annual_value',	'net_income_quarterly_value',	'gross_profit_margin_annual_value',	'gross_profit_margin_quarterly_value',	'revenue_annual_value',	'revenue_quarterly_value',	'analyst_estimate_earning_per_share_high_annual',	'analyst_estimate_earning_per_share_high_quarterly',	'analyst_estimate_earning_per_share_low_annual',	'analyst_estimate_earning_per_share_low_quarterly',	'analyst_estimate_earning_per_share_mean_annual',	'analyst_estimate_earning_per_share_mean_quarterly',	'analyst_estimate_gross_profit_margin_high_annual',	'analyst_estimate_gross_profit_margin_high_quarterly',	'analyst_estimate_gross_profit_margin_low_annual',	'analyst_estimate_gross_profit_margin_low_quarterly',	'analyst_estimate_gross_profit_margin_mean_annual',	'analyst_estimate_gross_profit_margin_mean_quarterly',	'analyst_estimate_net_income_high_annual', 'analyst_estimate_net_income_high_quarterly',	'analyst_estimate_net_income_low_annual',	'analyst_estimate_net_income_low_quarterly',	'analyst_estimate_net_income_mean_annual',	'analyst_estimate_net_income_mean_quarterly',	'analyst_estimate_revenue_high_annual',	'analyst_estimate_revenue_high_quarterly',	'analyst_estimate_revenue_low_annual',	'analyst_estimate_revenue_low_quarterly',	'analyst_estimate_revenue_mean_annual',	'analyst_estimate_revenue_mean_quarterly',	'company_estimate_earning_per_share_mean_annual',	'company_estimate_earning_per_share_mean_quarterly',	'company_estimate_net_income_mean_annual',	'company_estimate_net_income_mean_quarterly',	'company_estimate_revenue_mean_annual',	'company_estimate_revenue_mean_quarterly',	'company_estimate_gross_profit_margin_mean_annual',	'company_estimate_gross_profit_margin_mean_quarterly',	'earning_per_share_annual',	'earning_per_share_quarterly',	'net_income_annual',	'net_income_quarterly',	'non_gaap_gross_margin_annual',	'non_gaap_gross_margin_quarterly',	'revenue_annual',	'revenue_quarterly',	'analyst_estimate_earning_per_share_high_annual_acc_dcc',	'analyst_estimate_earning_per_share_high_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_low_annual_acc_dcc',	'analyst_estimate_earning_per_share_low_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_mean_annual_acc_dcc',	'analyst_estimate_earning_per_share_mean_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_high_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_high_quarterly_acc_dcc', 'analyst_estimate_gross_profit_margin_low_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_low_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'analyst_estimate_net_income_high_annual_acc_dcc',	'analyst_estimate_net_income_high_quarterly_acc_dcc',	'analyst_estimate_net_income_low_annual_acc_dcc',	'analyst_estimate_net_income_low_quarterly_acc_dcc',	'analyst_estimate_net_income_mean_annual_acc_dcc',	'analyst_estimate_net_income_mean_quarterly_acc_dcc',	'analyst_estimate_revenue_high_annual_acc_dcc',	'analyst_estimate_revenue_high_quarterly_acc_dcc',	'analyst_estimate_revenue_low_annual_acc_dcc',	'analyst_estimate_revenue_low_quarterly_acc_dcc',	'analyst_estimate_revenue_mean_annual_acc_dcc',	'analyst_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_earning_per_share_mean_annual_acc_dcc',	'company_estimate_earning_per_share_mean_quarterly_acc_dcc',	'company_estimate_net_income_mean_annual_acc_dcc',	'company_estimate_net_income_mean_quarterly_acc_dcc',	'company_estimate_revenue_mean_annual_acc_dcc',	'company_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_gross_profit_margin_mean_annual_acc_dcc',	'company_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'earning_per_share_annual_acc_dcc',	'earning_per_share_quarterly_acc_dcc',	'net_income_annual_acc_dcc',	'net_income_quarterly_acc_dcc',	'non_gaap_gross_margin_annual_acc_dcc',	'non_gaap_gross_margin_quarterly_acc_dcc',	'revenue_annual_acc_dcc', 'revenue_quarterly_acc_dcc'])		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')		i+=1	return directorygenerate_ticker_fundamental_details_csv()
generate_ticker_technical_details_csv()