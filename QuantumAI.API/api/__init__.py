from flask import Blueprint
routes = Blueprint('api', __name__)
import auth
import master
import indicator