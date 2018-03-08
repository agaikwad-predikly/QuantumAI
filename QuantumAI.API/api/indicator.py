from flask import Blueprint
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from . import routes
from flask import Response
from flask import json
from helper import database as db

@routes.route("/simulate_data/<from_date>/<to_date>/<ticker_ids>/<type>/<period_type>")
def get_simulation_data(from_date, to_date, ticker_ids, type, period_type):
   tickers = db.call_procedure_with_header("get_ticker_details","")
   content = {'status': 'SUCCESS','status_code': '200', 'message' : 'SUCCESS', 'data': tickers}
   return Response(response=json.dumps(content),status=200,mimetype='application/json')


@routes.route("/simulate_data/<target_date>/<type>")
def get_simulation_data(target_date,type):
   tickers = db.call_procedure_with_header("get_ticker_details","")
   content = {'status': 'SUCCESS','status_code': '200', 'message' : 'SUCCESS', 'data': tickers}
   return Response(response=json.dumps(content),status=200,mimetype='application/json')
       