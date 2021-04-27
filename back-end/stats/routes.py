from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import Book, HasRead
from sqlalchemy.sql import label, func, desc

stats = Blueprint('stats', __name__)

@stats.route("/api/v1.0/<string:user_id>/stats/mostread", methods=["GET"])
def get_most_read_author(user_id):
    data_to_return =[]
    authors = db.session.query(func.count(Book.author).label('count'), Book.author).join(HasRead, HasRead.book_id==Book.book_id).filter(HasRead.user_id==user_id).group_by(Book.author).order_by(desc('count')).limit(3).all()

    for author in authors:
        entry = {"author" : author[1], "num_books" : author[0]}
        data_to_return.append(entry)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No author data available for this user"}), 404)

@stats.route("/api/v1.0/<string:user_id>/stats/totalpages", methods=["GET"])
def get_total_pages_read(user_id):
    data_to_return = []

    num_pages = db.session.query(label('num_pages', func.sum(Book.page_count))).join(HasRead, HasRead.book_id==Book.book_id).filter(HasRead.user_id==user_id).all()
    
    return make_response(jsonify(num_pages), 200)