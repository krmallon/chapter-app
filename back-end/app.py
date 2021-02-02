from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.py")
DB_URI = config.get("DEFAULT", "DB_URI")

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db = SQLAlchemy(app)