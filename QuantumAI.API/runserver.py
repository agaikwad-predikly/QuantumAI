"""
This script runs the QuantumAI.API application using a development server.
"""

from os import environ

from flask import Flask
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from api import *
app = Flask(__name__)

app.register_blueprint(routes)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, 50515)


    