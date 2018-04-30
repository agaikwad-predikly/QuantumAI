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
import requests
from pandas.io.json.normalize import json_normalize
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
		indicator = call_procedure("get_ticker_technical_indicator_value_details_without_target",[ticker_id])
		if df is None:
			df = indicator
		else:
			df.append(indicator)
		i+=1
	return df


def get_ticker_fundamental_details():
	tickers = call_procedure("get_ticker_details_by_data_type","0")
	i = 0
	df = None
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_fundamental_indicator_value_details",[ticker_id])
		if df is None:
			df = indicator
		else:
			df.append(indicator)
		i+=1
	return df

def generate_ticker_technical_details_csv():
	try:
		tickers = call_procedure("get_ticker_details_by_data_type","0")
		i = 0
		df = None
		directory = os.path.dirname(os.path.realpath(__file__)) + "\\technical"
		if not os.path.exists(directory):
			os.makedirs(directory)
		while i < len(tickers):
			ticker_sym = tickers[i][1]
			ticker_id = tickers[i][2]
			indicator = call_procedure("get_ticker_technical_indicator_value_details_without_target",[ticker_id])
			df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name','ticker_symbol',	'date',	'14_day_close_price_sma',	'14_day_close_price_high',	'14_day_close_price_low',	'14_day_50_day_sma',	'14_day_100_day_sma',	'14_day_200_day_sma'])
			df.to_csv(directory + "\\" + ticker_sym+".csv",  index=False, encoding='utf-8')
			i+=1
		return directory
	except Exception as e:
			print(e + "Error")

