from flask import Blueprint, request
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from . import routes
from flask import Response
from flask import json
from helper import database as db
from api import auth
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta, time
import math
from dateutil.relativedelta import relativedelta
import re

@routes.route("/portfolio_predict", methods = ['GET'])
@auth.require_api_token
def portfolio_predict():
	params = request.args.to_dict()
	if(params is not None and "date" in params and "indicator_type" in params and "target_type" in params and "target_type" in params  and params["date"] is not None and params["indicator_type"] is not None and params["target_type"] is not None):
		if "limit" not in params or params["limit"] is not None:
			params["limit"] = 50
		if "adv_weight" not in params or params["adv_weight"] is not None:
			params["adv_weight"] = 20 if(params["target_type"]==1) else 0
		tickers = db.call_procedure_with_header("get_portfolio_prediction_details",[params["date"], params["indicator_type"],params["target_type"],params["adv_weight"],params["limit"]])
		df = pd.DataFrame(tickers)
		tk_lists = []
		if df is not None:
			per = pd.DatetimeIndex(df.value_date).to_period("M")
			tk_list = df.groupby(per).mean()
			for index, row in tk_list.iterrows():
				json_obj = {}
				json_obj["value_date"]=datetime.datetime(index.year, index.month, index.day)
				json_obj["price_gain"]=row["price_gain"]
				json_obj["percent_gain"]=row["percent_gain"]
				data_arr = []
				for index2, row in df.iterrows():
					if row["value_date"].month == index.month and row["value_date"].year == index.year :
						data  = {}
						data["ticker_id"] = row["ticker_id"]
						data["ticker_name"]= row["ticker_name"]
						data["ticker_symbol"]=row["ticker_symbol"]
						data["price_gain"]=row["price_gain"]
						data["percent_gain"]= row["percent_gain"]
						data["fundamental_strength_column_count"]=row["fundamental_strength_column_count"]
						data["fundamental_strength"]=row["fundamental_strength"]
						data["pred_buy_fund_target"] =row["pred_buy_fund_target"]
						data["pred_buy_fund_probability"]=row["pred_buy_fund_probability"]
						data["technical_strength"] =row["technical_strength"]
						data["technical_strength_column_count"]=row["technical_strength_column_count"]
						data["pred_tech_target"] =row["pred_tech_target"]
						data["pred_tech_probability"]=row["pred_tech_probability"]
						data["pred_short_sell_fund_target"]=row["pred_short_sell_fund_target"]
						data["pred_short_sell_fund_probability"]=row["pred_short_sell_fund_probability"]
						data["is_newly_added"]=row["is_newly_added"]
						data_arr.append(data)
				json_obj["percent_gain"]=data_arr
				tk_lists.append(json_obj)

		content = {'status': 'SUCCESS','status_code': '200', 'message' : 'SUCCESS', 'data': tk_lists}
		return Response(response=json.dumps(content),status=200,mimetype='application/json')
	else:
		content = {'status': 'BAD REQUEST','status_code': '400', 'message' : 'Need parameter date, indicator_type, target_type, adv_weight, limit', 'data': None}#tickers}
		return Response(response=json.dumps(content),status=200,mimetype='application/json')


@routes.route("/portfolio_predict_month", methods = ['GET'])
@auth.require_api_token
def portfolio_predict_monthly():
	params = request.args.to_dict()
	if(params is not None and "date" in params and "indicator_type" in params and "target_type" in params and "target_type" in params  and params["date"] is not None and params["indicator_type"] is not None and params["target_type"] is not None):
		if (not "limit"  in params) or (params["limit"] is  None):
			params["limit"] = 50
		if ("adv_weight" not in params) or (params["adv_weight"] is  None):
			params["adv_weight"] = 20 if(params["target_type"]==1) else 0
		tickers = db.call_procedure_with_header("get_mom_portfolio_prediction_details",[params["date"], params["indicator_type"],params["target_type"],params["adv_weight"],params["limit"]])
		content = {'status': 'SUCCESS','status_code': '200', 'message' : 'SUCCESS', 'data': tickers}
		return Response(response=json.dumps(content),status=200,mimetype='application/json')
	else:
		content = {'status': 'BAD REQUEST','status_code': '400', 'message' : 'Need parameter date, indicator_type, target_type, adv_weight, limit', 'data': None}#tickers}
		return Response(response=json.dumps(content),status=200,mimetype='application/json')
