from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import Follow, User, Activity
from user.routes import user_id_in_db
import datetime

import requests

follow = Blueprint('follow', __name__)

@follow.route("/api/v1.0/user/<string:user_id>/followedby/<string:follower_id>", methods=["GET"])
def check_following(user_id, follower_id):
    exists = db.session.query(Follow.id).filter_by(user_id=user_id, follower_id=follower_id).scalar() is not None
    
    return make_response(jsonify(exists), 200)

@follow.route("/api/v1.0/user/<string:user_id>/followers", methods=["GET"])
def get_followers(user_id):
    results = db.session.query(Follow.follower_id, Follow.follow_date).filter_by(user_id=user_id)

    data_to_return = []

    for follower in results:
        user = {"user_id" : follower.follower_id, "follow_date" : follower.follow_date}
        data_to_return.append(user)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "This user has 0 followers or does not exist"}), 404)

def get_followed_users(user_id):
    results = db.session.query(Follow.user_id, Follow.follow_date, User.full_name, User.image).join(User, User.user_id==Follow.user_id).filter(Follow.follower_id==user_id)

    data_to_return = []

    for follower in results:
        user = {"user_id" : follower.user_id, "name" : follower.full_name, "image" : follower.image, "follow_date" : follower.follow_date, "followed_by" : user_id}
        data_to_return.append(user)

    return data_to_return

@follow.route("/api/v1.0/user/<string:user_id>/followed", methods=["GET"])
def get_followed(user_id):
    data_to_return = get_followed_users(user_id)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No followed users"}), 404)


@follow.route("/api/v1.0/user/<string:user_id>/follow/<string:follower_id>", methods=["POST"])
def follow_user(user_id, follower_id):
    if user_id_in_db(user_id) and user_id_in_db(follower_id):
        exists = db.session.query(Follow).filter(Follow.user_id==user_id, Follow.follower_id==follower_id).first() is not None

        if not exists:
            db.session.add(Follow(user_id=user_id, follower_id=follower_id, follow_date=datetime.date.today()))
            follow_id = db.session.query(Follow.id).filter_by(user_id=user_id, follower_id=follower_id).first()
            db.session.add(Activity(user_id=follower_id, action_id=6, object_id=5, date_created=datetime.datetime.now(), target_id=user_id))
            db.session.commit()
        
            return make_response(jsonify({"success" : "Followed user", "data" : follow_id}), 200)
        else:
            return make_response(jsonify({"error" : "Follow relationship already exists"}), 400)


    else:
        return make_response(jsonify({"error" : "Invalid user"}), 400)

@follow.route("/api/v1.0/user/<string:user_id>/unfollow/<string:follower_id>", methods=["DELETE"])
def unfollow_user(user_id, follower_id):
    exists = db.session.query(Follow).filter_by(user_id=user_id, follower_id=follower_id).scalar() is not None

    if exists:
        relationship = db.session.query(Follow).filter_by(user_id=user_id, follower_id=follower_id).first()
        db.session.delete(relationship)
        db.session.commit()

        return make_response(jsonify({"success" : "Unfollowed user"}), 204)
    else:
        return make_response(jsonify({"error" : "Relationship does not exist"}), 400)