def generate_ticker_fundamental_details_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","0")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\fundamental"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_fundamental_daily_without_target_value_details",[ticker_id])
		df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name',	'ticker_symbol',	'date',	'analyst_estimate_earning_per_share_high_annual_value',	'analyst_estimate_earning_per_share_high_quarterly_value',	'analyst_estimate_earning_per_share_low_annual_value',	'analyst_estimate_earning_per_share_low_quarterly_value',	'analyst_estimate_earning_per_share_mean_annual_value',	'analyst_estimate_earning_per_share_mean_quarterly_value',	'analyst_estimate_gross_profit_margin_high_annual_value',	'analyst_estimate_gross_profit_margin_high_quarterly_value',	'analyst_estimate_gross_profit_margin_low_annual_value',	'analyst_estimate_gross_profit_margin_low_quarterly_value',	'analyst_estimate_gross_profit_margin_mean_annual_value',	'analyst_estimate_gross_profit_margin_mean_quarterly_value',	'analyst_estimate_net_income_high_annual_value',	'analyst_estimate_net_income_high_quarterly_value',	'analyst_estimate_net_income_low_annual_value',	'analyst_estimate_net_income_low_quarterly_value',	'analyst_estimate_net_income_mean_annual_value',	'analyst_estimate_net_income_mean_quarterly_value',	'analyst_estimate_revenue_high_annual_value',	'analyst_estimate_revenue_high_quarterly_value', 'analyst_estimate_revenue_low_annual_value',	'analyst_estimate_revenue_low_quarterly_value',	'analyst_estimate_revenue_mean_annual_value',	'analyst_estimate_revenue_mean_quarterly_value',	'company_estimate_earning_per_share_mean_annual_value',	'company_estimate_earning_per_share_mean_quarterly_value',	'company_estimate_net_income_mean_annual_value',	'company_estimate_net_income_mean_quarterly_value',	'company_estimate_revenue_mean_annual_value',	'company_estimate_revenue_mean_quarterly_value',	'company_estimate_gross_profit_margin_mean_annual_value',	'company_estimate_gross_profit_margin_mean_quarterly_value',	'earning_per_share_annual_value',	'earning_per_share_quarterly_value',	'net_income_annual_value',	'net_income_quarterly_value',	'gross_profit_margin_annual_value',	'gross_profit_margin_quarterly_value',	'revenue_annual_value',	'revenue_quarterly_value',	'analyst_estimate_earning_per_share_high_annual',	'analyst_estimate_earning_per_share_high_quarterly',	'analyst_estimate_earning_per_share_low_annual',	'analyst_estimate_earning_per_share_low_quarterly',	'analyst_estimate_earning_per_share_mean_annual',	'analyst_estimate_earning_per_share_mean_quarterly',	'analyst_estimate_gross_profit_margin_high_annual',	'analyst_estimate_gross_profit_margin_high_quarterly',	'analyst_estimate_gross_profit_margin_low_annual',	'analyst_estimate_gross_profit_margin_low_quarterly',	'analyst_estimate_gross_profit_margin_mean_annual',	'analyst_estimate_gross_profit_margin_mean_quarterly',	'analyst_estimate_net_income_high_annual', 'analyst_estimate_net_income_high_quarterly',	'analyst_estimate_net_income_low_annual',	'analyst_estimate_net_income_low_quarterly',	'analyst_estimate_net_income_mean_annual',	'analyst_estimate_net_income_mean_quarterly',	'analyst_estimate_revenue_high_annual',	'analyst_estimate_revenue_high_quarterly',	'analyst_estimate_revenue_low_annual',	'analyst_estimate_revenue_low_quarterly',	'analyst_estimate_revenue_mean_annual',	'analyst_estimate_revenue_mean_quarterly',	'company_estimate_earning_per_share_mean_annual',	'company_estimate_earning_per_share_mean_quarterly',	'company_estimate_net_income_mean_annual',	'company_estimate_net_income_mean_quarterly',	'company_estimate_revenue_mean_annual',	'company_estimate_revenue_mean_quarterly',	'company_estimate_gross_profit_margin_mean_annual',	'company_estimate_gross_profit_margin_mean_quarterly',	'earning_per_share_annual',	'earning_per_share_quarterly',	'net_income_annual',	'net_income_quarterly',	'non_gaap_gross_margin_annual',	'non_gaap_gross_margin_quarterly',	'revenue_annual',	'revenue_quarterly',	'analyst_estimate_earning_per_share_high_annual_acc_dcc',	'analyst_estimate_earning_per_share_high_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_low_annual_acc_dcc',	'analyst_estimate_earning_per_share_low_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_mean_annual_acc_dcc',	'analyst_estimate_earning_per_share_mean_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_high_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_high_quarterly_acc_dcc', 'analyst_estimate_gross_profit_margin_low_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_low_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'analyst_estimate_net_income_high_annual_acc_dcc',	'analyst_estimate_net_income_high_quarterly_acc_dcc',	'analyst_estimate_net_income_low_annual_acc_dcc',	'analyst_estimate_net_income_low_quarterly_acc_dcc',	'analyst_estimate_net_income_mean_annual_acc_dcc',	'analyst_estimate_net_income_mean_quarterly_acc_dcc',	'analyst_estimate_revenue_high_annual_acc_dcc',	'analyst_estimate_revenue_high_quarterly_acc_dcc',	'analyst_estimate_revenue_low_annual_acc_dcc',	'analyst_estimate_revenue_low_quarterly_acc_dcc',	'analyst_estimate_revenue_mean_annual_acc_dcc',	'analyst_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_earning_per_share_mean_annual_acc_dcc',	'company_estimate_earning_per_share_mean_quarterly_acc_dcc',	'company_estimate_net_income_mean_annual_acc_dcc',	'company_estimate_net_income_mean_quarterly_acc_dcc',	'company_estimate_revenue_mean_annual_acc_dcc',	'company_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_gross_profit_margin_mean_annual_acc_dcc',	'company_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'earning_per_share_annual_acc_dcc',	'earning_per_share_quarterly_acc_dcc',	'net_income_annual_acc_dcc',	'net_income_quarterly_acc_dcc',	'non_gaap_gross_margin_annual_acc_dcc',	'non_gaap_gross_margin_quarterly_acc_dcc',	'revenue_annual_acc_dcc', 'revenue_quarterly_acc_dcc'])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

