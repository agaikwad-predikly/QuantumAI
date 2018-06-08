import database as db
import eikon as ek
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import math
from dateutil.relativedelta import relativedelta
import error_log as log
import re
import helper
import os
import time
import failed_log as fl
import mail_helper as mailservice


	
try:
	"""Eikon App ID
	"""
	
	ek.set_app_id('93D5C93060C3ECEAD451638')
	
except ek.EikonError as e:
	if(e.code == '401'):
		StartEikon()
	else:
		log.Error(e)
					 

"""
    Function to get ticker data for date. Here we get all tickers from Database and 
    and the data is got for individual tickers from the end for which the last job stopped for the ticker 
    till todays date
"""
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
		print("API")
		if get_indicator_for_ticker_for_date(start_date,end_date, ticker_id, ticker_sym) == False:
			return False
		print("Job End Date:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		i+=1

""" Start up function of the api service
"""
def perform():	
	d1 = datetime.datetime.now()
	d2 = (datetime.datetime((d1 - relativedelta(years=20)).year, 1, 1))
	get_data_for_date(d2, d1)

def perform_eod_for_date(start_date,end_date, ticker_id, ticker_sym):
	if (relativedelta(end_date, start_date).years > 10):
		dt_dif = divmod(relativedelta(end_date, start_date).years, 10)
		loopcnt = 0
		if dt_dif[1] == 0:
			loopcnt = divmod(relativedelta(end_date, start_date).years, 10)[0]
		else:
			loopcnt = divmod(relativedelta(end_date, start_date).years, 10)[0] + 1

		for x in range(loopcnt):
			new_end_date = start_date + relativedelta(years=(10))
			if new_end_date > end_date:
				new_end_date = end_date
			get_eod_for_ticker_for_date(start_date,new_end_date, ticker_id, ticker_sym)
			start_date = new_end_date
			if new_end_date < end_date:            
			        get_eod_for_ticker_for_date(start_date,new_end_date, ticker_id, ticker_sym)
	else:
		get_eod_for_ticker_for_date(start_date,end_date, ticker_id, ticker_sym)

def get_eod_for_ticker_for_date(start_date, end_date, ticker_id, ticker_symbol):
	try:
		df = ek.get_timeseries(ticker_symbol, fields='*', start_date=start_date,  end_date=end_date, interval='daily', count=None, calendar=None, corax=None, normalize=False, raw_output=False, debug=False)
		save_ticker_data(df, ticker_id)
	except Exception as e:    
		log.Error(e)

def get_indicator_for_ticker_for_date(start_date, p_end_date, ticker_id, ticker_symbol):
	try:
		indicator = db.call_procedure("get_api_details",[ticker_id])
		eikon_proxy_failure_count=0
		start_date=datetime.datetime.today()
		fy_indicators, fq_indicators = [],[]
		i = 0
		result = False
		total_count= len(indicator)
		success_count = 0
		failed_count = 0
		while i < len(indicator):
			try:
				last_date = indicator[i][7]
				end_duration = indicator[i][8]
				indicator_name = indicator[i][0]
				indicator_id = indicator[i][1]
				end_date= p_end_date
				if last_date is None:
					last_date = start_date
				else:
					last_date = datetime.datetime.fromordinal(last_date.toordinal())
				if indicator[i][3] == 'FQ':
					period_year=0
					period_quarter=0
					try:
						period = "FQ0"
						quarter = helper.quarters_range(last_date, end_date)
						edate = len(quarter)
						if end_duration is not None and end_duration > 0:
							period = "FQ" + str(end_duration*4)
							edate = (edate + (end_duration*4))

						params = {'Period': period, "FRQ":"FQ","SDate":"0"}
						params['EDate'] = edate * -1
						if indicator[i][5] > 0:
							params['Scale'] = indicator[i][5]
						if indicator[i][6] is not None and indicator[i][6] != 'NULL':
							params['Curn'] = indicator[i][6]

						df = ek.get_data(instruments=[ticker_symbol], fields=[indicator[i][2], indicator[i][2] + ".periodenddate",indicator[i][2] + ".fperiod"],parameters=params,debug=True)
						dt = pd.DataFrame(df[0], index=None)
						
						df2 = pd.DataFrame(dt[dt.columns[0:]].apply(lambda x: '~'.join(x.dropna().astype(str).astype(str)),axis=1), index=None, columns=['data'])
						save_ticker_api_bulk_data(df2['data'].tolist(), ticker_id, 'FQ', indicator_id)
						result = True
						success_count +=1
						#if not dt.empty:
						#	dt = dt.sort_values(by=['Period End Date'])
						#	for index, row in dt.iterrows():
						#		indicator_value = row[indicator_name]
						#		data_date = row['Period End Date']
						#		if data_date!='':
						#			period_yr = datetime.datetime.strptime(data_date, '%Y-%m-%d').year
						#			period_qtr = math.ceil(datetime.datetime.strptime(data_date, '%Y-%m-%d').month/3.)
						#			fperiod = row["Financial Period Absolute"]
						#			if pd.isnull(fperiod) == False:
						#				period_yr = re.sub("FY","",re.sub("Q\d","",fperiod))
						#				period_qtr = re.sub("Q","",re.sub("FY\d{0,5}","",fperiod))
						#			if pd.isnull(data_date) == False:
						#				save_ticker_api_data(indicator_value, ticker_id, period_yr, period_qtr, 'FQ', indicator_name, indicator_id, data_date)
					except ek.EikonError as e:
						if(e.code == '401'):
							StartEikon()
							i = i -1
						else:
							log.Error(e)
							failed_count +=1
						fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], last_date.year, 0,last_date, 1, 0, datetime.date.today(), start_date, datetime.date.today(),e.message)

					except Exception as e:
						if(hasattr(e, 'message') and  e.message == "Invalid URL 'None': No schema supplied. Perhaps you meant http://None?"):
							StartEikon()
							i = i -1
						log.Error(e)
						failed_count+=1
						fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], last_date.year, 0,last_date, 1, 0, datetime.date.today(), start_date, datetime.date.today(),e.message)

					
					
				elif indicator[i][3] == 'DL':
					if end_duration is not None and end_duration > 0:
						end_date = end_date + timedelta(days=end_duration)
					delta = end_date - last_date
					step = 1345
					if(delta.days + 1 < step):
						step = delta.days + 1
					for j in range(delta.days + 1, -1, -step):
						period_yrs=0
						period_days=last_date
						try:
							period_days = last_date + timedelta(days=j)
							period_yrs = period_days.year
							params = {'Frq': 'D'}
							if j == 0:
								params['EDate'] = j
								params['SDate'] = j
							else:
								params['EDate'] = -j
								params['SDate'] = -j + step
								if (-j + step) > 0:
									params['SDate'] =0
							fields = [indicator[i][2],indicator[i][2] + ".Date"]
							if indicator[i][6] is not None and indicator[i][6] != 'NULL':
								params['Curn'] = indicator[i][6]
							df = ek.get_data(ticker_symbol, fields, params, debug=True)
							dt = pd.DataFrame(df[0], index=None)
							dt = dt.drop_duplicates(subset=['Date'], keep=False)
							df2 = pd.DataFrame(dt[dt.columns[0:]].apply(lambda x: '~'.join(x.dropna().astype(str).astype(str)),axis=1), index=None, columns=['data'])
							save_ticker_api_bulk_data(df2['data'].tolist(), ticker_id, 'DL', indicator_id)
							result = True
							success_count+=1
							#if not dt.empty:
							#	dt = dt.sort_values(by=['Date'])
							#	for index, row in dt.iterrows():
							#		indicator_value = row[indicator_name]
							#		data_date = row['Date']
							#		if pd.isnull(data_date) == False:
							#			save_ticker_api_data(indicator_value, ticker_id, period_yrs, 0, 'DL',  indicator_name, indicator_id,data_date)
						except ek.EikonError as e:
							if(e.code == '401'):
								StartEikon()
								i = i -1
							else:
								log.Error(e)
								failed_count +=1
							fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], period_yrs, 0,period_days, 1, 0, datetime.datetime.today(), start_date, datetime.datetime.now(),e.message)
						except Exception as e:
							if(hasattr(e, 'message') and  e.message == "Invalid URL 'None': No schema supplied. Perhaps you meant http://None?"):
								StartEikon()
								i = i -1
							log.Error(e)
							failed_count+=1
							fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], period_yrs, 0,period_days, 1, 0, datetime.datetime.today(), start_date, datetime.datetime.now(),e.message)

				elif indicator[i][3] == 'FY':
					try:
						period = "FY0"
						edate = len(range(last_date.year, end_date.year + 1))
						if end_duration is not None and end_duration > 0:
							period = "FY" + str(end_duration)
							edate = edate + end_duration
						params = {'Period': period, "FRQ":"FY","SDate":"0"}
						params['EDate']		= edate  * -1
						if indicator[i][5] > 0:
							params['Scale'] = indicator[i][5]
						if indicator[i][6] is not None and indicator[i][6] != 'NULL':
							params['Curn'] = indicator[i][6]
						df = ek.get_data(instruments=[ticker_symbol], fields=[indicator[i][2], indicator[i][2] + ".periodenddate",indicator[i][2] + ".fperiod"],parameters=params,debug=True)
						dt = pd.DataFrame(df[0], index=None)
						df2 = pd.DataFrame(dt[dt.columns[0:]].apply(lambda x: '~'.join(x.dropna().astype(str).astype(str)),axis=1), index=None, columns=['data'])
						save_ticker_api_bulk_data(df2['data'].tolist(), ticker_id, 'FY', indicator_id)
						result = True
						success_count+=1
                        #print(myarray)
                        #dt = pd.DataFrame(df[0])
						#dt.columns=['ticker_symbol', 'indicator_value', 'data_date', 'period']
						#print(df2)
						#if not dt.empty:
						#	dt = dt.sort_values(by=['Period End Date'])
						#	for index, row in dt.iterrows():
						#		indicator_value = row[indicator_name]
						#		data_date = row['Period End Date']
						#		if pd.isnull(data_date) == False and data_date!='':
						#			period_yr = datetime.datetime.strptime(data_date, '%Y-%m-%d').year
						#			period_qtr = 0
						#			fperiod = row["Financial Period Absolute"]
						#			if pd.isnull(fperiod) == False:
						#				period_yr = re.sub("FY","",fperiod)
						#			if pd.isnull(data_date) == False:
						#				save_ticker_api_data(indicator_value, ticker_id, period_yr, period_qtr, 'FY', indicator_name, indicator_id, data_date)
					except ek.EikonError as e:
						if(e.code == '401'):
							StartEikon()
							i = i -1
						else:
							log.Error(e)
							failed_count +=1
						fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3],last_date.year, 0,last_date, 1, 0, datetime.datetime.today(), start_date, datetime.datetime.now(),e.message)

					except Exception as e:
						if(hasattr(e, 'message') and  e.message == "Invalid URL 'None': No schema supplied. Perhaps you meant http://None?"):
							StartEikon()
							i = i -1
						log.Error(e)
						failed_count+=1
						fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3],last_date.year, 0,last_date, 1, 0, datetime.datetime.today(), start_date, datetime.datetime.now(),e.message)

				elif indicator[i][3] == 'EX':
					exchange = db.call_procedure("get_exchange_ticker_details",[ticker_id])	
					k = 0
					while k < len(exchange):
						try:
							df = ek.get_data(exchange[k][0], indicator[i][2],debug=True)
							indicator_value = df[0][indicator_name][0]
							save_ticker_api_data(indicator_value, exchange[k][2], 0, 0, indicator[i][3],  indicator_name, indicator_id, datetime.date.today())
							result = True
							success_count+=1
						except ek.EikonError as e:
							if(e.code == '401'):
								if StartEikon()==False:
									return False
								else:
									i = i -1
							else:
								log.Error(e)
								failed_count +=1
							fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], 0, 0,0, 1, retry_count, datetime.datetime.today(), start_date,  datetime.datetime.today(),e.message)
						except Exception as e:
							if(hasattr(e, 'message') and  e.message == "Invalid URL 'None': No schema supplied. Perhaps you meant http://None?"):
								StartEikon()
								i = i -1
							log.Error(e)
							failed_count+=1
							fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], 0, 0,0, 1, retry_count, datetime.datetime.today(), start_date,  datetime.datetime.today(),e.message)

						k+=1
				else:
					try:
						df = ek.get_data(instruments=[ticker_symbol], fields=[indicator[i][2], indicator[i][2] + ".date"],debug=True)
						indicator_value = df[0][indicator_name][0]
						data_date = datetime.date.today()
						try:
							data_date = df[0]['Date'][0]
						except Exception as e:    
							log.Error(e)
						save_ticker_api_data(indicator_value, ticker_id, 0, 0, indicator[i][3],  indicator_name, indicator_id, data_date)
						result= True
						success_count+=1
					except ek.EikonError as e:
						if(e.code == '401'):
							StartEikon()
							i = i -1
						else:
							log.Error(e)
							failed_count +=1
						fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], 0, 0,0, 1, retry_count, datetime.datetime.today(), start_date,  datetime.datetime.today(),e.message)

					except Exception as e:
						if(hasattr(e, 'message') and  e.message == "Invalid URL 'None': No schema supplied. Perhaps you meant http://None?"):
							StartEikon()
							i = i -1
						log.Error(e)
						failed_count+=1
						fl.save_error_log_details(0, 1, ticker_id, indicator_id,indicator[i][3], 0, 0,0, 1, retry_count, datetime.datetime.now().date(), start_date,  datetime.datetime.today(),e.message)

			except Exception as e:
				log.Error(e)
			i+=1
		status=0
		if total_count==success_count:
			status=1
		else :
			status=2
		fl.save_job_status(0,1,ticker_id, status, 0,total_count,success_count,failed_count,datetime.date.today(),start_date,datetime.date.today())

	except Exception as e:
		log.Error(e)
		
