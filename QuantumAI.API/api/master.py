from flask import Blueprint
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from . import routes
from flask import Response
from flask import json
from helper import database as db

@routes.route("/ticker")
def ticker():
   tickers = db.call_procedure_with_header("get_ticker_details","")
   content = {'status': 'SUCCESS','status_code': '200', 'message' : 'SUCCESS', 'data': tickers}
   return Response(response=json.dumps(content),status=200,mimetype='application/json')
       