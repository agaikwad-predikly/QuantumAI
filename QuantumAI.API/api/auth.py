from flask import Blueprint,Response, request,json
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from . import routes

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

def validate_token():
    # Check to see if it's in their session
	auth = request.authorization
	if not auth:  # no header set
		content = {'status': 'UNAUTHENTICATED','status_code': '401', 'message' : 'UNAUTHENTICATED'}
		return Response(response=json.dumps(content),status=200,mimetype='application/json')
	if auth != "AD3EDSFEF3EF23E123":
		content = {'status': 'UNAUTHENTICATED','status_code': '401', 'message' : 'UNAUTHENTICATED'}
		return Response(response=json.dumps(content),status=200,mimetype='application/json')
    # Otherwise just send them where they wanted to go
	return 1

def require_api_token(func):
	def check_token(*args, **kwargs):
		# Check to see if it's in their session
		auth = request.headers.get('Authorization')
		if not auth:  # no header set
			content = {'status': 'UNAUTHENTICATED','status_code': '401', 'message' : 'UNAUTHENTICATED'}
			return Response(response=json.dumps(content),status=200,mimetype='application/json')
		if auth != "AD3EDSFEF3EF23E123":
			content = {'status': 'UNAUTHENTICATED','status_code': '401', 'message' : 'UNAUTHENTICATED'}
			return Response(response=json.dumps(content),status=200,mimetype='application/json')
        # Otherwise just send them where they wanted to go
		return func(*args, **kwargs)
	# Renaming the function name:
	check_token.func_name = func.func_name
 
	return check_token