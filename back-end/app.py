from config import DB_URI, auth0_access_token
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import *
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.sql import label
import requests
import book_recommender

import configparser
import datetime

app = Flask(__name__)
CORS(app)

# config = configparser.ConfigParser()
# config.read("config.py")
# DB_URI = config.get("DEFAULT", "DB_URI")

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db = SQLAlchemy(app)

def user_id_in_db(user):
    return db.session.query(User.user_id).filter_by(user_id=user).scalar() is not None

def user_auth0_in_db(user):
    return db.session.query(User.user_id).filter_by(auth0_id=user).scalar() is not None

@app.route("/api/v1.0/userinDB/<string:auth0_id>", methods=["GET"])
def user_auth0_in_db(auth0_id):
    exists = db.session.query(User.user_id).filter_by(auth0_id=auth0_id).scalar() is not None

    if exists:
        return make_response(jsonify(exists), 200)
    else:
        return make_response(jsonify(exists), 404)


def isbn_in_bookRecData(isbn):
    return db.session.query(BookRecDatum).filter_by(isbn=isbn).scalar() is not None

@app.route("/api/v1.0/bookinDB/<string:ISBN>", methods=["GET"])
def book_in_db(ISBN):
    return make_response(jsonify(db.session.query(Book.ISBN).filter_by(ISBN=ISBN).first() is not None), 200) 
    # change to .scalar() instead of first when unique constraint is added to ISBN column  

# add unit test 
def addBookToDB(isbn):
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn
    r = requests.get(url)
    js = r.json()
    
    ISBN = "N/A"
    title = "N/A"
    author = "N/A"
    image = "N/A"
    description = "Description unavailable"
    publish_date = "N/A"
    page_count = 0

    # NEED TO REFACTOR THIS TO REMOVE MULTIPLE TRY/EXCEPT BLOCK
    try:
        title = js['items'][0]['volumeInfo']['title']
    except Exception:
        pass
    try:
        author = js['items'][0]['volumeInfo']['authors'][0]
    except Exception:
        pass
    try:
        image = js['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    except Exception:
        pass
    try:
        publish_date = js['items'][0]['volumeInfo']['publishedDate']
    except Exception:
        pass
    try:
        page_count = js['items'][0]['volumeInfo']['pageCount']
    except Exception:
        pass
    try:
        description = js['items'][0]['volumeInfo']['description']
    except Exception:
        pass
    
    db.session.add(Book(ISBN=isbn, title=title, author=author, publish_date=publish_date, page_count=page_count, image_link=image))
    db.session.commit()

def addRecToDB(rec_book_id, rec_source_id, user_id):
    db.session.add(BookRecommendation(rec_book_id=rec_book_id, rec_source_id=rec_source_id, user_id=user_id))

# BOOK ENDPOINTS

@app.route("/api/v1.0/addbooktodb", methods=["POST"])
def add_book_to_db():
    if "title" in request.form and "author" in request.form and "isbn" in request.form and "publish_date" in request.form and "page_count" in request.form and "image_link" in request.form:
        title = request.form["title"]
        author = request.form["author"]
        isbn = request.form["isbn"]
        publish_date = request.form["publish_date"]
        page_count = request.form["page_count"]
        image = request.form["image_link"]
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 404)
        
    db.session.add(Book(ISBN=isbn, title=title, author=author, publish_date=publish_date, page_count=page_count, image_link=image))
    db.session.commit()

    return make_response(jsonify({}), 200)

@app.route("/api/v1.0/book_id/<isbn>", methods=["GET"])
def get_book_id_by_ISBN(isbn):
    book = db.session.query(Book.book_id).filter(Book.ISBN==isbn).first()

    data_to_return = []

    if book is not None:
        data_to_return.append(book.book_id)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "Book not found in DB"}), 404)