def generate_ticker__both_combined_details_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","0")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\fundamental_technical_all"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_fundamental_technical_with_target_value_daily",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name", "ticker_symbol", "value_date","analyst_estimate_earning_per_share_high_annual","analyst_estimate_earning_per_share_high_quarterly","analyst_estimate_earning_per_share_mean_annual","analyst_estimate_earning_per_share_mean_quarterly","analyst_estimate_net_income_high_annual","analyst_estimate_net_income_high_quarterly","analyst_estimate_net_income_mean_annual","analyst_estimate_net_income_mean_quarterly","analyst_estimate_revenue_high_annual","analyst_estimate_revenue_high_quarterly","analyst_estimate_revenue_mean_annual","analyst_estimate_revenue_mean_quarterly","company_estimate_revenue_mean_annual","company_estimate_revenue_mean_quarterly","14_day_close_price_sma","14_day_50_day_sma", "14_day_100_day_sma","14_day_200_day_sma","fundamental_strength","pred_short_sell_fund_target","pred_short_sell_fund_probability","pred_tech_target","pred_tech_probability"])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

def update_ticker_indicator_prediction():
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\results_Short_sale"
	for root,dirs,files in os.walk(directory):
		for file in files:
			if file.endswith(".csv"):
				dt = pd.read_csv(directory +"\\" +  file)
				if not dt.empty:
					for index, row in dt.iterrows():
						try:
							print(row['ticker_id'], 2, row['PREDICTED'], row['1'],row['0'], row['date'] )
							call_procedure("update_indicator_target_data",[row['ticker_id'], 2, row['PREDICTED'], row['1'],row['0'], row['date'] ])
						except Exception as e:
							print(e + "Error")

					print("done")

					
def generate_ticker_future_buy_fundamental_details_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","1")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\buy_fundamental"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_future_indicator_value_details_with_target",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" , "target" , "year" , "quarter" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" ,"company_estimate_earning_per_share_mean_quarterly" , "company_estimate_gross_profit_margin_mean_quarterly" , "company_estimate_net_income_mean_quarterly" , "company_estimate_revenue_mean_quarterly" , "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "company_estimate_earning_per_share_mean_annual" , "company_estimate_gross_profit_margin_mean_annual" , "company_estimate_net_income_mean_annual" , "company_estimate_revenue_mean_annual" ])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

					
def generate_ticker_future_nobuy_fundamental_details_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","2")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\nobuy_fundamental"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_future_indicator_value_details_with_target",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" , "target" , "year" , "quarter" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" , "company_estimate_earning_per_share_mean_quarterly" , "company_estimate_gross_profit_margin_mean_quarterly" , "company_estimate_net_income_mean_quarterly" , "company_estimate_revenue_mean_quarterly" , "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "company_estimate_earning_per_share_mean_annual" , "company_estimate_gross_profit_margin_mean_annual" , "company_estimate_net_income_mean_annual" , "company_estimate_revenue_mean_annual" ])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

def generate_ticker_future_sell_fundamental_details_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","3")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\sell_fundamental"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_future_indicator_value_details_with_target",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" , "target" , "year" , "quarter" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" , "company_estimate_earning_per_share_mean_quarterly" , "company_estimate_gross_profit_margin_mean_quarterly" , "company_estimate_net_income_mean_quarterly" , "company_estimate_revenue_mean_quarterly" , "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "company_estimate_earning_per_share_mean_annual" , "company_estimate_gross_profit_margin_mean_annual" , "company_estimate_net_income_mean_annual" , "company_estimate_revenue_mean_annual" ])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

def generate_ticker_future_buy_fundamental_details_new_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","1")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\buy_fundamental_new"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_future_indicator_value_details_with_target_new",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" , "target" , "date" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" ,  "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "actual_net_income_quarterly", "actual_gross_profit_margin_quarterly", "actual_revenue_quarterly", "actual_earning_per_share_quarterly", "actual_net_income_annual","actual_gross_profit_margin_annual", "actual_revenue_annual", "actual_earning_per_share_annual" ])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

					
			
