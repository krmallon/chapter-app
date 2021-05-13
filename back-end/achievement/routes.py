from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import Achievement, UserAchievement, Goal, Activity, Review, HasRead, Group
import datetime
from sqlalchemy import exc
import traceback
# from constants import REVIEW_ACH_TYPE, GOAL_ACH_TYPE, READING_ACH_TYPE, GROUP_ACH_TYPE
# from constants import FIRST_REVIEW_ID, GROUP_FOUNDER_ID, GOAL_SET_ID, GOAL_ACHIEVED_ID, READ_10_BOOKS_ID
# from activity.constants import EARNED_ACHIEVEMENT_ACTION_ID, ACHIEVEMENT_OBJECT_ID

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



def check_achievement(user_id, achievement_type):
    if achievement_type == REVIEW_ACH_TYPE:
        try:
            first_review = db.session.query(Review).filter(Review.reviewer_id==user_id).one()
            if first_review is not None:
                db.session.add(UserAchievement(user_id=user_id, achievement_id=FIRST_REVIEW_ID, date_earned=datetime.date.today()))
                db.session.add(Activity(user_id=user_id, action_id=EARNED_ACHIEVEMENT_ACTION_ID, object_id=ACHIEVEMENT_OBJECT_ID, 
                                date_created=datetime.datetime.now(), target_id=FIRST_REVIEW_ID))
        except exc.SQLAlchemyError:
            traceback.print_exc()
    if achievement_type == GROUP_ACH_TYPE:
        try:
            first_group = db.session.query(Group).filter(Group.founder_id==user_id).one()
            if first_group is not None:
                db.session.add(UserAchievement(user_id=user_id, achievement_id=GROUP_FOUNDER_ID, date_earned=datetime.date.today()))
                db.session.add(Activity(user_id=user_id, action_id=EARNED_ACHIEVEMENT_ACTION_ID, object_id=ACHIEVEMENT_OBJECT_ID, 
                                date_created=datetime.datetime.now(), target_id=GROUP_FOUNDER_ID))
        except exc.SQLAlchemyError:
            traceback.print_exc()
    if achievement_type == GOAL_ACH_TYPE:
        goals = db.session.query(Goal).filter(Goal.user_id==user_id).all()
        count = db.session.query(Goal).filter(Goal.user_id==user_id).count()
        exists = db.session.query(UserAchievement).filter(UserAchievement.user_id==user_id, UserAchievement.achievement_id==GOAL_SET_ID).scalar() is not None

        if count == 0 and not exists:
            db.session.add(UserAchievement(user_id=user_id, achievement_id=GOAL_SET_ID, date_earned=datetime.date.today()))
            db.session.add(Activity(user_id=user_id, action_id=EARNED_ACHIEVEMENT_ACTION_ID, object_id=ACHIEVEMENT_OBJECT_ID, date_created=datetime.datetime.now(), target_id=GOAL_SET_ID))

        for goal in goals:
            if goal.current == goal.target:
                db.session.add(UserAchievement(user_id=user_id, achievement_id=GOAL_ACHIEVED_ID, date_earned=datetime.date.today()))
                db.session.add(Activity(user_id=user_id, action_id=EARNED_ACHIEVEMENT_ACTION_ID, object_id=ACHIEVEMENT_OBJECT_ID, date_created=datetime.datetime.now(), target_id=GOAL_ACHIEVED_ID))

    if achievement_type == READING_ACH_TYPE:
        count = db.session.query(HasRead).filter(HasRead.user_id==user_id).count()
        if count == 10:
            db.session.add(UserAchievement(user_id=user_id, achievement_id=READ_10_BOOKS_ID, date_earned=datetime.date.today()))
            db.session.add(Activity(user_id=user_id, action_id=EARNED_ACHIEVEMENT_ACTION_ID, object_id=ACHIEVEMENT_OBJECT_ID, date_created=datetime.datetime.now(), target_id=READ_10_BOOKS_ID))

    db.session.commit()