@app.route("/api/v1.0/books/<string:isbn>", methods=["GET"])
def get_one_book(isbn):
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn
    r = requests.get(url)
    js = r.json()

    if not "items" in js:
        return make_response(jsonify({"error" : "No result found"}), 404)
    
    title = "N/A"
    author = "N/A"
    image = "https://img.icons8.com/bubbles/100/000000/no-image.png"
    description = "Description unavailable"
    page_count = 0
    publish_date = "N/A"
    # NEED TO REFACTOR THIS TO REMOVE MULTIPLE TRY/EXCEPT BLOCK

    try:
        title = js['items'][0]['volumeInfo']['title']
    except Exception:
        pass
    try:
        author = js['items'][0]['volumeInfo']['authors'][0]
    except Exception:
        pass
    try:
        image = js['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    except Exception:
        pass
    try:
        description = js['items'][0]['volumeInfo']['description']
    except Exception:
        pass
    try:
        publish_date = js['items'][0]['volumeInfo']['publishedDate']
    except Exception:
        pass
    try:
        page_count = js['items'][0]['volumeInfo']['pageCount']
    except Exception:
        pass
    
    book = {"isbn" : isbn, "title" : title, "author" :  author, "image" : image, "description" : description, "pages" : page_count, "date" : publish_date}

    return make_response(jsonify(book), 200)

@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/currentlyreading", methods=["POST"])
def add_currently_reading(isbn, user_id):
    try:
        book = db.session.query(Book).filter_by(ISBN=isbn).first()
        book_id = book.book_id

        db.session.add(Reading(user_id=user_id, book_id=book_id, start_date=datetime.date.today()))
        db.session.add(Activity(user_id=user_id, action_id=4, object_id=1, date_created=datetime.date.today(), target_id=book_id))
        db.session.commit()

        return make_response( jsonify( {"success" : "Added to bookshelf"}), 201 )
    except Exception:
        return make_response( jsonify( {"error" : "Failed to add to shelf"}), 404)

@app.route("/api/v1.0/user/<string:user_id>/currentlyreading", methods=["GET"])
def get_currently_reading(user_id):
    data_to_return = []
    books = db.session.query(Reading.book_id, Book.ISBN, Book.title, Book.author, Book.image_link).join(Book, Reading.book_id==Book.book_id).filter(Reading.user_id==user_id).all()

    for book in books:
        book_id = book.book_id
        ISBN = book.ISBN
        title = book.title
        author = book.author
        image = book.image_link
        bk = {"book_id" : book_id, "ISBN" : ISBN, "title" : title, "author" : author, "image" : image}
        data_to_return.append(bk)
    
    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No books found"}), 404)


@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/currentlyreading", methods=["DELETE"])
def delete_currently_reading(isbn, user_id):
    try:
        book_id = db.session.query(Book.book_id).filter(Book.ISBN==isbn).first()
        deleted_rows = db.session.query(Reading).filter(Reading.user_id==user_id, Reading.book_id==book_id).delete()
        
        if deleted_rows == 1:
            db.session.commit()
            return make_response( jsonify( {"success" : "Removed from bookshelf"} ), 204)
        else:
            return make_response( jsonify( {"error" : "Failed to remove from bookshelf"} ), 400)
    except Exception:
        return make_response( jsonify( {"error" : "Failed to remove from bookshelf"} ), 400)


        


@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/wanttoread", methods=["POST"])
def add_want_to_read(isbn, user_id):
    try:
        book = db.session.query(Book).filter_by(ISBN=isbn).first()
        book_id = book.book_id

        db.session.add(WantsToRead(user_id=user_id, book_id=book_id, date_added=datetime.date.today()))
        db.session.add(Activity(user_id=user_id, action_id=2, object_id=1, date_created=datetime.date.today(), target_id=book_id))
        db.session.commit()
        
        return make_response( jsonify( {"success" : "Added to bookshelf"}), 201 )
    except Exception:
        return make_response( jsonify( {"error" : "Failed to add to shelf"}), 404)


@app.route("/api/v1.0/user/<string:user_id>/wantstoread", methods=["GET"])
def get_wants_to_read(user_id):
    data_to_return = []
    books = db.session.query(WantsToRead.book_id, Book.ISBN, Book.title, Book.author, Book.image_link).join(Book, WantsToRead.book_id==Book.book_id).filter(WantsToRead.user_id==user_id).all()

    for book in books:
        book_id = book.book_id
        ISBN = book.ISBN
        title = book.title
        author = book.author
        image = book.image_link
        bk = {"book_id" : book_id, "ISBN" : ISBN, "title" : title, "author" : author, "image" : image}
        data_to_return.append(bk)
    
    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No books found"}), 404)
        
@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/wanttoread", methods=["DELETE"])
def delete_wants_to_read(isbn, user_id):
    try:
        book_id = db.session.query(Book.book_id).filter(Book.ISBN==isbn).first()
        deleted_rows = db.session.query(WantsToRead).filter(WantsToRead.user_id==user_id, WantsToRead.book_id==book_id).delete()
        
        if deleted_rows == 1:
            db.session.commit()
            return make_response( jsonify( {"success" : "Removed from bookshelf"} ), 204)
        else:
            return make_response( jsonify( {"error" : "Failed to remove from bookshelf"} ), 400)
    except Exception:
        return make_response( jsonify( {"error" : "Failed to remove from bookshelf"} ), 400)


@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/hasread", methods=["POST"])
def add_has_read(isbn, user_id):
    try:
        book = db.session.query(Book).filter_by(ISBN=isbn).first()
        book_id = book.book_id

        # update date selection
        db.session.add(HasRead(user_id=user_id, book_id=book_id, start_date=datetime.date.today(), finish_date=datetime.date.today()))
        db.session.add(Activity(user_id=user_id, action_id=3, object_id=1, date_created=datetime.date.today(), target_id=book_id))
        goals = db.session.query(Goal).filter(Goal.user_id==user_id).all()

        for goal in goals:
            if str(goal.year) in str(datetime.date.today()):
                goal.current = goal.current + 1

        db.session.commit()
        check_achievement(user_id, 'goal')
        check_achievement(user_id, 'reading')
        return make_response( jsonify( {"success" : "Added to bookshelf"}), 201 )
    except Exception:
        return make_response( jsonify( {"error" : "Failed to add to shelf"}), 404)

@app.route("/api/v1.0/user/<string:user_id>/hasread", methods=["GET"])
def get_has_read(user_id):
    data_to_return = []
    books = db.session.query(HasRead.book_id, Book.ISBN, Book.title, Book.author, Book.image_link).join(Book, HasRead.book_id==Book.book_id).filter(HasRead.user_id==user_id).all()

    for book in books:
        book_id = book.book_id
        ISBN = book.ISBN
        title = book.title
        author = book.author
        image = book.image_link
        bk = {"book_id" : book_id, "ISBN" : ISBN, "title" : title, "author" : author, "image" : image}
        data_to_return.append(bk)
    
    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No books found"}), 404)

@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/hasread", methods=["DELETE"])
def delete_has_read(isbn, user_id):
    try:
        book_id = db.session.query(Book.book_id).filter(Book.ISBN==isbn).first()
        deleted_rows = db.session.query(HasRead).filter(HasRead.user_id==user_id, HasRead.book_id==book_id).delete()
        
        if deleted_rows == 1:
            db.session.commit()
            return make_response( jsonify( {"success" : "Removed from bookshelf"} ), 204)
        else:
            return make_response( jsonify( {"error" : "Failed to remove from bookshelf"} ), 400)
    except Exception:
        return make_response( jsonify( {"error" : "Failed to remove from bookshelf"} ), 400)

# USER ENDPOINTS

@app.route("/api/v1.0/auth0/<auth0_id>", methods=["GET"])
def get_user_id_by_auth0(auth0_id):
    try:
        user_id = get_user_id(auth0_id)
        return make_response(jsonify(user_id), 200)
    except:
        return make_response(jsonify({"error" : "Invalid ID"}), 404)

def get_user_id(auth0_id):
    user = db.session.query(User).filter_by(auth0_id=auth0_id).first()
    return user.user_id

@app.route("/api/v1.0/user/<user_id>", methods=["GET"])
def get_user_details(user_id):
    data_to_return = []

    try:
        result = db.session.query(User).filter_by(user_id=user_id).first()
    except:
        return make_response(jsonify({"error" : "Invalid ID"}), 404)
    
    user = {"user_id" : result.user_id, "auth0_id" : result.auth0_id, "name" : result.full_name, "image" : result.image}
    data_to_return.append(user)

    return make_response(jsonify(data_to_return), 200)

#  SEARCH ENDPOINTS

@app.route("/api/v1.0/search/users/<query>", methods=["GET"])
def search_users(query):
    url = 'https://dev-1spzh9o1.eu.auth0.com/api/v2/users?q=name:*' + query + '*'
    headers = {'authorization' : 'Bearer ' + auth0_access_token}

    req = requests.get(url, headers=headers)
    js = req.json()

    data_to_return = []

    for result in js:
        try:
            auth0_id = result['user_id']
            name = result['name']
            email = result['email']

            db_user = db.session.query(User).filter(User.auth0_id==auth0_id).first()
            user = {"user_id" : db_user.user_id, "auth0_id" : auth0_id, "name" : name, "email" : email, "image" :db_user.image}
            data_to_return.append(user)
        except Exception:
            pass

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No results for this query"}), 404)

@app.route("/api/v1.0/search/books/<string:query>", methods=["GET"])
def search_books(query):

    # default settings
    start_index = 0
    page_size = 30
    language = 'en'
    order = 'relevance'

    if request.args.get('startIndex'):
        start_index = int(request.args.get('startIndex'))

    if request.args.get('lang'):
        language = request.args.get('lang')

    if request.args.get('order'):
        order = request.args.get('order')

    url = "https://www.googleapis.com/books/v1/volumes?q=" + query + '&startIndex=' + str(start_index) + '&maxResults=' + str(page_size) + '&langRestrict=' + language + '&orderBy=' + order
    # '&startIndex=0&maxResults=40' # add pagination
    r = requests.get(url)
    js = r.json()

    data_to_return = []

    # add what to do if no results i.e. no books in js['items']
    try:
        for book in js['items']:
            title = book['volumeInfo']['title']
            try:
                author = book['volumeInfo']['authors'][0]
            except Exception:
                author = "N/A"
            gb_id = book['id']
            try:
                # use ISBN_10 if present, otherwise use ISBN_13 or mark as N/A
                # clean up code here
                if book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_10":
                    ISBN = book['volumeInfo']['industryIdentifiers'][0]['identifier']
                elif book['volumeInfo']['industryIdentifiers'][1]['type'] and book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_10":
                    ISBN = book['volumeInfo']['industryIdentifiers'][1]['identifier']
                elif book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_13":
                    ISBN = book['volumeInfo']['industryIdentifiers'][0]['identifier']
                else:
                    ISBN = "N/A"
            except Exception:
                ISBN = "N/A"
            try:
                date = book['volumeInfo']['publishedDate']
            except Exception:
                date = "N/A"
            try:
                imgLink = book['volumeInfo']['imageLinks']['thumbnail']
            except Exception:
                # imgLink = "https://img.icons8.com/fluent/96/000000/no-image.png"
                imgLink = "https://img.icons8.com/bubbles/100/000000/no-image.png"
                # https://www.rit.edu/nsfadvance/sites/rit.edu.nsfadvance/files/default_images/photo-unavailable.png" # find free-use default 'Cover Unavailable' image to use here
            new_book = {"title" : title, "author" : author, "date" : date, "image" : imgLink, "ISBN" : ISBN}
            if ISBN != "N/A":
                data_to_return.append(new_book)

        if data_to_return:
            return make_response( jsonify(data_to_return), 200 )
        else:
            return make_response( jsonify({"error" : "No results"}), 404 )
    except Exception:
         return make_response( jsonify({"error" : "No results"}), 404 )

        
# FOLLOW ENDPOINTS

@app.route("/api/v1.0/user/<string:user_id>/followedby/<string:follower_id>", methods=["GET"])
def check_following(user_id, follower_id):
    exists = db.session.query(Follow.id).filter_by(user_id=user_id, follower_id=follower_id).scalar() is not None
    
    return make_response(jsonify(exists), 200)

@app.route("/api/v1.0/user/<string:user_id>/followers", methods=["GET"])
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

@app.route("/api/v1.0/user/<string:user_id>/followed", methods=["GET"])
def get_followed(user_id):
    data_to_return = get_followed_users(user_id)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No followed users"}), 404)


@app.route("/api/v1.0/user/<string:user_id>/follow/<string:follower_id>", methods=["POST"])
def follow_user(user_id, follower_id):
    if user_id_in_db(user_id) and user_id_in_db(follower_id):
        exists = db.session.query(Follow).filter(Follow.user_id==user_id, Follow.follower_id==follower_id).first() is not None

        if not exists:
            db.session.add(Follow(user_id=user_id, follower_id=follower_id, follow_date=datetime.date.today()))
            follow_id = db.session.query(Follow.id).filter_by(user_id=user_id, follower_id=follower_id).first()
            db.session.add(Activity(user_id=follower_id, action_id=6, object_id=5, date_created=datetime.date.today(), target_id=user_id))
            db.session.commit()
        
            return make_response(jsonify({"success" : "Followed user", "data" : follow_id}), 200)
        else:
            return make_response(jsonify({"error" : "Follow relationship already exists"}), 400)


    else:
        return make_response(jsonify({"error" : "Invalid user"}), 400)

@app.route("/api/v1.0/user/<string:user_id>/unfollow/<string:follower_id>", methods=["DELETE"])
def unfollow_user(user_id, follower_id):
    exists = db.session.query(Follow).filter_by(user_id=user_id, follower_id=follower_id).scalar() is not None

    if exists:
        relationship = db.session.query(Follow).filter_by(user_id=user_id, follower_id=follower_id).first()
        db.session.delete(relationship)
        db.session.commit()

        return make_response(jsonify({"success" : "Unfollowed user"}), 204)
    else:
        return make_response(jsonify({"error" : "Relationship does not exist"}), 400)

# @app.route("/api/v1.0/unfollow/<string:follow_id>", methods=["DELETE"])
# def unfollow_user(follow_id):
#     exists = db.session.query(Follow).filter_by(follow_id=follow_id).scalar() is not None

#     if exists:
#         relationship = db.session.query(Follow).filter_by(follow_id=follow_id)).first()
#         db.session.delete(relationship)
#         db.session.commit()

#         return make_response(jsonify({}), 204)
#     else:
#         return make_response(jsonify({"error" : "Relationship does not exist"}), 400)

@app.route("/api/v1.0/userprofiletodb", methods=["POST"])
def send_profile_to_db():

    if "auth0_id" in request.form and "name" in request.form and "image" in request.form:
        auth0_id = request.form["auth0_id"]
        name = request.form["name"]
        nickname = "nickname"
        email = "email"
        image = request.form["image"]
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 400)

    
    if not user_auth0_in_db(auth0_id):
        db.session.add(User(auth0_id = auth0_id, full_name=name, nickname=nickname, email=email, image=image))
        # db.session.add(User(auth0_id = auth0_id, full_name=name, image=image))
        db.session.commit()
        
        return make_response(jsonify("User added to DB"), 200)
    else: 
        return make_response(jsonify({"error" : "User already exists in DB"}), 400)

