import sys
import database as db
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta, time
import math
from dateutil.relativedelta import relativedelta
import error_log as log
import re
import helper
import eikon as ek
import os 
import requests
import threading

def get_data_for_date(start_date,end_date):
	tickers = db.call_procedure("get_ticker_details","")
	i = 0
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		last_date = tickers[i][6]
		if last_date is None:
			last_date = end_date
		else:
			last_date = datetime.datetime.fromordinal(last_date.toordinal())
		print(ticker_sym + " for date " + start_date.strftime("%Y-%m-%d %H:%M:%S") + "-" + end_date.strftime("%Y-%m-%d %H:%M:%S"))
		ticker_id = tickers[i][2]
		print("Job Start Date:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		print("Indicators")
		get_indicator_for_ticker_for_date(start_date,end_date, ticker_id, ticker_sym)
		print("Job End Date:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		i+=1

def perform():
	d1 = datetime.datetime.now()
	d2 = datetime.datetime((d1 - relativedelta(years=20)).year, 1, 1)
	get_data_for_date(d2, d1)

def get_indicator_for_ticker_for_date(start_date, end_date, ticker_id, ticker_symbol):
	try:
		indicator = db.call_procedure("get_indicator_details",[ticker_id])
		i = 0
		while i < len(indicator):
			try:
				last_date = indicator[i][4]
				indicator_name = indicator[i][0]
				indicator_id = indicator[i][1]
				end_duration = indicator[i][9]
				formula = indicator[i][2]
				period = indicator[i][3]
				if last_date is None:
					last_date = start_date
				else:
					last_date = datetime.datetime.fromordinal(last_date.toordinal())

				if period=="DL":
					daterange = pd.date_range(last_date, end_date, freq='B')
					charlist = []
					for dt in daterange:
						try:
							if dt < datetime.datetime.now():
								formula = indicator[i][8]
							else:
									formula = indicator[i][2]
							print(indicator_name)
							if formula!='':
								indicator_value = CalculateFormula(formula, indicator[i][3], dt, ticker_id, 1, dt.year) 
								#save_ticker_indicator_data(indicator_value, ticker_id, indicator[i][3],  indicator_name, indicator_id, dt._date_repr)
								if indicator_value is not None and math.isnan(float(indicator_value)) == False:
									charlist.append(dt._date_repr + '~' + str(indicator_value) + '~' + str(ticker_id))

						except Exception as e:
							log.Error(e)
					save_ticker_indicator_data_bulk(ticker_id, indicator_id, indicator[i][3], charlist)
				elif period=="FQ":
					if end_duration is not None and end_duration > 0:
							end_date = end_date  + relativedelta(years=(end_duration))
					else:
						end_date = end_date  + relativedelta(years=(1))

					quarter = helper.quarters_range(last_date, end_date)
					x = 0
					for x in range(len(quarter)):
						try:
							period_yr = quarter[x][1]
							period_qtr = quarter[x][0]
							prev_q_start, prev_q_end = get_start_end_date(period_yr, period_qtr, ticker_symbol)
							if prev_q_end < datetime.date.today():
								formula = indicator[i][8]
							else:
									formula = indicator[i][2]

							print(indicator_name)
							if formula!='':
								indicator_value = CalculateFormula(formula, indicator[i][3], prev_q_start, ticker_id, period_qtr, period_yr) 
								save_ticker_indicator_data_multiple(indicator_value, ticker_id, indicator[i][3],  indicator_name, indicator_id, prev_q_start, prev_q_end)
						except Exception as e:
							log.Error(e)
						x+=1
				elif period=="FY":
					if end_duration is not None and end_duration > 0:
						end_date = end_date  + relativedelta(years=end_duration)
					else:
						end_date = end_date  + relativedelta(years=1)
					years = range(last_date.year, end_date.year + 1)
					x = 0
					for x in range(len(years)):
						try:
							period_yr = years[x] 
							prev_q_start, prev_q_end = get_start_end_date(period_yr, 0, ticker_symbol)
							if prev_q_end < datetime.date.today():
								formula = indicator[i][8]
							else:
								formula = indicator[i][2]
							print(indicator_name)
							if formula!='':
								indicator_value = CalculateFormula(formula, indicator[i][3], prev_q_end, ticker_id, 0, period_yr) 
								save_ticker_indicator_data_multiple(indicator_value, ticker_id, indicator[i][3],  indicator_name, indicator_id, prev_q_start, prev_q_end)
						except Exception as e:    
							log.Error(e)
						x+=1

			except Exception as e:
				log.Error(e)

			i+=1
	except Exception as e:
		log.Error(e)

def CalculateFormula(formula, period, date, ticker_id, f_quater, f_year): 
	try:
		params = re.findall(r'@\d{0,5}{#?[\D]?[\D]?[\D]?[\D]?[\D]?[+-]?\d+(?:\.\d+)?}',  formula)
		if params:
			params = set(params)
			for temp in params:
				temp_dt= date
				api_id = int(re.sub("{#?[\D]?[\D]?[\D]?[\D]?[\D]?[+-]?\d+(?:\.\d+)?}", "", temp).replace("@", ""))
				forms = re.sub("}|} ","",re.sub("[\d]+{", "", temp)).replace("@#", "")
				diff = int(re.sub(re.sub("[+-]?\d","",forms),"",forms))
				ind_period = re.sub("[+-]?\d","",forms)
				year = temp_dt.year
				quarter=int(math.ceil(temp_dt.month/3.))
				if ind_period == 'Y' or ind_period == 'IY':
					year = f_year + diff
					period = "FY"
				elif ind_period == 'Q' or ind_period == 'IQ':
					quarter=4 if f_quater==1 else f_quater-1
					year = f_year-1  if f_quater==1 else f_year
					period = "FQ"
				elif ind_period == 'QY':
					quarter=f_quater
					year = f_year - 1
					period = "FQ"
				elif ind_period == 'D' or ind_period == 'ID':
					temp_dt =  temp_dt + timedelta(days=diff)
					period = "DL"
				elif ind_period == 'LD' or ind_period == 'ILD':
					temp_dt =  temp_dt + timedelta(days=diff)
					period = "LDL"
				elif ind_period == 'AVGD' or ind_period == 'AVGID':
					year =  diff if diff>=0 else -diff
					period = "AVG"
				str_date = temp_dt.strftime("%Y-%m-%d")
				if 'I' not in ind_period:
					api_value = db.call_procedure("get_api_values",[ticker_id, period, year, quarter, str_date, api_id])
				else:
					api_value = db.call_procedure("get_indicator_values",[ticker_id, period, year, quarter, str_date, api_id])
				if api_value:
					value = api_value[0][0]
					formula= formula.replace(temp, str(value))
				else:
					formula =formula.replace(temp, str(None))
		return eval(formula)
	except Exception as e:    
		log.Error(e)
		return None

def save_ticker_indicator_data(indicator_value, ticker_id, period_type, indicator_name, indicator_id, for_date):
	stocks = db.call_procedure("insert_update_indicator_data",[ticker_id, indicator_id, period_type, float(indicator_value) if math.isnan(float(indicator_value)) == False else None, for_date])

def save_ticker_indicator_data_multiple(indicator_value, ticker_id, period_type, indicator_name, indicator_id, from_date, to_date):
	stocks = db.call_procedure("insert_update_indicator_data_multiple",[ticker_id, indicator_id, period_type, float(indicator_value) if math.isnan(float(indicator_value)) == False else None, from_date, to_date])

def save_ticker_indicator_data_bulk(ticker_id, indicator_id,period_type, data):
	stocks = db.call_procedure("insert_update_indicator_data_bulk",[ticker_id, indicator_id,period_type,  data])

def get_start_end_date(f_year, f_quarter,ticker_symbol ):
	period_end_dt = datetime.date.today()
	period_start_dt = datetime.date.today()
	try:
		#period = "FY0"
		#current_yr = datetime.datetime.now().year
		#year = current_yr-1 if (f_year>(current_yr-1)) else f_year
		#yr_dif = f_year - year
		#if f_quarter>0:
		#	period = str(f_quarter) + "FQ" + str(year)
		#else:
		#	period = "FY" + str(year)
		#ek.set_app_id('93D5C93060C3ECEAD451638')
		#df = ek.get_data(instruments=[ticker_symbol], fields=['TR.SMPeriodEndDate'],parameters={'Period': period},debug=True)
		#end_dt = datetime.datetime.strptime(df[0]["Period End Date"][0], '%Y-%m-%dT%H:%M:%SZ')
		#period_end_dt = datetime.date( end_dt.year + yr_dif, end_dt.month, end_dt.day)
		#if f_quarter>0:
		#	dt = period_end_dt + relativedelta(months=-2, days=0)
		#	period_start_dt = datetime.date(dt.year,dt.month, 1)
		#else:
		#	dt = period_end_dt + relativedelta(years=-1, months=1)
		#	period_start_dt = datetime.date(dt.year,dt.month, 1)
		fy = db.call_procedure("get_ticker_fy_dates",[ticker_id, f_year, f_quarter])
		if fy is not None:
			period_start_dt = fy[0][1]
			period_end_dt = tickers[0][2]
	except Exception as e: 
		if f_quarter>0:
			period_start_dt, period_end_dt =helper.quarter_start_end(f_quarter, f_year)
		else:
			period_start_dt, period_end_dt =helper.year_start_end(f_year)
	return period_start_dt, period_end_dt

def calculate_bulk_ticker_fundamentals_details():
	tickers = db.call_procedure("get_ticker_details_by_data_type","4")
	i = 0
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		try:
			print(ticker_sym + " - " + str(ticker_id) + "START")
			log.Error(ticker_sym + " - " + str(ticker_id) + "START")
			indicator = db.call_procedure("insert_update_indicator_actual_date",[ticker_id])
			log.Error(ticker_sym + " - " + str(ticker_id) + "COMPLETE")
			print(ticker_sym + " - " + str(ticker_id) + "COMPLETE")
			if i%100==0:
				rtn = db.vaccum("ticker_indicator_value")
				log.Error(ticker_sym + " - " + str(ticker_id) + "VACCUM COMPLETE")
				print(ticker_sym + " - " + str(ticker_id) + "VACCUM  COMPLETE")
		except Exception as e:
			print(ticker_sym + " - " + str(ticker_id) + "Error")
			log.Error(e)
		i+=1

		
def calculate_bulk_ticker_fundamentals_actual_values_details():
	tickers = db.call_procedure("get_ticker_details_by_data_type","4")
	i = 0
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		try:
			print(ticker_sym + " - " + str(ticker_id) + "START")
			log.Error(ticker_sym + " - " + str(ticker_id) + "START")
			indicator = db.call_procedure("insert_update_indicator_actual_value_data",[ticker_id])
			log.Error(ticker_sym + " - " + str(ticker_id) + "COMPLETE")
			print(ticker_sym + " - " + str(ticker_id) + "COMPLETE")
			if i>499 and i%500==0:
				rtn = db.vaccum("ticker_indicator_value")
				log.Error(ticker_sym + " - " + str(ticker_id) + "VACCUM COMPLETE")
				print(ticker_sym + " - " + str(ticker_id) + "VACCUM  COMPLETE")
			
			
		except Exception as e:
			print(ticker_sym + " - " + str(ticker_id) + "Error")
			log.Error(e)
		i+=1

def calculate_bulk_ticker_technical_details():
	tickers = db.call_procedure("get_ticker_details_by_data_type","4")
	i = 0
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		ticker_id = tickers[i][2]
		try:
			print(ticker_sym + " - " + str(ticker_id) + "START")
			log.Error(ticker_sym + " - " + str(ticker_id) + "START")
			indicator = db.call_procedure("insert_update_indicator_technical_actual_date",[ticker_id])
			log.Error(ticker_sym + " - " + str(ticker_id) + "COMPLETE")
			print(ticker_sym + " - " + str(ticker_id) + "COMPLETE")
		except Exception as e:
			print(ticker_sym + " - " + str(ticker_id) + "Error")
			log.Error(e)
		i+=1

def predict_short_sell_fund_ticker_indicator():
	try:
		tickers = db.call_procedure("get_ticker_details_by_data_type","0")
		i = 0
		directory = os.path.dirname(os.path.realpath(__file__)) + "\\sell_fundamental_api"
		if not os.path.exists(directory):
			os.makedirs(directory)
		while i < len(tickers):
			ticker_sym = tickers[i][1]
			ticker_id = tickers[i][2]
			log.Error("FUND SHORT/SELL STARTED:" + ticker_sym)
			filename = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +".csv"
			try:
				indicator = db.call_procedure("get_ticker_fundamental_without_target_value_details",[ticker_id])
				df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name',	'ticker_symbol',	'date',	'analyst_estimate_earning_per_share_high_annual_value',	'analyst_estimate_earning_per_share_high_quarterly_value',	'analyst_estimate_earning_per_share_low_annual_value',	'analyst_estimate_earning_per_share_low_quarterly_value',	'analyst_estimate_earning_per_share_mean_annual_value',	'analyst_estimate_earning_per_share_mean_quarterly_value',	'analyst_estimate_gross_profit_margin_high_annual_value',	'analyst_estimate_gross_profit_margin_high_quarterly_value',	'analyst_estimate_gross_profit_margin_low_annual_value',	'analyst_estimate_gross_profit_margin_low_quarterly_value',	'analyst_estimate_gross_profit_margin_mean_annual_value',	'analyst_estimate_gross_profit_margin_mean_quarterly_value',	'analyst_estimate_net_income_high_annual_value',	'analyst_estimate_net_income_high_quarterly_value',	'analyst_estimate_net_income_low_annual_value',	'analyst_estimate_net_income_low_quarterly_value',	'analyst_estimate_net_income_mean_annual_value',	'analyst_estimate_net_income_mean_quarterly_value',	'analyst_estimate_revenue_high_annual_value',	'analyst_estimate_revenue_high_quarterly_value', 'analyst_estimate_revenue_low_annual_value',	'analyst_estimate_revenue_low_quarterly_value',	'analyst_estimate_revenue_mean_annual_value',	'analyst_estimate_revenue_mean_quarterly_value',	'company_estimate_earning_per_share_mean_annual_value',	'company_estimate_earning_per_share_mean_quarterly_value',	'company_estimate_net_income_mean_annual_value',	'company_estimate_net_income_mean_quarterly_value',	'company_estimate_revenue_mean_annual_value',	'company_estimate_revenue_mean_quarterly_value',	'company_estimate_gross_profit_margin_mean_annual_value',	'company_estimate_gross_profit_margin_mean_quarterly_value',	'earning_per_share_annual_value',	'earning_per_share_quarterly_value',	'net_income_annual_value',	'net_income_quarterly_value',	'gross_profit_margin_annual_value',	'gross_profit_margin_quarterly_value',	'revenue_annual_value',	'revenue_quarterly_value',	'analyst_estimate_earning_per_share_high_annual',	'analyst_estimate_earning_per_share_high_quarterly',	'analyst_estimate_earning_per_share_low_annual',	'analyst_estimate_earning_per_share_low_quarterly',	'analyst_estimate_earning_per_share_mean_annual',	'analyst_estimate_earning_per_share_mean_quarterly',	'analyst_estimate_gross_profit_margin_high_annual',	'analyst_estimate_gross_profit_margin_high_quarterly',	'analyst_estimate_gross_profit_margin_low_annual',	'analyst_estimate_gross_profit_margin_low_quarterly',	'analyst_estimate_gross_profit_margin_mean_annual',	'analyst_estimate_gross_profit_margin_mean_quarterly',	'analyst_estimate_net_income_high_annual', 'analyst_estimate_net_income_high_quarterly',	'analyst_estimate_net_income_low_annual',	'analyst_estimate_net_income_low_quarterly',	'analyst_estimate_net_income_mean_annual',	'analyst_estimate_net_income_mean_quarterly',	'analyst_estimate_revenue_high_annual',	'analyst_estimate_revenue_high_quarterly',	'analyst_estimate_revenue_low_annual',	'analyst_estimate_revenue_low_quarterly',	'analyst_estimate_revenue_mean_annual',	'analyst_estimate_revenue_mean_quarterly',	'company_estimate_earning_per_share_mean_annual',	'company_estimate_earning_per_share_mean_quarterly',	'company_estimate_net_income_mean_annual',	'company_estimate_net_income_mean_quarterly',	'company_estimate_revenue_mean_annual',	'company_estimate_revenue_mean_quarterly',	'company_estimate_gross_profit_margin_mean_annual',	'company_estimate_gross_profit_margin_mean_quarterly',	'earning_per_share_annual',	'earning_per_share_quarterly',	'net_income_annual',	'net_income_quarterly',	'non_gaap_gross_margin_annual',	'non_gaap_gross_margin_quarterly',	'revenue_annual',	'revenue_quarterly',	'analyst_estimate_earning_per_share_high_annual_acc_dcc',	'analyst_estimate_earning_per_share_high_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_low_annual_acc_dcc',	'analyst_estimate_earning_per_share_low_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_mean_annual_acc_dcc',	'analyst_estimate_earning_per_share_mean_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_high_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_high_quarterly_acc_dcc', 'analyst_estimate_gross_profit_margin_low_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_low_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'analyst_estimate_net_income_high_annual_acc_dcc',	'analyst_estimate_net_income_high_quarterly_acc_dcc',	'analyst_estimate_net_income_low_annual_acc_dcc',	'analyst_estimate_net_income_low_quarterly_acc_dcc',	'analyst_estimate_net_income_mean_annual_acc_dcc',	'analyst_estimate_net_income_mean_quarterly_acc_dcc',	'analyst_estimate_revenue_high_annual_acc_dcc',	'analyst_estimate_revenue_high_quarterly_acc_dcc',	'analyst_estimate_revenue_low_annual_acc_dcc',	'analyst_estimate_revenue_low_quarterly_acc_dcc',	'analyst_estimate_revenue_mean_annual_acc_dcc',	'analyst_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_earning_per_share_mean_annual_acc_dcc',	'company_estimate_earning_per_share_mean_quarterly_acc_dcc',	'company_estimate_net_income_mean_annual_acc_dcc',	'company_estimate_net_income_mean_quarterly_acc_dcc',	'company_estimate_revenue_mean_annual_acc_dcc',	'company_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_gross_profit_margin_mean_annual_acc_dcc',	'company_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'earning_per_share_annual_acc_dcc',	'earning_per_share_quarterly_acc_dcc',	'net_income_annual_acc_dcc',	'net_income_quarterly_acc_dcc',	'non_gaap_gross_margin_annual_acc_dcc',	'non_gaap_gross_margin_quarterly_acc_dcc',	'revenue_annual_acc_dcc', 'revenue_quarterly_acc_dcc'])

				df.to_csv(filename, index=False, encoding='utf-8')
				API_ENDPOINT = "http://13.126.153.34:8004/ocpu/user/mahi/library/qa/R/short/json"
				f =open(filename,'rb')
				files = {'input': f}
				r = requests.post(API_ENDPOINT, files=files)
				if not r.json() is None:
					for data in r.json():
						db.call_procedure("update_indicator_target_data",[data['ticker_id'], 2,data['newdata$PREDICTED'], data['1'],data['0'], data['date'] ])
			except Exception as e:
				log.Error(e)
			finally:
				i=i+1
				log.Error("FUND SHORT/SELL COMPLETED:" + ticker_sym)
				f.close()
				try:
					os.remove(filename)
				except Exception as e:
					log.Error(e)
	except Exception as e:
		log.Error(e)

def predict_buy_ticker_indicator():
	try:
		tickers = db.call_procedure("get_ticker_details_by_data_type","0")
		i = 0
		directory = os.path.dirname(os.path.realpath(__file__)) + "\\buy_fundamental_api"
		if not os.path.exists(directory):
			os.makedirs(directory)
		while i < len(tickers):
			ticker_sym = tickers[i][1]
			ticker_id = tickers[i][2]
			log.Error("FUND BUY STARTED:" + ticker_sym)
			filename = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +".csv"
			filename2 = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +"_linear.csv"
			filename3 = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +"_time.csv"
			try:
				indicator = db.call_procedure("get_ticker_fundamental_without_target_value_details",[ticker_id])
				df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name',	'ticker_symbol',	'date',	'analyst_estimate_earning_per_share_high_annual_value',	'analyst_estimate_earning_per_share_high_quarterly_value',	'analyst_estimate_earning_per_share_low_annual_value',	'analyst_estimate_earning_per_share_low_quarterly_value',	'analyst_estimate_earning_per_share_mean_annual_value',	'analyst_estimate_earning_per_share_mean_quarterly_value',	'analyst_estimate_gross_profit_margin_high_annual_value',	'analyst_estimate_gross_profit_margin_high_quarterly_value',	'analyst_estimate_gross_profit_margin_low_annual_value',	'analyst_estimate_gross_profit_margin_low_quarterly_value',	'analyst_estimate_gross_profit_margin_mean_annual_value',	'analyst_estimate_gross_profit_margin_mean_quarterly_value',	'analyst_estimate_net_income_high_annual_value',	'analyst_estimate_net_income_high_quarterly_value',	'analyst_estimate_net_income_low_annual_value',	'analyst_estimate_net_income_low_quarterly_value',	'analyst_estimate_net_income_mean_annual_value',	'analyst_estimate_net_income_mean_quarterly_value',	'analyst_estimate_revenue_high_annual_value',	'analyst_estimate_revenue_high_quarterly_value', 'analyst_estimate_revenue_low_annual_value',	'analyst_estimate_revenue_low_quarterly_value',	'analyst_estimate_revenue_mean_annual_value',	'analyst_estimate_revenue_mean_quarterly_value',	'company_estimate_earning_per_share_mean_annual_value',	'company_estimate_earning_per_share_mean_quarterly_value',	'company_estimate_net_income_mean_annual_value',	'company_estimate_net_income_mean_quarterly_value',	'company_estimate_revenue_mean_annual_value',	'company_estimate_revenue_mean_quarterly_value',	'company_estimate_gross_profit_margin_mean_annual_value',	'company_estimate_gross_profit_margin_mean_quarterly_value',	'earning_per_share_annual_value',	'earning_per_share_quarterly_value',	'net_income_annual_value',	'net_income_quarterly_value',	'gross_profit_margin_annual_value',	'gross_profit_margin_quarterly_value',	'revenue_annual_value',	'revenue_quarterly_value',	'analyst_estimate_earning_per_share_high_annual',	'analyst_estimate_earning_per_share_high_quarterly',	'analyst_estimate_earning_per_share_low_annual',	'analyst_estimate_earning_per_share_low_quarterly',	'analyst_estimate_earning_per_share_mean_annual',	'analyst_estimate_earning_per_share_mean_quarterly',	'analyst_estimate_gross_profit_margin_high_annual',	'analyst_estimate_gross_profit_margin_high_quarterly',	'analyst_estimate_gross_profit_margin_low_annual',	'analyst_estimate_gross_profit_margin_low_quarterly',	'analyst_estimate_gross_profit_margin_mean_annual',	'analyst_estimate_gross_profit_margin_mean_quarterly',	'analyst_estimate_net_income_high_annual', 'analyst_estimate_net_income_high_quarterly',	'analyst_estimate_net_income_low_annual',	'analyst_estimate_net_income_low_quarterly',	'analyst_estimate_net_income_mean_annual',	'analyst_estimate_net_income_mean_quarterly',	'analyst_estimate_revenue_high_annual',	'analyst_estimate_revenue_high_quarterly',	'analyst_estimate_revenue_low_annual',	'analyst_estimate_revenue_low_quarterly',	'analyst_estimate_revenue_mean_annual',	'analyst_estimate_revenue_mean_quarterly',	'company_estimate_earning_per_share_mean_annual',	'company_estimate_earning_per_share_mean_quarterly',	'company_estimate_net_income_mean_annual',	'company_estimate_net_income_mean_quarterly',	'company_estimate_revenue_mean_annual',	'company_estimate_revenue_mean_quarterly',	'company_estimate_gross_profit_margin_mean_annual',	'company_estimate_gross_profit_margin_mean_quarterly',	'earning_per_share_annual',	'earning_per_share_quarterly',	'net_income_annual',	'net_income_quarterly',	'non_gaap_gross_margin_annual',	'non_gaap_gross_margin_quarterly',	'revenue_annual',	'revenue_quarterly',	'analyst_estimate_earning_per_share_high_annual_acc_dcc',	'analyst_estimate_earning_per_share_high_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_low_annual_acc_dcc',	'analyst_estimate_earning_per_share_low_quarterly_acc_dcc',	'analyst_estimate_earning_per_share_mean_annual_acc_dcc',	'analyst_estimate_earning_per_share_mean_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_high_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_high_quarterly_acc_dcc', 'analyst_estimate_gross_profit_margin_low_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_low_quarterly_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_annual_acc_dcc',	'analyst_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'analyst_estimate_net_income_high_annual_acc_dcc',	'analyst_estimate_net_income_high_quarterly_acc_dcc',	'analyst_estimate_net_income_low_annual_acc_dcc',	'analyst_estimate_net_income_low_quarterly_acc_dcc',	'analyst_estimate_net_income_mean_annual_acc_dcc',	'analyst_estimate_net_income_mean_quarterly_acc_dcc',	'analyst_estimate_revenue_high_annual_acc_dcc',	'analyst_estimate_revenue_high_quarterly_acc_dcc',	'analyst_estimate_revenue_low_annual_acc_dcc',	'analyst_estimate_revenue_low_quarterly_acc_dcc',	'analyst_estimate_revenue_mean_annual_acc_dcc',	'analyst_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_earning_per_share_mean_annual_acc_dcc',	'company_estimate_earning_per_share_mean_quarterly_acc_dcc',	'company_estimate_net_income_mean_annual_acc_dcc',	'company_estimate_net_income_mean_quarterly_acc_dcc',	'company_estimate_revenue_mean_annual_acc_dcc',	'company_estimate_revenue_mean_quarterly_acc_dcc',	'company_estimate_gross_profit_margin_mean_annual_acc_dcc',	'company_estimate_gross_profit_margin_mean_quarterly_acc_dcc',	'earning_per_share_annual_acc_dcc',	'earning_per_share_quarterly_acc_dcc',	'net_income_annual_acc_dcc',	'net_income_quarterly_acc_dcc',	'non_gaap_gross_margin_annual_acc_dcc',	'non_gaap_gross_margin_quarterly_acc_dcc',	'revenue_annual_acc_dcc', 'revenue_quarterly_acc_dcc'])
				df.to_csv(filename, index=False, encoding='utf-8')
				dt = df.interpolate(method='linear', axis=0, limit=None, inplace=False, downcast=None)
				dt.to_csv(filename2, index=False, encoding='utf-8')
				dt2 = pd.to_datetime(df['date']).set_index('date', inplace=False)
				dt2.interpolate(method='time', axis=0, limit=None, inplace=False, downcast=None)
				dt2.to_csv(filename3, index=False, encoding='utf-8')
				#API_ENDPOINT = "http://13.126.153.34:8004/ocpu/user/mahi/library/qa/R/fund/json"
				#f =open(filename,'rb')
				#files = {'input': f}
				#r = requests.post(API_ENDPOINT, files=files)
				#if not r.json() is None:
				#	print r.json()
				#	for data in r.json():
				#		db.call_procedure("update_indicator_target_data",[data['ticker_id'], 0,data['newdata$PREDICTED'], data['1'],data['0'], data['date'] ])
			except Exception as e:
					#print(e + "Error")
					log.Error(e)
			finally:
				i=i+1
				f.close()
				log.Error("FUND BUY COMPLETED:" + ticker_sym)
				#try:
				#	os.remove(filename)
				#except Exception as e:
				#	log.Error(e)
	except Exception as e:
		log.Error(e)
		#print(e + "Error")