def StartEikon():
	global eikon_proxy_failure_count
	if  eikon_proxy_failure_count<3:
		eikon_proxy_failure_count+=1
		os.startfile(os.path.dirname(os.getenv('APPDATA')) + "\\Local\\Eikon API Proxy\\EikonAPIProxy.exe")
		time.sleep(30)
		return True
	else :
		mailservice.send_eikon_failure_mail()
		return False

def save_ticker_data(df, ticker_id):
	dt = pd.DataFrame(df)
	for index, row in dt.iterrows():
		high = float(row['HIGH']) if math.isnan(float(row['HIGH'])) == False else 0
		CLOSE = float(row['CLOSE']) if math.isnan(float(row['CLOSE'])) == False else 0
		LOW = float(row['LOW']) if math.isnan(float(row['LOW'])) == False else 0
		OPEN = float(row['OPEN']) if math.isnan(float(row['OPEN'])) == False else 0
		COUNT = float(row['COUNT']) if math.isnan(float(row['COUNT'])) == False else 0
		VOLUME = float(row['VOLUME']) if math.isnan(float(row['VOLUME'])) == False else 0
		stocks = db.call_procedure("insert_update_eod_data",[ticker_id, row.name, high, CLOSE, LOW, OPEN, COUNT, VOLUME])

def save_ticker_api_data(api_value, ticker_id, period_yr, period_qtr, period_type, api_name, api_id, for_date):
	stocks = db.call_procedure("insert_update_api_data",[ticker_id, api_id, period_type, period_yr, period_qtr, float(api_value) if math.isnan(float(api_value)) == False else None, for_date])

def save_ticker_api_bulk_data(data, ticker_id, period_type, api_id):
	stocks = db.call_procedure("insert_update_api_data_bulk",[ticker_id, api_id, period_type, data])


eikon_proxy_failure_count=0
perform()