def generate_ticker_future_nobuy_fundamental_details_new_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","2")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\nobuy_fundamental_new"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_future_indicator_value_details_with_target_new",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" , "target" , "date" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" ,  "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "actual_net_income_quarterly", "actual_gross_profit_margin_quarterly", "actual_revenue_quarterly", "actual_earning_per_share_quarterly", "actual_net_income_annual","actual_gross_profit_margin_annual", "actual_revenue_annual", "actual_earning_per_share_annual" ])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

def generate_ticker_future_sell_fundamental_details_new_csv():
	tickers = call_procedure("get_ticker_details_by_data_type","3")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\sell_fundamental_new"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_future_indicator_value_details_with_target_new",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" , "target" , "date" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" ,  "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "actual_net_income_quarterly", "actual_gross_profit_margin_quarterly", "actual_revenue_quarterly", "actual_earning_per_share_quarterly", "actual_net_income_annual","actual_gross_profit_margin_annual", "actual_revenue_annual", "actual_earning_per_share_annual"])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory


def generate_tickernew_alog_sell_fundamental_details_csv():
	try:
		tickers = call_procedure("get_ticker_details_by_data_type","0")
		i = 0
		directory = os.path.dirname(os.path.realpath(__file__)) + "\\BUY_NOBUY"
		if not os.path.exists(directory):
			os.makedirs(directory)
		while i < len(tickers):
			ticker_sym = tickers[i][1]
			ticker_id = tickers[i][2]
			print("JOB STARTED:" + ticker_sym)
			filename = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +".csv"
			try:
				indicator = call_procedure("get_ticker_fundamental_without_target_value_details",[ticker_id])
				df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name',	'ticker_symbol',	'date',	'analyst_estimate_earning_per_share_high_annual_value',	'analyst_estimate_earning_per_share_high_quarterly_value',	'analyst_estimate_earning_per_share_low_annual_value',	'analyst_estimate_earning_per_share_low_quarterly_value',	'analyst_estimate_earning_per_share_mean_annual_value',	'analyst_estimate_earning_per_share_mean_quarterly_value',	'analyst_estimate_gross_profit_margin_high_annual_value',	'analyst_estimate_gross_profit_margin_high_quarterly_value',	'analyst_estimate_gross_profit_margin_low_annual_value',	'analyst_estimate_gross_profit_margin_low_quarterly_value',	'analyst_estimate_gross_profit_margin_mean_annual_value',	'analyst_estimate_gross_profit_margin_mean_quarterly_value',	'analyst_estimate_net_income_high_annual_value',	'analyst_estimate_net_income_high_quarterly_value',	'analyst_estimate_net_income_low_annual_value',	'analyst_estimate_net_income_low_quarterly_value',	'analyst_estimate_net_income_mean_annual_value',	'analyst_estimate_net_income_mean_quarterly_value',	'analyst_estimate_revenue_high_annual_value',	'analyst_estimate_revenue_high_quarterly_value', 'analyst_estimate_revenue_low_annual_value',	'analyst_estimate_revenue_low_quarterly_value',	'analyst_estimate_revenue_mean_annual_value',	'analyst_estimate_revenue_mean_quarterly_value',	'company_estimate_earning_per_share_mean_annual_value',	'company_estimate_earning_per_share_mean_quarterly_value',	'company_estimate_net_income_mean_annual_value',	'company_estimate_net_income_mean_quarterly_value',	'company_estimate_revenue_mean_annual_value',	'company_estimate_revenue_mean_quarterly_value',	'company_estimate_gross_profit_margin_mean_annual_value',	'company_estimate_gross_profit_margin_mean_quarterly_value',	'earning_per_share_annual_value',	'earning_per_share_quarterly_value',	'net_income_annual_value',	'net_income_quarterly_value',	'gross_profit_margin_annual_value',	'gross_profit_margin_quarterly_value',	'revenue_annual_value',	'revenue_quarterly_value',	'analyst_estimate_earning_per_share_high_annual',	'analyst_estimate_earning_per_share_high_quarterly',	'analyst_estimate_earning_per_share_low_annual',	'analyst_estimate_earning_per_share_low_quarterly',	'analyst_estimate_earning_per_share_mean_annual',	'analyst_estimate_earning_per_share_mean_quarterly',	'analyst_estimate_gross_profit_margin_high_annual',	'analyst_estimate_gross_profit_margin_high_quarterly',	'analyst_estimate_gross_profit_margin_low_annual',	'analyst_estimate_gross_profit_margin_low_quarterly',	'analyst_estimate_gross_profit_margin_mean_annual',	'analyst_estimate_gross_profit_margin_mean_quarterly',	'analyst_estimate_net_income_high_annual', 'analyst_estimate_net_income_high_quarterly',	'analyst_estimate_net_income_low_annual',	'analyst_estimate_net_income_low_quarterly',	'analyst_estimate_net_income_mean_annual',	'analyst_estimate_net_income_mean_quarterly',	'analyst_estimate_revenue_high_annual',	'analyst_estimate_revenue_high_quarterly',	'analyst_estimate_revenue_low_annual',	'analyst_estimate_revenue_low_quarterly',	'analyst_estimate_revenue_mean_annual',	'analyst_estimate_revenue_mean_quarterly',	'company_estimate_earning_per_share_mean_annual',	'company_estimate_earning_per_share_mean_quarterly',	'company_estimate_net_income_mean_annual',	'company_estimate_net_income_mean_quarterly',	'company_estimate_revenue_mean_annual',	'company_estimate_revenue_mean_quarterly',	'company_estimate_gross_profit_margin_mean_annual',	'company_estimate_gross_profit_margin_mean_quarterly',	'earning_per_share_annual',	'earning_per_share_quarterly',	'net_income_annual',	'net_income_quarterly',	'non_gaap_gross_margin_annual',	'non_gaap_gross_margin_quarterly',	'revenue_annual',	'revenue_quarterly',	'analyst_estimate_earning_per_share_high_annual_acc_dcc',	'analyst_estimate_earning_per_share_high_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_low_annual_acc_dcc',	'analyst_estimate_earning_per_share_low_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_mean_annual_acc_dcc',	'analyst_estimate_earning_per_share_mean_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_high_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_high_quarterly_acc_dcc', 'analyst_estimate_gross_profit_margin_low_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_low_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'analyst_estimate_net_income_high_annual_acc_dcc',	'analyst_estimate_net_income_high_quarterly_acc_dcc',	'analyst_estimate_net_income_low_annual_acc_dcc',	'analyst_estimate_net_income_low_quarterly_acc_dcc',	'analyst_estimate_net_income_mean_annual_acc_dcc',	'analyst_estimate_net_income_mean_quarterly_acc_dcc',	'analyst_estimate_revenue_high_annual_acc_dcc',	'analyst_estimate_revenue_high_quarterly_acc_dcc',	'analyst_estimate_revenue_low_annual_acc_dcc',	'analyst_estimate_revenue_low_quarterly_acc_dcc',	'analyst_estimate_revenue_mean_annual_acc_dcc',	'analyst_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_earning_per_share_mean_annual_acc_dcc',	'company_estimate_earning_per_share_mean_quarterly_acc_dcc',	'company_estimate_net_income_mean_annual_acc_dcc',	'company_estimate_net_income_mean_quarterly_acc_dcc',	'company_estimate_revenue_mean_annual_acc_dcc',	'company_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_gross_profit_margin_mean_annual_acc_dcc',	'company_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'earning_per_share_annual_acc_dcc',	'earning_per_share_quarterly_acc_dcc',	'net_income_annual_acc_dcc',	'net_income_quarterly_acc_dcc',	'non_gaap_gross_margin_annual_acc_dcc',	'non_gaap_gross_margin_quarterly_acc_dcc',	'revenue_annual_acc_dcc', 'revenue_quarterly_acc_dcc'])
				df.to_csv(filename, index=False, encoding='utf-8')
				API_ENDPOINT = "http://13.126.153.34:8004/ocpu/user/mahi/library/buyWestimate/R/buyWesti/json"
				f =open(filename,'rb')
				files = {'input': f}
				r = requests.post(API_ENDPOINT, files=files)
				if not r.json() is None:
					dt = json_normalize(r.json())
					print(dt.columns.tolist())
					df["ml_result"] =dt["PREDICTED"]
					filename2 = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +"_complete.csv"
					df.to_csv(filename2, index=False, encoding='utf-8')
				
					#for data in r.json():
					#	db.call_procedure("update_indicator_target_data",[data['ticker_id'], 1,data['newdata$PREDICTED'], data['1'],data['0'], data['date'] ])
			except Exception as e:
					#log.Error(e)
					print(e.message)
			finally:
				i=i+1
				f.close()
				
	except Exception as e:
		print(e.message)
			#log.Error(e)
			

