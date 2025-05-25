import os
from decouple import config
from flask import Flask, request
from flask_avatars import Avatars
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
# from src.tasks.scheduler import schedule_tasks

def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.config['SESSION_SQLALCHEMY'] = db

moment = Moment(app)

avatars = Avatars(app)

cache = Cache(app)

from src.web.routes import web

# Registering blueprints
app.register_blueprint(web, url_prefix='/')


# schedule_tasks()