# REVIEW ENDPOINTS

@app.route("/api/v1.0/books/<string:ISBN>/reviews", methods=["GET"])
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

@app.route("/api/v1.0/user/<string:user_id>/reviews", methods=["GET"])
def get_all_reviews_by_user(user_id):
    data_to_return = []
    
    if user_id_in_db(user_id):
        reviews = db.session.query(Book.book_id, Book.title, Book.ISBN, Review.id, Review.reviewer_id, Review.rating, Review.text).join(Review, Book.book_id==Review.book_id).filter(Review.reviewer_id==user_id)
    
    else:
        return make_response( jsonify({"error":"Invalid user ID"}), 404)
        
    if reviews is not None:
        for review in reviews:
            rev = {"book_id": review.book_id, "book_ISBN" : review.ISBN, "book title" : review.title, "review_id" : review.id, "reviewer_id" : review.reviewer_id, "rating" : review.rating, "text" : review.text}
            data_to_return.append(rev)
        return make_response( jsonify(data_to_return), 200)

@app.route("/api/v1.0/reviews/<string:review_id>", methods=["GET"])
def get_one_review(review_id):
    review = db.session.query(Review.id, Review.reviewer_id, Review.book_id, Review.rating, Review.text).filter(Review.id==review_id).first()
    num_likes = get_like_count(2, review_id)

    if review is not None:
        rev = {"review_id" : review.id, "reviewer_id" : review.reviewer_id, "rating" : review.rating, "text" : review.text, "likes" : num_likes}
        return make_response(jsonify(rev), 200)
    else:
        return make_response(jsonify({"error" : "Invalid review ID"}), 404)