def generate_ticker_alog_sell_fundamental_details_csv():
	try:
		tickers = call_procedure("get_ticker_details_by_data_type","0")
		i = 0
		directory = os.path.dirname(os.path.realpath(__file__)) + "\\New_BUY_NOBUY"
		if not os.path.exists(directory):
			os.makedirs(directory)
		while i < len(tickers):
			ticker_sym = tickers[i][1]
			ticker_id = tickers[i][2]
			print("JOB STARTED:" + ticker_sym)
			filename = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +".csv"
			try:
				indicator = call_procedure("get_ticker_future_indicator_value_details_with_target_new",[ticker_id])
				df = pd.DataFrame(indicator,columns=["ticker_id","ticker_name","ticker_symbol","target","date","analyst_estimate_earning_per_share_high_quarterly","analyst_estimate_earning_per_share_mean_quarterly","analyst_estimate_gross_profit_margin_high_quarterly","analyst_estimate_gross_profit_margin_mean_quarterly","analyst_estimate_net_income_high_quarterly","analyst_estimate_net_income_mean_quarterly","analyst_estimate_revenue_high_quarterly","analyst_estimate_revenue_mean_quarterly","analyst_estimate_earning_per_share_high_annual","analyst_estimate_earning_per_share_mean_annual","analyst_estimate_gross_profit_margin_high_annual","analyst_estimate_gross_profit_margin_mean_annual","analyst_estimate_net_income_high_annual","analyst_estimate_net_income_mean_annual","analyst_estimate_revenue_high_annual","analyst_estimate_revenue_mean_annual","actual_net_income_quarterly","actual_gross_profit_margin_quarterly","actual_revenue_quarterly","actual_earning_per_share_quarterly","actual_net_income_annual","actual_gross_profit_margin_annual","actual_revenue_annual","actual_earning_per_share_annual"])
				newdf = df
				newdf = newdf.drop('target', 1)
				newdf.to_csv(filename, index=False, encoding='utf-8')
				API_ENDPOINT = "http://13.126.153.34:8004/ocpu/user/mahi/library/bnbuyWesPercet/R/buyNOBUYperWiesti/json"
				f =open(filename,'rb')
				files = {'input': f}
				r = requests.post(API_ENDPOINT, files=files)
				if not r.json() is None:
					dt = json_normalize(r.json())
					print(dt.columns.tolist())
					df["ml_result"] =dt["PREDICTED"]
					filename2 = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +"_complete.csv"
					df.to_csv(filename2, index=False, encoding='utf-8')
				
					#for data in r.json():
					#	db.call_procedure("update_indicator_target_data",[data['ticker_id'], 1,data['newdata$PREDICTED'], data['1'],data['0'], data['date'] ])
			except Exception as e:
					#log.Error(e)
					print(e.message)
			finally:
				i=i+1
				f.close()
				
	except Exception as e:
		print(e.message)


