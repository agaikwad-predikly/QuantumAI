from flask import Blueprint
routes = Blueprint('api', __name__)
from . import auth
from . import master
from . import indicator