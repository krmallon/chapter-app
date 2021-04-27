from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import Goal

goal = Blueprint('goal', __name__)


@goal.route("/api/v1.0/<string:user_id>/goals", methods=["GET"])
def get_goals_by_user_id(user_id):
    data_to_return = []

    goals = db.session.query(Goal.id, Goal.target, Goal.current, Goal.year).filter(Goal.user_id==user_id).all()

    for goal in goals:
        goal_id = goal.id
        target = goal.target
        current = goal.current
        year = goal.year
        data_to_return.append(goal)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No goals found"}), 404)

@goal.route("/api/v1.0/goals/new", methods=["POST"])
def set_new_reading_goal():
    if "user_id" in request.form and "target" in request.form and "year" in request.form:
        user_id = request.form["user_id"],
        target = request.form["target"],
        year = request.form["year"]

        check_achievement(user_id, 'goal')
        # change so current reads from count of HasRead with dates within that year
        # current = db.session.query(func.count(HasRead).label('current')).filter(HasRead.user_id==user_id, HasRead.finish_date.between(year + '-01-01', year + '-12-31')).all()
        # authors = db.session.query(func.count(Book.author).label('count'), Book.author).join(HasRead, HasRead.book_id==Book.book_id).filter(HasRead.user_id==user_id).group_by(Book.author).order_by(desc('count')).limit(3).all()
        existing_goal = db.session.query(Goal).filter(Goal.user_id==user_id, Goal.year==year).scalar() is not None

        if not existing_goal:
            db.session.add(Goal(target=target, current=0, user_id=user_id, year=year))
            db.session.commit()

        return make_response(jsonify({"success:" : "Reading goal successfully set"}), 200)
    else:
        return make_response(jsonify({"error:" : "Failed to set goal"}), 404)

@goal.route("/api/v1.0/goals/<string:goal_id>", methods=["PUT"])
def edit_reading_goal(goal_id):
    if "target" in request.form:
        new_target = request.form["target"]

    goal = db.session.query(Goal).filter(Goal.id==goal_id).first()
    goal.target = new_target
    db.session.commit()

    return make_response(jsonify({"success:" : "Reading goal successfully edited"}), 200)
    

@goal.route("/api/v1.0/goals/<string:goal_id>", methods=["DELETE"])
def delete_reading_goal(goal_id):
    goal = db.session.query(Goal).filter(Goal.id==goal_id).first()
    if goal:
        db.session.delete(goal)
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error" : "Failed to delete goal"}), 404)