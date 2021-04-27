from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import BookRecommendation, Book 

recommendation = Blueprint('recommedation', __name__)


@recommendation.route("/api/v1.0/<string:user_id>/recommendations", methods=["GET"])
def get_recommendations_by_user_id(user_id):
    data_to_return = []
    recs = db.session.query(BookRecommendation.id, BookRecommendation.rec_book_id, BookRecommendation.rec_source_id, Book.title, Book.ISBN, Book.author, Book.image_link).join(Book, Book.book_id == BookRecommendation.rec_book_id).filter(BookRecommendation.user_id==user_id).order_by(BookRecommendation.id.desc()).all()

    for rec in recs:
        rec_source_info = db.session.query(Book.title, Book.ISBN).filter(Book.book_id == rec.rec_source_id).first()
        rec_source = {"id" : rec.rec_source_id, "ISBN" : rec_source_info.ISBN, "title" : rec_source_info.title}
        rec_book = {"id" : rec.rec_book_id, "ISBN" : rec.ISBN, "title" : rec.title, "author" : rec.author, "image" : rec.image_link}
        recommendation = {"id" : rec.id, "rec_book" : rec_book, "rec_source" : rec_source}
        data_to_return.append(recommendation)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No recommendations found"}), 404)