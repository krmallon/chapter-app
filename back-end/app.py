from config import DB_URI, auth0_access_token
from extensions import db
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
# from models import *
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.sql import label
import requests
import book_recommender

from book.routes import book
from search.routes import search
from follow.routes import follow
from achievement.routes import achievement
from activity.routes import activity
from goal.routes import goal
from group.routes import group
from message.routes import message
from recommendation.routes import recommendation
from review.routes import review
from stats.routes import stats
from user.routes import user

import configparser
import datetime

app = Flask(__name__)
CORS(app)

app.register_blueprint(book)
app.register_blueprint(search)
app.register_blueprint(follow)
app.register_blueprint(stats)
app.register_blueprint(achievement)
app.register_blueprint(activity)
app.register_blueprint(goal)
app.register_blueprint(group)
app.register_blueprint(message)
app.register_blueprint(recommendation)
app.register_blueprint(review)
app.register_blueprint(user)


app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)