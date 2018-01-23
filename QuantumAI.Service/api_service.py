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
"""Eikon App ID
"""
ek.set_app_id('93D5C93060C3ECEAD451638')

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
		print("EOD")
        #perform_eod_for_date(last_date,end_date, ticker_id, ticker_sym)

		print("API")
		get_indicator_for_ticker_for_date(start_date,end_date, ticker_id, ticker_sym)
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
        fy_indicators, fq_indicators = [],[]
        i = 0
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
                        dt = pd.DataFrame(df[0])
                        if not dt.empty:
                            dt = dt.sort_values(by=['Period End Date'])
                            for index, row in dt.iterrows():
                                indicator_value = row[indicator_name]
                                data_date = row['Period End Date']
                                if data_date!='':
                                    period_yr = datetime.datetime.strptime(data_date, '%Y-%m-%d').year
                                    period_qtr = math.ceil(datetime.datetime.strptime(data_date, '%Y-%m-%d').month/3.)
                                    fperiod = row["Financial Period Absolute"]
                                    if pd.isnull(fperiod) == False:
                                        period_yr = re.sub("FY","",re.sub("Q\d","",fperiod))
                                        period_qtr = re.sub("Q","",re.sub("FY\d{0,5}","",fperiod))
                                    if pd.isnull(data_date) == False:
                                        save_ticker_api_data(indicator_value, ticker_id, period_yr, period_qtr, 'FQ', indicator_name, indicator_id, data_date)
                    except Exception as e:    
                        log.Error(e)
                   # x = 0
                    #for x in range(len(quarter)):
                    #    try:
                    #        period_yr = quarter[x][1]
                    #        period_qtr = quarter[x][0]
                    #        period = (str(period_qtr) + 'FQ' + str(period_yr))
                            
                            
                    #        df = ek.get_data(ticker_symbol, {indicator[i][2]:{'params':params}},debug=True)
                    #        indicator_value = df[0][indicator_name][0]
                    #        save_ticker_api_data(indicator_value, ticker_id, period_yr, period_qtr, 'FQ', indicator_name, indicator_id, datetime.date.today())
                    #    except Exception as e:    
                    #        log.Error(e)
                    #    x+=1

                elif indicator[i][3] == 'DL':
                    if end_duration is not None and end_duration > 0:
                        end_date = end_date + timedelta(days=end_duration)
                    delta = end_date - last_date
                    step = 1345
                    if(delta.days + 1 < step):
                        step = delta.days + 1
                    for j in range(delta.days + 1, -1, -step):
                        try:
                            period_days = last_date + timedelta(days=j)
                            #period_enddays = last_date + timedelta(days=j +
                            #(step-1))
                            period_yrs = period_days.year
                            params = {'Frq': 'D'}
                            if j == 0:
                                params['EDate'] = j
                                params['SDate'] = j
                            else:
                                params['EDate'] = -j
                                params['SDate'] = -j + step
                        

                            fields = [indicator[i][2],indicator[i][2] + ".Date"]
                            df = ek.get_data(ticker_symbol, fields, params, debug=True)
                            dt = pd.DataFrame(df[0])
                            if not dt.empty:
                                dt = dt.sort_values(by=['Date'])
                                for index, row in dt.iterrows():
                                    indicator_value = row[indicator_name]
                                    data_date = row['Date']
                                    if pd.isnull(data_date) == False:
                                        save_ticker_api_data(indicator_value, ticker_id, period_yrs, 0, 'DL',  indicator_name, indicator_id,data_date)
                        except Exception as e:    
                            log.Error(e)

                elif indicator[i][3] == 'FY':
                    #if end_duration is not None and end_duration > 0:
                    #    end_date = end_date + timedelta(end_duration*365)
                    #years = range(last_date.year, end_date.year + 1)
                    #x = 0
                    #for x in range(len(years)):
                    #    try:
                    #        period_yr = years[x]
                    #        period = ('FY' + str(period_yr))
                    #        params = {'Period': period}
                    #        if indicator[i][5] > 0:
                    #            params['Scale'] = indicator[i][5]

                    #        if indicator[i][6] is not None and indicator[i][6] != 'NULL':
                    #            params['Curn'] = indicator[i][6]

                    #        df = ek.get_data(ticker_symbol, {indicator[i][2]:{'params':params}},debug=True)
                    #        indicator_value = df[0][indicator_name][0]
                    #        save_ticker_api_data(indicator_value, ticker_id, period_yr, 0, 'FY',  indicator_name, indicator_id, datetime.date.today())
                    #    except Exception as e:    
                    #        log.Error(e)
                    #    x+=1
                    try:
                        period = "FY0"
                        edate = len(range(last_date.year, end_date.year + 1))
                        if end_duration is not None and end_duration > 0:
                            period = "FY" + str(end_duration)
                            edate = edate + end_duration
                    
                        params = {'Period': period, "FRQ":"FY","SDate":"0"}
                        params['EDate'] = edate  * -1
                        if indicator[i][5] > 0:
                            params['Scale'] = indicator[i][5]
                        
                        if indicator[i][6] is not None and indicator[i][6] != 'NULL':
                            params['Curn'] = indicator[i][6]

                        df = ek.get_data(instruments=[ticker_symbol], fields=[indicator[i][2], indicator[i][2] + ".periodenddate",indicator[i][2] + ".fperiod"],parameters=params,debug=True)
                        dt = pd.DataFrame(df[0])
                        if not dt.empty:
                            dt = dt.sort_values(by=['Period End Date'])
                            for index, row in dt.iterrows():
                                indicator_value = row[indicator_name]
                                data_date = row['Period End Date']
                                if pd.isnull(data_date) == False and data_date!='':
                                    period_yr = datetime.datetime.strptime(data_date, '%Y-%m-%d').year
                                    period_qtr = 0
                                    fperiod = row["Financial Period Absolute"]
                                    if pd.isnull(fperiod) == False:
                                        period_yr = re.sub("FY","",fperiod)
                                    if pd.isnull(data_date) == False:
                                        save_ticker_api_data(indicator_value, ticker_id, period_yr, period_qtr, 'FY', indicator_name, indicator_id, data_date)
                    except Exception as e:    
                        log.Error(e)
                elif indicator[i][3] == 'EX':
                    exchange = db.call_procedure("get_exchange_ticker_details",[ticker_id])	
                    k = 0
                    while k < len(exchange):         
                        try:
                            df = ek.get_data(exchange[k][0], indicator[i][2],debug=True)
                            indicator_value = df[0][indicator_name][0]
                            save_ticker_api_data(indicator_value, exchange[k][2], 0, 0, indicator[i][3],  indicator_name, indicator_id, datetime.date.today())
                        except Exception as e:    
                            log.Error(e)

                        k+=1
                #elif indicator[i][3] == 'CLDL':
                #    formula = indicator[i][2]
                #    daterange = pd.date_range(start_date, end_date)
                #    for dt in daterange:
                #        try:
                #            indicator_value = CalculateFormula(formula, 'DL', dt.year, x,0, ticker_id) 
                #            save_ticker_indicator_data(indicator_value, ticker_id, dt.year, 0, 'CLDL',  indicator_name, indicator_id, dt)
                #        except Exception as e:    
                #            log.Error(e)
                #        x+=1
                #elif indicator[i][3] == 'CLFQ':
                #    formula = indicator[i][2]
                #    quarter = quarters_range(last_date, end_date)
                #    x = 0
                #    for x in range(len(quarter)):
                #        try:
                #            period_yr = quarter[x][1]
                #            period_qtr = quarter[x][0]
                #            indicator_value = CalculateFormula(formula, 'FQ', period_yr, None,period_qtr, ticker_id) 
                #            save_ticker_indicator_data(indicator_value, ticker_id, period_yr, period_qtr, 'CLFQ',  indicator_name, indicator_id, datetime.date.today())
                #        except Exception as e:    
                #            log.Error(e)
                #        x+=1
                #elif indicator[i][3] == 'CLFY':
                #    formula = indicator[i][2]
                #    years = range(last_date.year, datetime.datetime.now().year + 1)
                #    x = 0
                #    for x in range(len(years)):
                #        try:
                #            period_yr = years[x]                       
                #            indicator_value = CalculateFormula(formula, 'FY', period_yr, None,0, ticker_id) 
                #            save_ticker_indicator_data(indicator_value, ticker_id, period_yr, 0, 'FY',  indicator_name, indicator_id, datetime.date.today())
                #        except Exception as e:    
                #            log.Error(e)
                #        x+=1
                else:
                    df = ek.get_data(instruments=[ticker_symbol], fields=[indicator[i][2], indicator[i][2] + ".date"],debug=True)
                    indicator_value = df[0][indicator_name][0]
                    data_date = datetime.date.today();
                    try:
                        data_date = df[0]['Date'][0]
                    except Exception as e:    
                        log.Error(e)
                    save_ticker_api_data(indicator_value, ticker_id, 0, 0, indicator[i][3],  indicator_name, indicator_id, data_date)
            except Exception as e:    
                log.Error(e)

            i+=1
    except Exception as e:    
        log.Error(e)

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

perform()