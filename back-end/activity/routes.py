from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import User, Activity, Action, Book, Review, Achievement
from follow.routes import get_followed_users
from sqlalchemy.sql import label, func
import datetime

activity = Blueprint('activity', __name__)


@activity.route("/api/v1.0/activity/<string:user_id>", methods=["GET"])
def get_all_activity_by_user(user_id):
    data_to_return = []

    activities = db.session.query(Action.description, Activity.date_created, Activity.target_id, Activity.action_id, Activity.object_id, User.user_id, User.full_name).join(User, Activity.user_id==User.user_id).join(Action, Activity.action_id==Action.id).filter(Activity.user_id==user_id)

    for activity in activities:
        if activity.action_id == 1:
            target = db.session.query(Book.title, Book.author, Book.ISBN, Review.id, Review.rating, Review.text).join(Review, Book.book_id==Review.book_id).filter(Book.book_id==activity.target_id).first()
        elif activity.action_id == 2 or activity.action_id == 3 or activity.action_id == 4:
            target = db.session.query(Book.title, Book.author, Book.ISBN).filter(Book.book_id==activity.target_id).first()
        elif activity.action_id == 5:
            target = db.session.query(Book.title, Book.author, Book.ISBN, Review.id, Review.rating, Review.text, User.user_id, User.full_name).join(Book, Review.book_id==Book.book_id).join(User, User.user_id==Review.reviewer_id).filter(Review.id==activity.target_id).first()
        elif activity.action_id == 6:
            target = db.session.query(User.user_id, User.full_name).filter(User.user_id==activity.target_id).first()
        elif activity.action_id == 7:
            target = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge).filter(Achievement.id==activity.target_id).first()

        act = {"user_id" : activity.user_id, "user" : activity.full_name, "action" : activity.description, "target" : target, "date_created" : activity.date_created}
        data_to_return.append(act)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No activities found"}), 404)

@activity.route("/api/v1.0/activity/followedby/<string:user_id>", methods=["GET"])
def get_activity_followed_users(user_id):
    data_to_return = []

    followed = get_followed_users(user_id)

    activities = db.session.query(Action.description, Activity.id, Activity.date_created, Activity.target_id, Activity.action_id, Activity.object_id, User.user_id, User.full_name, User.image).join(User, Activity.user_id==User.user_id).join(Action, Activity.action_id==Action.id).filter(Activity.user_id.in_([(f['user_id']) for f in followed])).order_by(Activity.date_created.desc()).all()
   
    for activity in activities:
        likes = get_like_count(7, activity.id)
        target = ""
        if activity.action_id == 1:
            target = db.session.query(Book.title, Book.author, Book.ISBN, Book.image_link, Review.id, Review.rating, Review.text).join(Review, Book.book_id==Review.book_id).filter(Book.book_id==activity.target_id).first()
        elif activity.action_id == 2 or activity.action_id == 3 or activity.action_id == 4:
            target = db.session.query(Book.title, Book.author, Book.ISBN, Book.image_link).filter(Book.book_id==activity.target_id).first()
        elif activity.action_id == 5:
            if activity.object_id == 2:
                target = db.session.query(Book.title, Book.author, Book.ISBN, Review.id, Review.rating, Review.text, User.user_id, User.full_name).join(Book, Review.book_id==Book.book_id).join(User, User.user_id==Review.reviewer_id).filter(Review.id==activity.target_id).first()
            if activity.object_id == 3:
                target = db.session.query(Comment.comment_id, Comment.commenter_id, Comment.text, Comment.time_submitted, User.user_id, User.full_name).join(User, Comment.commenter_id==User.user_id).filter(Comment.comment_id==activity.target_id).first()
            if activity.object_id == 4:
                target = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge).filter(Achievement.id==activity.target_id).first()
            # if activity.object_id == 7:
                
                # activity_user = db.session.query(Activity.user_id).filter(Activity.id==activity.target_id).first()
                # target = db.session.query(User.full_name, User.user_id, User.image).filter(User.user_id==activity_user).first()
        elif activity.action_id == 6:
            target = db.session.query(User.user_id, User.full_name, User.image).filter(User.user_id==activity.target_id).first()
        elif activity.action_id == 7:
            target = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge).filter(Achievement.id==activity.target_id).first()

        # return all updates with exception of 'User X liked User Y's update'
        if not activity.object_id == 7:
            act = {"activity_id" : activity.id, "user_id" : activity.user_id, "user" : activity.full_name, "user_image" : activity.image, "action" : activity.description, "object_id" : activity.object_id, "target" : target, "date_created" : activity.date_created, "likes" : likes}
            data_to_return.append(act)
        
        # act = {"activity_id" : activity.id, "user_id" : activity.user_id, "user" : activity.full_name, "user_image" : activity.image, "action" : activity.description, "object_id" : activity.object_id, "target" : target, "date_created" : activity.date_created, "likes" : likes}
        # data_to_return.append(act)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No activities found"}), 404)

@activity.route("/api/v1.0/<string:user_id>/likes", methods=["POST"])
def add_like(user_id):
    if request.args.get('objectID') and request.args.get('targetID'):
        object_id = request.args.get('objectID')
        target_id = request.args.get('targetID')
        # add constants file and have LIKE_ID as 5 instead of hard coding like this
        liked = db.session.query(Activity).filter(Activity.user_id==user_id, Activity.action_id==5, Activity.target_id==target_id).scalar() is not None

        if not liked:
            db.session.add(Activity(user_id=user_id, action_id=5, object_id=object_id, date_created=datetime.date.today(), target_id=target_id))
            db.session.commit()
            
            return make_response(jsonify({"success" : "Added like"}), 201)
        else:
            return make_response(jsonify({"error" : "Failed to add like"}), 404)
    else:
        return make_response(jsonify({"error" : "Failed to add like"}), 404)

@activity.route("/api/v1.0/likes", methods=["GET"])
def get_like_count():
    if request.args.get('objectID') and request.args.get('targetID'):
        object_id = request.args.get('objectID')
        target_id = request.args.get('targetID')
        num_likes = db.session.query(label('num_likes', func.count(Activity.id))).filter(Activity.action_id==5, Activity.object_id==object_id,Activity.target_id==target_id).all()

        return make_response(jsonify(num_likes), 200)
    else:
        return make_response(jsonify({"error" : "Failed to return like count"}), 404)


def get_like_count(object_id, target_id):
    likes = db.session.query(label('count', func.count(Activity.id))).filter(Activity.action_id==5, Activity.object_id==object_id,Activity.target_id==target_id).all()

    # for lk in likes:
    #     num_likes = lk['num_likes']

    return likes[0]

    # return likes.num_likes
    # return num_likes
