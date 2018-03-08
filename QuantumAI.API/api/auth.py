from flask import Blueprint
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from . import routes
from flask import Response
from flask import json

@routes.route("/authenticate")
@routes.route('/authenticate/<username>/<password>')
def authenticate(username, password):
    if username is not None and password is not None and username!='' and password !='':
        if username=='admin' and password=='admin':
            content = {'status': 'SUCCESS','status_code': '200', 'message' : 'SUCCESS', 'data': {'token':'AD3EDSFEF3EF23E123'}}
            return Response(response=json.dumps(content),status=200,mimetype='application/json')
        else:
            content = {'status': 'ERROR','status_code': '400', 'message' : 'Please enter username and password'}
            return Response(response=json.dumps(content),status=200,mimetype='application/json')
    else:
        content = {'status': 'ERROR','status_code': '400', 'message' : 'Please enter username and password'}
        return Response(response=json.dumps(content),status=200,mimetype='application/json')