@app.route("/api/v1.0/books/<string:ISBN>/reviews", methods=["POST"])
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

        db.session.add(Activity(user_id=reviewer_id, action_id=1, object_id=1, date_created=datetime.date.today(), target_id=book_id))
        check_achievement(reviewer_id, 'review')
        # review_id = db.session.query(Review.review_id).filter_by(Review.reviewer_id=reviewer_id, Review.book_id=book_id, Review.rating=rating)
        db.session.commit()
        return make_response( jsonify( {"review" : review_id} ), 201 )
    else:
        return make_response( jsonify({"error" : "Failed to add review"}), 404)

@app.route("/api/v1.0/reviews/<string:review_id>", methods=["PUT"])
def edit_review(review_id):

    if "text" in request.form and "rating" in request.form:
        text = request.form["text"]
        rating = request.form["rating"]
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 404)

    db.session.query(Review).filter(Review.id==review_id).update({'text' : text, 'rating' : rating})
    db.session.commit()

    return make_response(jsonify("Successfully edited review"), 200)

@app.route("/api/v1.0/reviews/<string:review_id>", methods=["DELETE"])
def delete_review(review_id):
    book_id = db.session.query(Review.book_id).filter(Review.id==review_id).first()
    deleted_rows = db.session.query(Review).filter(Review.id==review_id).delete()

    if deleted_rows == 1:
        db.session.query(Activity).filter(Activity.object_id==1, Activity.target_id==book_id).delete()
        db.session.commit()
        return make_response( jsonify( {"success" : "Review deleted"} ), 204)
    else:
        return make_response( jsonify( {"error" : "Invalid review ID"} ), 400)

