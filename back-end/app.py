from config import DB_URI, auth0_access_token
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import *
from sqlalchemy import and_, or_
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
    # update once unique SERIAL has been created for id on this table
    db.session.add(BookRecommendation(id="5", rec_book_id=rec_book_id, rec_source_id=rec_source_id, user_id=user_id))

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
    image = "N/A"
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
    book = db.session.query(Book).filter_by(ISBN=isbn).first()
    book_id = book.book_id

    db.session.add(Reading(user_id=user_id, book_id=book_id, start_date=datetime.date.today()))
    db.session.commit()

    return make_response( jsonify( "Successfully added to bookshelf"), 201 )

@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/wanttoread", methods=["POST"])
def add_want_to_read(isbn, user_id):
    book = db.session.query(Book).filter_by(ISBN=isbn).first()
    book_id = book.book_id

    db.session.add(WantsToRead(user_id=user_id, book_id=book_id, date_added=datetime.date.today()))
    db.session.commit()

    return make_response( jsonify( "Successfully added to bookshelf"), 201 )

@app.route("/api/v1.0/books/<string:isbn>/<string:user_id>/hasread", methods=["POST"])
def add_has_read(isbn, user_id):
    book = db.session.query(Book).filter_by(ISBN=isbn).first()
    book_id = book.book_id

    # update date selection
    db.session.add(HasRead(user_id=user_id, book_id=book_id, start_date=datetime.date.today(), finish_date=datetime.date.today()))
    db.session.commit()

    return make_response( jsonify( "Successfully added to bookshelf"), 201 )

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
            user = {"auth0_id" : result['user_id'], "name" : result['name'], "email" : result['email']}
            data_to_return.append(user)
        except Exception:
            pass

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No results for this query"}), 404)

@app.route("/api/v1.0/search/<string:query>", methods=["GET"])
def search_books(query):
    url = "https://www.googleapis.com/books/v1/volumes?q=" + query +'&startIndex=0&maxResults=40' # add pagination
    r = requests.get(url)
    js = r.json()

    data_to_return = []

    # add what to do if no results i.e. no books in js['items']
    for book in js['items']:
        title = book['volumeInfo']['title']
        try:
            author = book['volumeInfo']['authors'][0]
        except:
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
        except:
            ISBN = "N/A"
        try:
            date = book['volumeInfo']['publishedDate']
        except:
            date = "N/A"
        try:
            imgLink = book['volumeInfo']['imageLinks']['thumbnail']
        except:
            imgLink = ""
            # https://www.rit.edu/nsfadvance/sites/rit.edu.nsfadvance/files/default_images/photo-unavailable.png" # find free-use default 'Cover Unavailable' image to use here
        new_book = {"title" : title, "author" : author, "date" : date, "image" : imgLink, "ISBN" : ISBN}
        if ISBN != "N/A":
            data_to_return.append(new_book)

    if data_to_return:
        return make_response( jsonify(data_to_return), 200 )
    else:
        return make_response( jsonify({"error" : "No results"}), 404 )

@app.route("/api/v1.0/user/<string:user_id>/followedby/<string:follower_id>", methods=["GET"])
def check_following(user_id, follower_id):
    exists = db.session.query(Follow.id).filter_by(user_id=user_id, follower_id=follower_id).scalar() is not None
    
    if exists:
        return make_response(jsonify(exists), 200)
    else:
        return make_response(jsonify(exists), 404)

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
    results = db.session.query(Follow.user_id, Follow.follow_date).filter(Follow.follower_id==user_id)

    data_to_return = []

    for follower in results:
        user = {"user_id" : follower.user_id, "follow_date" : follower.follow_date, "followed_by" : user_id}
        data_to_return.append(user)

    return data_to_return

@app.route("/api/v1.0/user/<string:user_id>/follow/<string:follower_id>", methods=["POST"])
def follow_user(user_id, follower_id):
    if user_id_in_db(user_id) and user_id_in_db(follower_id):
        db.session.add(Follow(user_id=user_id, follower_id=follower_id, follow_date=datetime.date.today()))
        db.session.commit()
        
        return make_response(jsonify({"success" : "Followed user"}), 200)

    else:
        return make_response(jsonify({"error" : "Invalid user"}), 400)

@app.route("/api/v1.0/user/<string:user_id>/unfollow/<string:follower_id>", methods=["DELETE"])
def unfollow_user(user_id, follower_id):
    exists = db.session.query(Follow).filter_by(user_id=user_id, follower_id=follower_id).scalar() is not None

    if exists:
        relationship = db.session.query(Follow).filter_by(user_id=user_id, follower_id=follower_id).first()
        db.session.delete(relationship)
        db.session.commit()

        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error" : "Relationship does not exist"}), 400)

@app.route("/api/v1.0/userprofiletodb/", methods=["POST"])
def send_profile_to_db():

    if "auth0_id" in request.form and "name" in request.form and "nickname" in request.form and "email" in request.form and "image" in request.form:
        auth0_id = request.form["auth0_id"]
        name = request.form["name"]
        nickname = request.form["nickname"]
        email = request.form["email"]
        image = request.form["image"]
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 400)

    
    if not user_auth0_in_db(auth0_id):
        db.session.add(User(auth0_id = auth0_id, full_name=name, nickname=nickname, email=email, image=image))
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
        reviews = db.session.query(Book.title, User.full_name, Review.id, Review.reviewer_id, Review.rating, Review.text, Review.likes).join(Review, Book.book_id==Review.book_id).join(User, User.user_id==Review.reviewer_id).filter(Book.ISBN==ISBN)
        
        for review in reviews:
            rev = {"review_id" : review.id, "book" : review.title, "reviewer_id" : review.reviewer_id, "reviewer_name" : review.full_name, "rating" : review.rating, "text" : review.text, "likes" : review.likes}
            data_to_return.append(rev)

        return make_response( jsonify(data_to_return), 200)
    else:
        return make_response( jsonify({"error" : "Invalid book ID"} ), 404)