def generate_ticker_sell_fundamental_newestimate_details_csv():
	try:
		tickers = call_procedure("get_ticker_details_by_data_type","0")
		i = 0
		directory = os.path.dirname(os.path.realpath(__file__)) + "\\New_fundamental_buy"
		if not os.path.exists(directory):
			os.makedirs(directory)
		while i < len(tickers):
			ticker_sym = tickers[i][1]
			ticker_id = tickers[i][2]
			print("JOB STARTED:" + ticker_sym)
			filename = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +".csv"
			try:
				indicator = call_procedure("get_ticker_future_indicator_value_details_with_target",[ticker_id])
				df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" , "target" , "date" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" , "company_estimate_earning_per_share_mean_quarterly" , "company_estimate_gross_profit_margin_mean_quarterly" , "company_estimate_net_income_mean_quarterly" , "company_estimate_revenue_mean_quarterly" , "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "company_estimate_earning_per_share_mean_annual" , "company_estimate_gross_profit_margin_mean_annual" , "company_estimate_net_income_mean_annual" , "company_estimate_revenue_mean_annual" ])
				newdf = df
				newdf = newdf.drop('target', 1)
				newdf.to_csv(filename, index=False, encoding='utf-8')
				API_ENDPOINT = "http://13.126.153.34:8004/ocpu/user/mahi/library/val/R/valfunda/json"
				f =open(filename,'rb')
				files = {'input': f}
				r = requests.post(API_ENDPOINT, files=files)
				if not r.json() is None:
					dt = json_normalize(r.json())
					print(dt.columns.tolist())
					df["ml_result"] =dt["newdata$PREDICTED"]
					filename2 = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +"_complete.csv"
					df.to_csv(filename2, index=False, encoding='utf-8')
				
					#for data in r.json():
					#	db.call_procedure("update_indicator_target_data",[data['ticker_id'], 1,data['newdata$PREDICTED'], data['1'],data['0'], data['date'] ])
			except Exception as e:
					#log.Error(e)
					print(e)
			finally:
				i=i+1
				f.close()
				
	except Exception as e:
		print(e)


