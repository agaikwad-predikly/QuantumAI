"""
This script runs the QuantumAI.API application using a development server.
"""

from os import environ

from flask import Flask,abort, request
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from flask_cors import CORS
from api import *
app = Flask(__name__)

app.register_blueprint(routes)
CORS(app)
@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, 81, threaded=True)


    