def predict_technical_ticker_indicator():
	try:
		tickers = db.call_procedure("get_ticker_details_by_data_type","0")
		i = 0
		directory = os.path.dirname(os.path.realpath(__file__)) + "\\technical_api"
		if not os.path.exists(directory):
			os.makedirs(directory)
		while i < len(tickers):
			ticker_sym = tickers[i][1]
			ticker_id = tickers[i][2]
			log.Error("TECH STARTED:" + ticker_sym)
			filename = directory + "\\" + ticker_sym+ 	datetime.datetime.now().strftime('%Y%m%d%H%M%S') +".csv"
			try:
				indicator = db.call_procedure("get_ticker_technical_indicator_value_details_without_target",[ticker_id])
				df = pd.DataFrame(indicator,columns=['ticker_id',	'ticker_name','ticker_symbol',	'date',	'14_day_close_price_sma',	'14_day_close_price_high',	'14_day_close_price_low',	'14_day_50_day_sma',	'14_day_100_day_sma',	'14_day_200_day_sma'])
				df.to_csv(filename, index=False, encoding='utf-8')
				API_ENDPOINT = "http://13.126.153.34:8004/ocpu/user/mahi/library/qa/R/tech/json"
				f =open(filename,'rb')
				files = {'input': f}
				r = requests.post(API_ENDPOINT, files=files)
				if not r.json() is None:
					for data in r.json():
						db.call_procedure("update_indicator_target_data",[data['ticker_id'], 1,data['newdata$PREDICTED'], data['1'],data['0'], data['date'] ])
			except Exception as e:
					log.Error(e)
			finally:
				i=i+1
				f.close()
				try:
					os.remove(filename)					
					log.Error("TECH COMPLETED:" + ticker_sym)
				except Exception as e:
					log.Error(e)
	except Exception as e:
			log.Error(e)
			#print(e + "Error")

#calculate_bulk_ticker_fundamentals_actual_values_details()
#calculate_bulk_ticker_fundamentals_details()
#calculate_bulk_ticker_technical_details()
#perform()
predict_buy_ticker_indicator()
#predict_technical_ticker_indicator()
#predict_short_sell_fund_ticker_indicator()
#t = threading.Thread(target=predict_short_sell_fund_ticker_indicator)
#t.start()

#t = threading.Thread(target=predict_buy_ticker_indicator)
#t.start()

#t = threading.Thread(target=predict_technical_ticker_indicator)
#t.start()