# MESSAGING ENDPOINTS

@app.route("/api/v1.0/user/<string:user_id>/messages/participants", methods=["GET"])
def get_chat_partners(user_id):
    data_to_return = []

    # gets chat partners by most recent 
    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent).filter(or_(Message.sender_id==user_id, Message.recipient_id==user_id)).order_by(Message.time_sent.desc()).all()

    for message in messages:
        if message.sender_id == int(user_id):
            user = db.session.query(User.full_name, User.image).filter(User.user_id==message.recipient_id).first()
            partner = {"id" : message.recipient_id, "name" : user.full_name, "image" : user.image }
        elif message.recipient_id == int(user_id):
            user = db.session.query(User.full_name, User.image).filter(User.user_id==message.sender_id).first()
            partner = {"id" : message.sender_id, "name" : user.full_name, "image" : user.image }
        if partner not in data_to_return:
            data_to_return.append(partner)
   
    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No chats found"}), 404)

@app.route("/api/v1.0/user/<string:user_id>/messages/", methods=["GET"])
def get_all_messages_by_user_id(user_id):
    data_to_return = []

    if not user_id_in_db(user_id):
        return make_response(jsonify({"error" : "Invalid user ID"}), 404)

    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent).filter(or_(Message.sender_id==user_id, Message.recipient_id==user_id)).all()

    for message in messages:
        msg = {"id" : message.msg_id, "text" : message.msg_text, "sender" : message.sender_id, "recipient" : message.recipient_id, "sent" : message.time_sent }
        data_to_return.append(msg)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No messages found"}), 404)

