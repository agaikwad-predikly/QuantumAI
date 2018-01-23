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
                formula = indicator[i][2]
                period = indicator[i][3]
                if last_date is None:
                    last_date = start_date
                else:
                    last_date = datetime.datetime.fromordinal(last_date.toordinal())

                if period=="DL":
                    daterange = pd.date_range(last_date, end_date)
                    for dt in daterange:
                        try:
                            if dt < datetime.date.today():
                                formula = indicator[i][8]

                            if formula!='':
                                indicator_value = CalculateFormula(formula, indicator[i][3], dt, ticker_id) 
                                save_ticker_indicator_data(indicator_value, ticker_id, indicator[i][3],  indicator_name, indicator_id, dt._date_repr)
                        except Exception as e:    
                            log.Error(e)
                elif period=="FQ":
                    quarter = helper.quarters_range(last_date, end_date)
                    x = 0
                    for x in range(len(quarter)):
                        try:
                            period_yr = quarter[x][1]
                            period_qtr = quarter[x][0]
                            prev_q_start, prev_q_end = get_start_end_date(period_yr, period_qtr, ticker_symbol)
                            if prev_q_end < datetime.date.today():
                                formula = indicator[i][8]
                            if formula!='':
                                indicator_value = CalculateFormula(formula, indicator[i][3], prev_q_start, ticker_id) 
                                save_ticker_indicator_data_multiple(indicator_value, ticker_id, indicator[i][3],  indicator_name, indicator_id, prev_q_start, prev_q_end)
                        except Exception as e:    
                            log.Error(e)
                        x+=1
                elif period=="FY":
                    years = range(last_date.year, end_date.year + 1)
                    x = 0
                    for x in range(len(years)):
                        try:
                            period_yr = years[x] 
                            prev_q_start, prev_q_end = get_start_end_date(period_yr, 0, ticker_symbol)
                            if prev_q_end < datetime.date.today():
                                formula = indicator[i][8]
                            if formula!='':
                                indicator_value = CalculateFormula(formula, indicator[i][3], prev_q_end, ticker_id) 
                                save_ticker_indicator_data_multiple(indicator_value, ticker_id, indicator[i][3],  indicator_name, indicator_id, prev_q_start, prev_q_end)
                        except Exception as e:    
                            log.Error(e)
                        x+=1
                   
            except Exception as e:    
                log.Error(e)

            i+=1
    except Exception as e:    
        log.Error(e)

def CalculateFormula(formula, period, date, ticker_id): 
    try:
        params = re.findall(r'@\d{0,5}{#?[\D]?[\D]?[+-]?\d+(?:\.\d+)?}',  formula)
        if params:
            params = set(params)
            for temp in params:
                api_id = int(re.sub("{#?[\D]?[\D]?[+-]?\d+(?:\.\d+)?}", "", temp).replace("@", ""))
                forms = re.sub("}|} ","",re.sub("[\d]+{", "", temp)).replace("@#", "")
                diff = int(re.sub("\D","",forms))
                ind_period = re.sub("[+-]?\d","",forms)
                year = date.year
                quarter=int(math.ceil(date.month/3.))
                if ind_period == 'Y' or ind_period == 'IY':
                    year = year + diff
                    period = "FY"
                elif ind_period == 'Q' or ind_period == 'IQ':
                    temp_date = date + timedelta((3*diff)*365/12)
                    quarter=int(math.ceil(temp_date.month/3.))
                    year = temp_date.year
                    period = "FQ"
                elif ind_period == 'QY':
                    temp_date = date + timedelta((3*diff)*365/12)
                    quarter=int(math.ceil(temp_date.month/3.))
                    year = temp_date.year - 1
                    period = "FQ"
                elif ind_period == 'D':
                    date =  date - timedelta(days=diff)
                    period = "DL"
                elif ind_period == 'AVGD':
                    year =  diff
                    period = "AVG"
                str_date = date.strftime("%Y-%m-%d")
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

def get_start_end_date(f_year, f_quarter,ticker_symbol ):
    period_end_dt = datetime.date.today()
    period_start_dt = datetime.date.today()
    try:
        period = "FY0"
        current_yr = datetime.datetime.now().year
        year = current_yr if (f_year>current_yr) else f_year
        if f_quarter>0:
            period = str(f_quarter) + "FQ" + str(year)
        else:
            period = "FY" + str(year)
        ek.set_app_id('93D5C93060C3ECEAD451638')
        df = ek.get_data(instruments=[ticker_symbol], fields=['TR.SMPeriodEndDate'],parameters={'Period': period},debug=True)
        period_end_dt = df[0]["Period End Date"][0]
        if f_quarter>0:
            dt = period_end_dt + relativedelta(months=-3, days=0)
            period_start_dt = datetime.date(dt.year,dt.month, 1)
        else:
            dt = period_end_dt + relativedelta(years=-1, days=0)
            period_start_dt = datetime.date(dt.year,dt.month, 1)
    except Exception as e: 
         period_start_dt, period_end_dt =helper.quarter_start_end(f_quarter, f_year)
    return period_start_dt, period_end_dt
perform()