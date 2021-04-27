from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import User

user = Blueprint('user', __name__)

def user_id_in_db(user):
    return db.session.query(User.user_id).filter_by(user_id=user).scalar() is not None

def user_auth0_in_db(user):
    return db.session.query(User.user_id).filter_by(auth0_id=user).scalar() is not None

@user.route("/api/v1.0/userinDB/<string:auth0_id>", methods=["GET"])
def user_auth0_in_db(auth0_id):
    exists = db.session.query(User.user_id).filter_by(auth0_id=auth0_id).scalar() is not None

    if exists:
        return make_response(jsonify(exists), 200)
    else:
        return make_response(jsonify(exists), 404)

@user.route("/api/v1.0/auth0/<auth0_id>", methods=["GET"])
def get_user_id_by_auth0(auth0_id):
    try:
        user_id = get_user_id(auth0_id)
        return make_response(jsonify(user_id), 200)
    except:
        return make_response(jsonify({"error" : "Invalid ID"}), 404)

def get_user_id(auth0_id):
    user = db.session.query(User).filter_by(auth0_id=auth0_id).first()
    return user.user_id

@user.route("/api/v1.0/user/<user_id>", methods=["GET"])
def get_user_details(user_id):
    data_to_return = []

    try:
        result = db.session.query(User).filter_by(user_id=user_id).first()
    except:
        return make_response(jsonify({"error" : "Invalid ID"}), 404)
    
    user = {"user_id" : result.user_id, "auth0_id" : result.auth0_id, "name" : result.full_name, "image" : result.image}
    data_to_return.append(user)

    return make_response(jsonify(data_to_return), 200)