def generate_ticker_future_percent_buy_fundamental_details_new_csv_without_target():
	tickers = call_procedure("get_ticker_details_by_data_type","0")
	i = 0
	df = None
	directory = os.path.dirname(os.path.realpath(__file__)) + "\\percent_buy_fundamental_new"
	if not os.path.exists(directory):
		os.makedirs(directory)
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		indicator = call_procedure("get_ticker_future_indicator_value_details_without_target",[ticker_id])
		df = pd.DataFrame(indicator,columns=["ticker_id", "ticker_name" , "ticker_symbol" ,  "date" , "analyst_estimate_earning_per_share_high_quarterly" , "analyst_estimate_earning_per_share_mean_quarterly" , "analyst_estimate_gross_profit_margin_high_quarterly" , "analyst_estimate_gross_profit_margin_mean_quarterly" , "analyst_estimate_net_income_high_quarterly" , "analyst_estimate_net_income_mean_quarterly" , "analyst_estimate_revenue_high_quarterly" , "analyst_estimate_revenue_mean_quarterly" , "company_estimate_earning_per_share_mean_quarterly" , "company_estimate_gross_profit_margin_mean_quarterly" , "company_estimate_net_income_mean_quarterly" , "company_estimate_revenue_mean_quarterly" , "analyst_estimate_earning_per_share_high_annual" , "analyst_estimate_earning_per_share_mean_annual" , "analyst_estimate_gross_profit_margin_high_annual" , "analyst_estimate_gross_profit_margin_mean_annual" , "analyst_estimate_net_income_high_annual" , "analyst_estimate_net_income_mean_annual" , "analyst_estimate_revenue_high_annual" , "analyst_estimate_revenue_mean_annual" , "company_estimate_earning_per_share_mean_annual" , "company_estimate_gross_profit_margin_mean_annual" , "company_estimate_net_income_mean_annual" , "company_estimate_revenue_mean_annual" ])
		df.to_csv(directory + "\\" + ticker_sym+".csv", index=False, encoding='utf-8')
		i+=1
	return directory

#update_ticker_indicator_prediction()
#generate_ticker__both_combined_details_csv()
#generate_ticker_technical_details_csv()
#predict_short_sell_fund_ticker_indicator()
#predict_buy_ticker_indicator()
#predict_technical_ticker_indicator()
#generate_ticker_future_sell_fundamental_details_csv()
generate_ticker_future_percent_buy_fundamental_details_new_csv_without_target()