from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import Achievement, UserAchievement, Goal, Activity
import datetime

achievement = Blueprint('achievement', __name__)


@achievement.route("/api/v1.0/achievements", methods=["GET"])
def get_all_achievements():
    data_to_return = []
    achievements = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge).all()

    for achievement in achievements:
        ach = {"id" : achievement.id, "name" : achievement.name, "description" : achievement.description, "image" : achievement.badge}
        data_to_return.append(ach)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No achievements found"}), 404)

@achievement.route("/api/v1.0/achievements/<id>", methods=["GET"])
def get_one_achievement(id):
    data_to_return = []
    achievements = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge).filter(Achievement.id==id).all()

    for achievement in achievements:
        ach = {"id" : achievement.id, "name" : achievement.name, "description" : achievement.description, "image" : achievement.badge}
        data_to_return.append(ach)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No achievement found"}), 404)



@achievement.route("/api/v1.0/user/<string:user_id>/achievements", methods=["GET"])
def get_user_achievements(user_id):
    data_to_return = []
    user_achievements = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge, UserAchievement.date_earned).join(UserAchievement, Achievement.id == UserAchievement.achievement_id).filter(UserAchievement.user_id==user_id)

    for achievement in user_achievements:
        ach = {"name" : achievement.name, "description" : achievement.description, "date_earned" : achievement.date_earned, "image" : achievement.badge}
        data_to_return.append(ach)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No achievements found"}), 404)

# def update_achievement_progress(user_id, achievement):
#     if achievement == 1:



def check_achievement(user_id, achievement_type):
    if achievement_type == 'review':
        try:
            first_review = db.session.query(Review).filter(Review.reviewer_id==user_id).one()
            if first_review is not None:
                db.session.add(UserAchievement(user_id=user_id, achievement_id=1, date_earned=datetime.date.today()))
                db.session.add(Activity(user_id=user_id, action_id=7, object_id=4, date_created=datetime.datetime.now(), target_id=1))
        except Exception:
            pass
    if achievement_type == 'group':
        try:
            first_group = db.session.query(Group).filter(Group.founder_id==user_id).one()
            if first_group is not None:
                db.session.add(UserAchievement(user_id=user_id, achievement_id=2, date_earned=datetime.date.today()))
                db.session.add(Activity(user_id=user_id, action_id=7, object_id=4, date_created=datetime.datetime.now(), target_id=2))
        except Exception:
            pass
    if achievement_type == 'goal':
        goals = db.session.query(Goal).filter(Goal.user_id==user_id).all()
        count = db.session.query(Goal).filter(Goal.user_id==user_id).count()
        exists = db.session.query(UserAchievement).filter(UserAchievement.user_id==user_id, UserAchievement.achievement_id==3).scalar() is not None

        if count == 0 and not exists:
            db.session.add(UserAchievement(user_id=user_id, achievement_id=3, date_earned=datetime.date.today()))
            db.session.add(Activity(user_id=user_id, action_id=7, object_id=4, date_created=datetime.datetime.now(), target_id=3))

        for goal in goals:
            if goal.current == goal.target:
                db.session.add(UserAchievement(user_id=user_id, achievement_id=4, date_earned=datetime.date.today()))
                db.session.add(Activity(user_id=user_id, action_id=7, object_id=4, date_created=datetime.datetime.now(), target_id=4))

    if achievement_type == 'reading':
        count = db.session.query(HasRead).filter(HasRead.user_id==user_id).count()
        if count == 10:
            db.session.add(UserAchievement(user_id=user_id, achievement_id=5, date_earned=datetime.date.today()))
            db.session.add(Activity(user_id=user_id, action_id=7, object_id=4, date_created=datetime.datetime.now(), target_id=5))

    db.session.commit()