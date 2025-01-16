from flask import Blueprint

article_config = Blueprint('article_config', __name__)

from . import views, models