@app.route("/api/v1.0/user/<string:user_id>/messages/received", methods=["GET"])
def get_all_received_messages_by_user_id(user_id):
    data_to_return = []

    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent, Message.read, User.full_name, User.image).join(User, User.user_id==Message.sender_id).filter(Message.recipient_id==user_id)

    for message in messages:
        msg = db.session.query(Message).filter(Message.msg_id==message.msg_id).first()
        msg.read = True
        # print(msg.read)
        # mark_as_read(message.msg_id)
        db.session.commit()
        print(message.read)
        msg = {"id" : message.msg_id, "text" : message.msg_text, "sender" : message.sender_id, "sender_name" : message.full_name, "sender_image" : message.image, "recipient" : message.recipient_id, "sent" : message.time_sent }
        data_to_return.append(msg)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No messages found"}), 404)

def mark_as_read(msg_id):
    message = db.session.query(Message).filter(Message.msg_id==msg_id).first()
    message.read = True
    # print(message.read)
    # db.session.commit()

@app.route("/api/v1.0/user/<string:user_id>/messages/unread", methods=["GET"])
def get_unread_count(user_id):
    data_to_return = []
    num_unread = 0
    messages = db.session.query(Message).filter(Message.recipient_id==user_id).all()

    for message in messages:
        if message.read == False:
            num_unread = num_unread + 1
    
    data_to_return.append(num_unread)
    
    # return make_response(jsonify({"num_unread" : num_unread}), 200)
    return make_response(jsonify(data_to_return), 200)



@app.route("/api/v1.0/user/<string:user_id>/messages/sent", methods=["GET"])
def get_all_sent_messages_by_user_id(user_id):
    data_to_return = []

    if not user_id_in_db(user_id):
        return make_response(jsonify({"error" : "Invalid user ID"}), 404)

    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent).filter(Message.sender_id==user_id)

    for message in messages:
        msg = {"id" : message.msg_id, "text" : message.msg_text, "sender" : message.sender_id, "recipient" : message.recipient_id, "sent" : message.time_sent }
        data_to_return.append(msg)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No messages found"}), 404)

@app.route("/api/v1.0/messages/", methods=["GET"])
def get_all_messages_between_two_users():
    user_A = request.args.get('userA')
    user_B = request.args.get('userB')

    data_to_return = []

    messages = db.session.query(Message).filter(or_(and_(Message.sender_id==user_A, Message.recipient_id==user_B), and_(Message.sender_id==user_B, Message.recipient_id==user_A)))

    for message in messages:
        sender = db.session.query(User.full_name, User.image).filter(User.user_id==message.sender_id).first()
        msg = {"id" : message.msg_id, "text" : message.msg_text, "sender" : message.sender_id, "sender_name" : sender.full_name, "sender_image" : sender.image, "recipient" : message.recipient_id, "sent" : message.time_sent }
        data_to_return.append(msg)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No messages found"}), 404)


@app.route("/api/v1.0/user/<string:user_id>/contact", methods=["POST"])
def send_message(user_id):

    if not user_id_in_db(user_id):
        return make_response(jsonify({"error" : "Invalid user ID"}), 400)

    if "msg_text" in request.form and "sender_id" in request.form:
        msg_text = request.form["msg_text"]
        sender_id = request.form["sender_id"]
        recipient_id = user_id
        time_sent = datetime.datetime.now()
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 400)


    # db.session.add(Message(msg_text=msg_text, sender_id=sender_id, recipient_id=recipient_id, time_sent=time_sent))
    db.session.add(Message(msg_text=msg_text, sender_id=sender_id, recipient_id=recipient_id, time_sent=time_sent, read=False))
    db.session.commit()

    return make_response(jsonify({"success" : "Message sent successfully"}), 200)

# ACTIVITY ENDPOINTS

@app.route("/api/v1.0/activity/<string:user_id>", methods=["GET"])
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

@app.route("/api/v1.0/activity/followedby/<string:user_id>", methods=["GET"])
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
            if activity.object_id == 7:
                activity_user = db.session.query(Activity.user_id).filter(Activity.id==activity.target_id).first()
                target = db.session.query(User.full_name, User.user_id, User.image).filter(User.user_id==activity_user).first()
        elif activity.action_id == 6:
            target = db.session.query(User.user_id, User.full_name, User.image).filter(User.user_id==activity.target_id).first()
        elif activity.action_id == 7:
            target = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge).filter(Achievement.id==activity.target_id).first()

        act = {"activity_id" : activity.id, "user_id" : activity.user_id, "user" : activity.full_name, "user_image" : activity.image, "action" : activity.description, "object_id" : activity.object_id, "target" : target, "date_created" : activity.date_created, "likes" : likes}
        data_to_return.append(act)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No activities found"}), 404)

