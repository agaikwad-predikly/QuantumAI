import database as db
import eikon as ek
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import math
from dateutil.relativedelta import relativedelta
import error_log as log
ek.set_app_id('asdasdasdsadasd')
	
def save_ticker_data(df, ticker_id):
	dt = pd.DataFrame(df)
	for index, row in dt.iterrows():
		stocks = db.call_procedure("insert_update_eod_data",[ticker_id, row.name, float(row['HIGH']), float(row['CLOSE']), float(row['LOW']), float(row['OPEN']), float(row['COUNT']), float(row['VOLUME'])])

def save_ticker_indicator_data(df, ticker_id, period_yr, period_qtr, period_type, indicator_name, indicator_id, for_date):
	indicator_value = df[0][indicator_name][0]
	stocks = db.call_procedure("insert_update_indicator_data",[ticker_id, indicator_id, period_type, period_yr, period_qtr, float(indicator_value), for_date])

		
def perform():	
	d1 = datetime.datetime.now()
	d2 = d1 - relativedelta(years=20)
	perform_for_date(d1, d2)


def perform_for_date(start_date,end_date):
	if (relativedelta(start_date, end_date).years > 10):
		dt_dif = divmod(relativedelta(start_date, end_date).years, 10)
		loopcnt = 0
		if dt_dif[1] == 0:
			loopcnt = divmod(relativedelta(start_date, end_date).years, 10)[0]
		else:
			loopcnt = divmod(relativedelta(start_date, end_date).years, 10)[0] + 1
		for x in range(loopcnt):  
			new_end_date = start_date - relativedelta(years=(10))
			if end_date > new_end_date:
				new_end_date = end_date
			get_data_for_date(start_date,new_end_date)
			start_date = new_end_date
			
	else:
		get_data_for_date(start_date,end_date)
		
def get_data_for_date(start_date,end_date):
	tickers = db.call_procedure("get_ticker_details","")
	i = 0
	while i < len(tickers):
		ticker_sym = tickers[i][1]
		print ticker_sym + " for date " + end_date.strftime("%Y-%m-%d %H:%M:%S") + "-" + start_date.strftime("%Y-%m-%d %H:%M:%S")
		ticker_id = tickers[i][2]
		print "Job Start Date:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print "EOD"
		#get_eod_for_ticker_for_date(end_date, start_date, ticker_id, ticker_sym)
		print "Indicators"
		get_indicator_for_ticker_for_date(end_date, start_date, ticker_id, ticker_sym)
		print "Job End Date:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		i+=1

		
def get_eod_for_ticker_for_date(start_date, end_date, ticker_id, ticker_symbol):
	df = ek.get_timeseries(ticker_symbol, fields='*', start_date=start_date,  end_date=end_date, interval='daily', count=None, calendar=None, corax=None, normalize=False, raw_output=False, debug=False)
	save_ticker_data(df, ticker_id)
			
def get_indicator_for_ticker_for_date(start_date, end_date, ticker_id, ticker_symbol):
    try:
	    indicator = db.call_procedure("get_indicator_api_details",[ticker_id])	
	    fy_indicators, fq_indicators = [],[]
	    i = 0
	    while i < len(indicator):
		    last_date = indicator[i][7]
		    if last_date is None:
			    last_date = end_date
		    if indicator[i][3] == 'FQ':				
			    quater = quarters_range(start_date, last_date)
			    x = 0
			    for x in range(len(quater)):
				    period_yr = quater[x][1]
				    period_qtr = quater[x][0]
				    period = (str(period_qtr) + 'FQ' + str(period_yr))
				    params = {'Period': period}
				    if indicator[i][5] > 0:
					    params['Scale'] = indicator[i][5]
					
				    if indicator[i][6] is not None:
					    params['Curn'] = indicator[i][6]
				    df = ek.get_data(ticker_symbol, {indicator[i][2]:{'params':params}},debug=True)
				    save_ticker_indicator_data(df, ticker_id, period_yr, period_qtr, 'FQ', indicator[i][0], indicator[i][1], datetime.date.today())
		    elif indicator[i][3] == 'DL':
			    delta = last_date - start_date     # timedelta
			    for j in range(delta.days + 1):
				    period_days = start_date + timedelta(days=j)
				    period_yrs = period_days.year
				    params = {'SDate': period_days.strftime("%Y%m%d")}

				    if indicator[i][5] > 0:
					    params['Scale'] = indicator[i][5]
					
				    if indicator[i][6] is not None:
					    params['Curn'] = indicator[i][6]
					
				    df = ek.get_data(ticker_symbol, {indicator[i][2]:{'params':params}},debug=True)
				    save_ticker_indicator_data(df, ticker_id, period_yrs, 0, 'DL', indicator[i][0], indicator[i][1],period_days)			
		    elif indicator[i][3] == 'FY':
			    years = range(last_date.year + 1, datetime.datetime.now().year + 1)
			    x = 0
			    for x in range(len(years)):
				    period_yr = years[x]
				    period = ('FY' + str(period_yr))
				    params = {'Period': period}
				    if indicator[i][5] > 0:
					    params['Scale'] = indicator[i][5]
					
				    if indicator[i][6] is not None:
					    params['Curn'] = indicator[i][6]
				
				    df = ek.get_data(ticker_symbol, {indicator[i][2]:{'params':params}},debug=True)
				    save_ticker_indicator_data(df, ticker_id, period_yr, 0, 'FY', indicator[i][0], indicator[i][1], datetime.date.today())
		    elif indicator[i][3] == 'EX':
			    df = ek.get_data(indicator[i][8], indicator[i][2],debug=True)
			    save_ticker_indicator_data(df, ticker_id, 0, 0, indicator[i][3], indicator[i][0], indicator[i][1], datetime.date.today())
		    else:
			    df = ek.get_data(ticker_symbol, indicator[i][2],debug=True)
			    save_ticker_indicator_data(df, ticker_id, 0, 0, indicator[i][3], indicator[i][0], indicator[i][1], datetime.date.today())
			
		    i+=1
    except Exception as e:    
        log.Error(e)
    
	
def quarters_range(date_to, date_from=None):
			result = []
			if date_from is None:
				date_from = datetime.datetime.now()
		
			quarter_from = ((date_from.month / 4) + 1)
			quarter_to = (date_to.month / 4) + 1
			for year in range(date_to.year, date_from.year + 1):
				for quarter in range(1, 5):
					if date_to.year == year and quarter >= quarter_to:
						break
					if date_from.year == year and quarter <= quarter_from:
						continue
					result.append([quarter, year])
			return (result)

def get_next_quater(current_date):
	Q = math.ceil(current_date.month / 3.)
	if Q == 4:
		return "1FQ" + str(current_date.year + 1)
	else:
		return str(Q + 1) + "FQ" + str(current_date.year)



perform()