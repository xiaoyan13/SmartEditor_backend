from flask import Blueprint

prompt = Blueprint('prompt', __name__)

from . import views, models
