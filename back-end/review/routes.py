from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import Book, User, Review, Activity
from achievement.routes import check_achievement
from activity.routes import get_like_count
from user.routes import user_id_in_db
import datetime
import book_recommender
from book.routes import addBookToDB, addRecToDB


review = Blueprint('review', __name__)

@review.route("/api/v1.0/books/<string:ISBN>/reviews", methods=["GET"])
def get_all_reviews(ISBN):
    data_to_return = []

    book = db.session.query(Book).filter(Book.ISBN==ISBN).first()

    if book is not None:
        reviews = db.session.query(Book.title, User.full_name, User.image, Review.id, Review.reviewer_id, Review.rating, Review.text).join(Review, Book.book_id==Review.book_id).join(User, User.user_id==Review.reviewer_id).filter(Book.ISBN==ISBN)
        
        for review in reviews:
            likes = get_like_count(2, review.id)
            rev = {"review_id" : review.id, "book" : review.title, "reviewer_id" : review.reviewer_id, "reviewer_name" : review.full_name, "reviewer_image" : review.image, "rating" : review.rating, "text" : review.text, "likes" : likes}
            data_to_return.append(rev)

        return make_response( jsonify(data_to_return), 200)
    else:
        return make_response( jsonify({"error" : "Invalid book ID"} ), 404)

@review.route("/api/v1.0/user/<string:user_id>/reviews", methods=["GET"])
def get_all_reviews_by_user(user_id):
    data_to_return = []
    
    if user_id_in_db(user_id):
        reviews = db.session.query(Book.book_id, Book.title, Book.ISBN, Book.author, Review.id, Review.reviewer_id, Review.rating, Review.text).join(Review, Book.book_id==Review.book_id).filter(Review.reviewer_id==user_id)
    
    else:
        return make_response( jsonify({"error":"Invalid user ID"}), 404)
        
    if reviews is not None:
        for review in reviews:
            rev = {"book_id": review.book_id, "book_ISBN" : review.ISBN, "book_title" : review.title, "book_author" : review.author, "review_id" : review.id, "reviewer_id" : review.reviewer_id, "rating" : review.rating, "text" : review.text}
            data_to_return.append(rev)
        return make_response( jsonify(data_to_return), 200)

@review.route("/api/v1.0/reviews/<string:review_id>", methods=["GET"])
def get_one_review(review_id):
    review = db.session.query(Review.id, Review.reviewer_id, Review.book_id, Review.rating, Review.text).filter(Review.id==review_id).first()
    num_likes = get_like_count(2, review_id)

    if review is not None:
        rev = {"review_id" : review.id, "reviewer_id" : review.reviewer_id, "rating" : review.rating, "text" : review.text, "likes" : num_likes}
        return make_response(jsonify(rev), 200)
    else:
        return make_response(jsonify({"error" : "Invalid review ID"}), 404)

@review.route("/api/v1.0/books/<string:ISBN>/reviews", methods=["POST"])
def add_review(ISBN):
    data_to_return = []

    # exists = db.session.query(Book.ISBN).filter_by(ISBN=ISBN).scalar() is not None
    exists = db.session.query(Book.ISBN).filter_by(ISBN=ISBN).first() is not None

    if not exists:
        addBookToDB(ISBN)

    book = db.session.query(Book).filter(Book.ISBN==ISBN).first()

    if "reviewer_id" in request.form and "text" in request.form and "rating" in request.form:
        reviewer_id = request.form["reviewer_id"]
        book_id = book.book_id
        text = request.form["text"]
        rating = request.form["rating"]
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 400)

    if rating in ("3.5", "4", "4.5", "5"):
        try:
            recs = book_recommender.recommend(ISBN)
        except Exception:
            pass
        else:
            rec_source_id = db.session.query(Book.book_id).filter(Book.ISBN==ISBN).first()
            for rec in recs:
                addBookToDB(rec)
                rec_book = db.session.query(Book).filter(Book.ISBN==rec).first()
                rec_book_id = rec_book.book_id
                if not rec_book.title == "N/A":
                    addRecToDB(rec_book_id, rec_source_id, reviewer_id)
                # rec_book_id = db.session.query(Book.book_id).filter(Book.ISBN==rec).first()
                # addRecToDB(rec_book_id, rec_source_id, reviewer_id)
            # print(recs)

    if book is not None:
        db.session.add(Review(reviewer_id=reviewer_id, book_id=book_id, rating=rating, text=text))
        review_id = db.session.query(Review.id).filter(Review.reviewer_id==reviewer_id, Review.book_id==book_id, Review.rating==rating, Review.text==text).first()

        db.session.add(Activity(user_id=reviewer_id, action_id=1, object_id=1, date_created=datetime.datetime.now(), target_id=book_id))
        check_achievement(reviewer_id, 'review')
        # review_id = db.session.query(Review.review_id).filter_by(Review.reviewer_id=reviewer_id, Review.book_id=book_id, Review.rating=rating)
        db.session.commit()
        return make_response( jsonify( {"review" : review_id} ), 201 )
    else:
        return make_response( jsonify({"error" : "Failed to add review"}), 404)

@review.route("/api/v1.0/reviews/<string:review_id>", methods=["PUT"])
def edit_review(review_id):

    if "text" in request.form and "rating" in request.form:
        text = request.form["text"]
        rating = request.form["rating"]
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 404)

    db.session.query(Review).filter(Review.id==review_id).update({'text' : text, 'rating' : rating})
    db.session.commit()

    return make_response(jsonify("Successfully edited review"), 200)

@review.route("/api/v1.0/reviews/<string:review_id>", methods=["DELETE"])
def delete_review(review_id):
    book_id = db.session.query(Review.book_id).filter(Review.id==review_id).first()
    deleted_rows = db.session.query(Review).filter(Review.id==review_id).delete()

    if deleted_rows == 1:
        db.session.query(Activity).filter(Activity.object_id==1, Activity.target_id==book_id).delete()
        db.session.commit()
        return make_response( jsonify( {"success" : "Review deleted"} ), 204)
    else:
        return make_response( jsonify( {"error" : "Invalid review ID"} ), 400)