# ACHIEVEMENT ENDPOINTS

@app.route("/api/v1.0/achievements", methods=["GET"])
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

@app.route("/api/v1.0/achievements/<id>", methods=["GET"])
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



@app.route("/api/v1.0/user/<string:user_id>/achievements", methods=["GET"])
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


# RECOMMENDATION ENDPOINTS

@app.route("/api/v1.0/<string:user_id>/recommendations", methods=["GET"])
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

# GOAL ENDPOINTS
@app.route("/api/v1.0/<string:user_id>/goals", methods=["GET"])
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

@app.route("/api/v1.0/goals/new", methods=["POST"])
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

@app.route("/api/v1.0/goals/<string:goal_id>", methods=["PUT"])
def edit_reading_goal(goal_id):
    if "target" in request.form:
        new_target = request.form["target"]

    goal = db.session.query(Goal).filter(Goal.id==goal_id).first()
    goal.target = new_target
    db.session.commit()

    return make_response(jsonify({"success:" : "Reading goal successfully edited"}), 200)
    

@app.route("/api/v1.0/goals/<string:goal_id>", methods=["DELETE"])
def delete_reading_goal(goal_id):
    goal = db.session.query(Goal).filter(Goal.id==goal_id).first()
    if goal:
        db.session.delete(goal)
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error" : "Failed to delete goal"}), 404)

# GROUP ENDPOINTS

@app.route("/api/v1.0/groups", methods=["GET"])
def get_all_groups():
    data_to_return = []
    groups = db.session.query(Group).all()

    for group in groups:
        gr = {"id" : group.id, "name" : group.name, "description" : group.description}
        data_to_return.append(gr)
    
    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No groups found"}), 404)

@app.route("/api/v1.0/user/<string:user_id>/groups", methods=["GET"])
def get_groups_by_user(user_id):
    data_to_return = []
    groups = db.session.query(Group).join(UserGroup, Group.id==UserGroup.group_id).filter(UserGroup.user_id==user_id).all()

    for group in groups:
        gr = {"id" : group.id, "name" : group.name, "description" : group.description}
        data_to_return.append(gr)
    
    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No groups found"}), 404)

@app.route("/api/v1.0/groups/new", methods=["POST"])
def create_new_group():
    if "name" in request.form and "description" in request.form and "founder_id" in request.form:
        name = request.form["name"],
        description = request.form["description"]
        founder_id = request.form["founder_id"]

        db.session.add(Group(name=name, description=description, founder_id=founder_id))
        group_id = db.session.query(Group.id).filter(Group.name==name, Group.description==description, Group.founder_id==founder_id).first()
        check_achievement(founder_id, "group")
        db.session.commit()

        return make_response(jsonify({"success:" : "Group created", "data" : group_id}), 200)
    else:
        return make_response(jsonify({"error:" : "Failed to create group"}), 404)


# probably won't implement this
@app.route("/api/v1.0/groups/edit", methods=["PUT"])
def edit_group():
    if "group_id" in request.form:
        group_id = request.form["group_id"]
        group = db.session.query(Group).filter(Group.id==group_id).first()

        if "name" in request.form:
            group.name = request.form["name"]
        if "description" in request.form:
            group.description = request.form[""]

        db.session.commit()

    return make_response(jsonify({"success:" : "Group edited"}), 200)

# probably won't implement this
@app.route("/api/v1.0/groups/delete", methods=["DELETE"])
def delete_group():
    if "group_id" in request.form:
        group_id = request.form["group_id"]

    group = db.session.query(Group).filter(Group.id==group_id).first()
    db.session.delete(group)
    db.session.commit()

    return make_response(jsonify({}), 204)

@app.route("/api/v1.0/groups/<string:group_id>", methods=["GET"])
def get_group(group_id):
    data_to_return = []

    try:
        group = db.session.query(Group).filter(Group.id==group_id).first()
        gr = {"id" : group.id, "name" : group.name, "description" : group.description}

        data_to_return.append(gr)

        if data_to_return:
            return make_response(jsonify(data_to_return), 200)
        else:
            return make_response(jsonify({"error" : "No group information available"}), 404)
    except Exception:
        return make_response(jsonify({"error" : "No group information available"}), 404)


@app.route("/api/v1.0/groups/<string:group_id>/members", methods=["GET"])
def get_group_members(group_id):
    data_to_return = []
    members = db.session.query(UserGroup.user_id, User.full_name, User.image).join(User, UserGroup.user_id==User.user_id).filter(UserGroup.group_id==group_id).all()

    for member in members:
        memb = {"user_id" : member.user_id, "name" : member.full_name, "image" : member.image}
        data_to_return.append(memb)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No members found"}), 404)