@app.route("/api/v1.0/user/<string:user_id>/reviews", methods=["GET"])
def get_all_reviews_by_user(user_id):
    data_to_return = []
    
    if user_id_in_db(user_id):
        reviews = db.session.query(Book.book_id, Book.title, Book.ISBN, Review.id, Review.reviewer_id, Review.rating, Review.text, Review.likes).join(Review, Book.book_id==Review.book_id).filter(Review.reviewer_id==user_id)
    
    else:
        return make_response( jsonify({"error":"Invalid user ID"}), 404)
        
    if reviews is not None:
        for review in reviews:
            rev = {"book_id": review.book_id, "book title" : review.title, "review_id" : review.id, "reviewer_id" : review.reviewer_id, "rating" : review.rating, "text" : review.text, "likes" : review.likes}
            data_to_return.append(rev)
        return make_response( jsonify(data_to_return), 200)

@app.route("/api/v1.0/reviews/<string:review_id>", methods=["GET"])
def get_one_review(review_id):
    review = db.session.query(Review.id, Review.reviewer_id, Review.book_id, Review.rating, Review.text, Review.likes).filter(Review.id==review_id).first()

    if review is not None:
        rev = {"review_id" : review.id, "reviewer_id" : review.reviewer_id, "rating" : review.rating, "text" : review.text, "likes" : review.likes}
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

    if "reviewer_id" in request.form and "book_id" in request.form and "text" in request.form and "rating" in request.form:
        reviewer_id = request.form["reviewer_id"]
        book_id = request.form["book_id"]
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
                rec_book_id = db.session.query(Book.book_id).filter(Book.ISBN==rec).first()
                addRecToDB(rec_book_id, rec_source_id, reviewer_id)
            # print(recs)

    if book is not None:
        db.session.add(Review(reviewer_id=reviewer_id, book_id=book_id, rating=rating, text=text, likes=0))
        # review_id = db.session.query(Review.review_id).filter_by(Review.reviewer_id=reviewer_id, Review.book_id=book_id, Review.rating=rating)
        db.session.commit()
        return make_response( jsonify( "Review successfully added" ), 201 )
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
    deleted_rows = db.session.query(Review).filter(Review.id==review_id).delete()

    if deleted_rows == 1:
        db.session.commit()
        return make_response( jsonify( {} ), 204)
    else:
        return make_response( jsonify( {"error" : "Invalid review ID"} ), 400)

# MESSAGING ENDPOINTS

@app.route("/api/v1.0/user/<string:user_id>/messages/participants", methods=["GET"])
def get_chat_partners(user_id):
    data_to_return = []

    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent).filter(or_(Message.sender_id==user_id, Message.recipient_id==user_id)).all()

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

    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent, User.full_name, User.image).join(User, User.user_id==Message.sender_id).filter(Message.recipient_id==user_id)

    for message in messages:
        msg = {"id" : message.msg_id, "text" : message.msg_text, "sender" : message.sender_id, "sender_name" : message.full_name, "sender_image" : message.image, "recipient" : message.recipient_id, "sent" : message.time_sent }
        data_to_return.append(msg)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No messages found"}), 404)

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


    db.session.add(Message(msg_text=msg_text, sender_id=sender_id, recipient_id=recipient_id, time_sent=time_sent))
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

    activities = db.session.query(Action.description, Activity.date_created, Activity.target_id, Activity.action_id, Activity.object_id, User.user_id, User.full_name, User.image).join(User, Activity.user_id==User.user_id).join(Action, Activity.action_id==Action.id).filter(Activity.user_id.in_([(f['user_id']) for f in followed])).order_by(Activity.date_created.desc()).all()
   
    for activity in activities:
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
        elif activity.action_id == 6:
            target = db.session.query(User.user_id, User.full_name, User.image).filter(User.user_id==activity.target_id).first()
        elif activity.action_id == 7:
            target = db.session.query(Achievement.id, Achievement.name, Achievement.description, Achievement.badge).filter(Achievement.id==activity.target_id).first()

        act = {"user_id" : activity.user_id, "user" : activity.full_name, "user_image" : activity.image, "action" : activity.description, "object_id" : activity.object_id, "target" : target, "date_created" : activity.date_created}
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

# RECOMMENDATION ENDPOINTS

@app.route("/api/v1.0/<string:user_id>/recommendations", methods=["GET"])
def get_recommendations_by_user_id(user_id):
    data_to_return = []
    recs = db.session.query(BookRecommendation.id, BookRecommendation.rec_book_id, BookRecommendation.rec_source_id, Book.title, Book.image_link).join(Book, Book.book_id == BookRecommendation.rec_book_id).filter(BookRecommendation.user_id==user_id).all()

    for rec in recs:
        rec_source_title = db.session.query(Book.title).filter(Book.book_id == rec.rec_source_id).first()
        rec_source = {"id" : rec.rec_source_id, "title" : rec_source_title.title}
        rec_book = {"id" : rec.rec_book_id, "title" : rec.title, "image" : rec.image_link}
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

    goals = db.session.query(Goal.target, Goal.current, Goal.year).filter(Goal.user_id==user_id).all()

    for goal in goals:
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

    db.session.add(Goal(id=4, target=target, current=0, user_id=user_id, year=year))
    db.session.commit()

    return make_response(jsonify({"success:" : "Reading goal successfully set"}), 200)

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
    db.session.delete(goal)

    return make_response(jsonify({}), 204)
    
if __name__ == "__main__":
    app.run(debug=True)