import database as db
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta, time
import math
from dateutil.relativedelta import relativedelta
import error_log as log
import re

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
            print ticker_sym + " for date " + start_date.strftime("%Y-%m-%d %H:%M:%S") + "-" + end_date.strftime("%Y-%m-%d %H:%M:%S")
            ticker_id = tickers[i][2]
            print "Job Start Date:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print "Indicators"
            get_indicator_for_ticker_for_date(start_date,end_date, ticker_id, ticker_sym)
            print "Job End Date:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                if last_date is None:
                    last_date = start_date
                else:
                    last_date = datetime.datetime.fromordinal(last_date.toordinal())
                daterange = pd.date_range(last_date, end_date)
                for dt in daterange:
                    try:
                        indicator_value = CalculateFormula(formula, indicator[i][3], dt, ticker_id) 
                        save_ticker_indicator_data(indicator_value, ticker_id, indicator[i][3],  indicator_name, indicator_id, dt._date_repr)
                    except Exception as e:    
                        log.Error(e)
            except Exception as e:    
                log.Error(e)

            i+=1
    except Exception as e:    
        log.Error(e)

def CalculateFormula(formula, period, date, ticker_id): 
    try:
        params = re.findall(r'@\d{0,5}{#?[D|Y|Q]?[+-]?\d+(?:\.\d+)?}',  formula)
        if params:
            params = set(params)
            for temp in params:
                api_id = int(re.sub("{#?[D|Y|Q]?[+-]?\d+(?:\.\d+)?}", "", temp).replace("@", ""))
                forms = re.sub("}|} ","",re.sub("[\d]+{", "", temp)).replace("@#", "")
                diff = int(re.sub("D|Y|Q","",forms))
                ind_period = re.sub("[+-]?\d","",forms)
                year = date.year
                quater=int(math.ceil(date.month/3.))
                if ind_period == 'Y':
                    year = year + diff
                    period = "FY"
                elif ind_period == 'Q':
                    temp_date = date + timedelta((3*diff)*365/12)
                    quater=int(math.ceil(temp_date.month/3.))
                    year = temp_date.year
                    period = "FQ"
                elif ind_period == 'D':
                    date =  date - timedelta(days=diff)
                    period = "DL"
                str_date = date.strftime("%Y-%m-%d")
                api_value = db.call_procedure("get_api_values",[ticker_id, period, year, quater, str_date, api_id])
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

perform()