@app.route("/api/v1.0/groups/<string:group_id>/join", methods=["POST"])
def join_group(group_id):
    if "user_id" in request.form:
        user_id = request.form["user_id"]

    try:
        db.session.add(UserGroup(user_id=user_id, group_id=group_id, join_date=datetime.date.today()))
        db.session.commit()

        return make_response(jsonify({"success:" : "Group joined"}), 200)
    except Exception:
        return make_response(jsonify({"error:" : "Failed to join group"}), 404)

# probably won't implement this
@app.route("/api/v1.0/groups/<string:group_id>/leave", methods=["DELETE"])
def leave_group(group_id):
    if "user_id" in request.form:
        user_id = request.form["user_id"]

    entry = db.session.query(UserGroup).filter(UserGroup.group_id==group_id, UserGroup.user_id==user_id).first()
    db.session.delete(entry)
    db.session.commit()

    return make_response(jsonify({}), 204)

@app.route("/api/v1.0/groups/<string:group_id>/posts", methods=["GET"])
def get_all_group_posts(group_id):
    data_to_return = []
    posts = db.session.query(Post.id, Post.author_id, Post.text, Post.title, User.full_name, User.image).join(User, Post.author_id==User.user_id).filter(Post.group_id==group_id).all()

    for post in posts:
        p = {"id" : post.id, "author_id" : post.author_id, "author_name" : post.full_name, "author_image" : post.image, "text" : post.text, "title" : post.title}
        data_to_return.append(p)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No posts found"}), 404)

@app.route("/api/v1.0/groups/<string:group_id>/posts", methods=["POST"])
def add_group_post(group_id):
    if "user_id" in request.form and "text" in request.form and "title" in request.form:
        user_id = request.form["user_id"]
        text = request.form["text"]
        title = request.form["title"]

        db.session.add(Post(group_id=group_id, author_id=user_id, text=text, title=title))
        db.session.commit()

        return make_response(jsonify({"success:" : "Posted"}), 200)
    else:
        return make_response(jsonify({"error:" : "Failed to add post"}), 404)


# probably won't implement this
@app.route("/api/v1.0/groups/posts/<string:post_id>", methods=["PUT"])
def edit_group_post(post_id):
    post = db.session.query(Post).filter(Post.id==post_id).first()
    
    if "text" in request.form:
        post.text = request.form["text"]
    if "title" in request.form:
        post.title = request.form["title"]

    db.session.commit()

    # change so it only returns this if successful
    return make_response(jsonify({"success:" : "Post edited"}), 200)

# probably won't implement this
@app.route("/api/v1.0/groups/posts", methods=["DELETE"])
def delete_group_post(): 
    if "post_id" in request.form:
        post_id = request.form["post_id"]
        post = db.session.query(Post).filter(Post.id==post_id).first()
        db.session.delete(post)
    
    db.session.commit()
    
    return make_response(jsonify({}), 204)

# COMMENT/REPLIES ENDPOINTS
@app.route("/api/v1.0/comments/<string:object_id>/<string:target_id>", methods=["GET"])
def get_comments(object_id, target_id):
    data_to_return = []
    comments = db.session.query(Comment.commenter_id, Comment.text, Comment.time_submitted, User.full_name).join(User, User.user_id==Comment.commenter_id).filter(Comment.object_id==object_id, Comment.target_id==target_id).all()
         
    for comment in comments:
        com = {"commenter_id" : comment.commenter_id, "commenter_name" : comment.full_name, "text" : comment.text, "time" : comment.time_submitted}
        data_to_return.append(com)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
        
@app.route("/api/v1.0/comments/<string:object_id>/<string:target_id>", methods=["POST"])
def add_comment(object_id, target_id):
    if "commenter_id" in request.form and "text" in request.form:
        commenter_id = request.form["commenter_id"]
        text = request.form["text"]
        db.session.add(Comment(comment_id=2, object_id=object_id, commenter_id=commenter_id, text=text, time_submitted=datetime.date.today(), target_id=target_id))
        db.session.commit()

    return make_response(jsonify({"success:" : "Comment posted"}), 200)

# STATS ENDPOINTS

@app.route("/api/v1.0/<string:user_id>/stats/mostread", methods=["GET"])
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

@app.route("/api/v1.0/<string:user_id>/stats/totalpages", methods=["GET"])
def get_total_pages_read(user_id):
    data_to_return = []

    num_pages = db.session.query(label('num_pages', func.sum(Book.page_count))).join(HasRead, HasRead.book_id==Book.book_id).filter(HasRead.user_id==user_id).all()
    
    return make_response(jsonify(num_pages), 200)
    # else:
    #     return make_response(jsonify({"error" : "No page data available"}), 404)

   
# LIKES ENDPOINTS
@app.route("/api/v1.0/<string:user_id>/likes", methods=["POST"])
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

@app.route("/api/v1.0/likes", methods=["GET"])
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


if __name__ == "__main__":
    app.run(debug=True)