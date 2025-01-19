from flask import Blueprint

article_generate = Blueprint('article_generate', __name__)

from . import views, models
