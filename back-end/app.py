from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import configparser

app = Flask(__name__)
CORS(app)

config = configparser.ConfigParser()
config.read("config.py")
DB_URI = config.get("DEFAULT", "DB_URI")

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db = SQLAlchemy(app)

def user_id_in_db(user):
    return db.session.query(User.user_id).filter_by(user_id=user).scalar() is not None

def user_auth0_in_db(user):
    return db.session.query(User.user_id).filter_by(auth0_id=user).scalar() is not None

# add unit test 
def addBookToDB(isbn):
    url = "https://www.googleapis.com/books/v1/volumes?q=" + isbn
    r = requests.get(url)
    js = r.json()

    entry = {"title" : js['items'][0]['volumeInfo']['title'], "author" :  js['items'][0]['volumeInfo']['authors'][0], "image" : js['items'][0]['volumeInfo']['imageLinks']['thumbnail'], "description" : js['items'][0]['volumeInfo']['description'], "ISBN" : js['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier'], "publish_date" : js['items'][0]['volumeInfo']['publishedDate'], "page_count" : js['items'][0]['volumeInfo']['pageCount']}
    
    db.session.add(Book(ISBN=entry['ISBN'], title=entry['title'], author=entry['author'], publish_date=entry['publish_date'], page_count=entry['page_count'], image_link=entry['image']))
    db.session.commit()

# User endpoints
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
    
    user = {"user_id" : result.user_id, "auth0_id" : result.auth0_id, "name" : result.full_name}
    data_to_return.append(user)

    return make_response(jsonify(data), 200)

@app.route("/api/v1.0/search/users/<query>", methods=["GET"])
def search_users(query):
    url = 'https://dev-1spzh9o1.eu.auth0.com/api/v2/users?q=name:*' + query + '*'
    headers = {'authorization' : 'Bearer ' + access_token}

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

@app.route("/api/v1.0/userprofiletodb/<auth0_id>/<name>/<email>", methods=["POST"])
def send_profile_to_db(auth0_id, name, email):
    
    if not user_auth0_in_db(auth0_id):
        db.session.add(User(auth0_id = auth0_id, full_name=name, nickname='km', email=email))
        db.session.commit()
        
        return make_response(jsonify("User added to DB"), 200)
    else: 
        return make_response(jsonify({"error" : "User already exists in DB"}), 400)

# Review endpoints

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

    exists = db.session.query(Book.ISBN).filter_by(ISBN=ISBN).scalar() is not None

    if not exists:
        addBookToDB(ISBN)

    book = db.session.query(Book).filter(Book.ISBN==ISBN).first()

    if "id" in request.form and "reviewer_id" in request.form and "book_id" in request.form and "text" in request.form and "rating" in request.form:
        new_review = {
        "id" : request.form["id"],
        "reviewer_id" : request.form["reviewer_id"],
        "book_id" : request.form["book_id"],
        "text" : request.form["text"],
        "rating" : request.form["rating"]
        }
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 400)

    if book is not None:
        db.session.add(Review(id=new_review['id'], reviewer_id=new_review['reviewer_id'], book_id=new_review['book_id'], rating=new_review['rating'], text=new_review['text'], likes=0))
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

# Messaging endpoints

@app.route("/api/v1.0/user/<string:user_id>/messages/received", methods=["GET"])
def get_all_received_messages_by_user_id(user_id):
    data_to_return = []

    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent).filter(Message.recipient_id==user_id)

    for message in messages:
        msg = {"id" : message.msg_id, "text" : message.msg_text, "sender" : message.sender_id, "recipient" : message.recipient_id, "sent" : message.time_sent }
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


@app.route("/api/v1.0/user/<string:user_id>/contact", methods=["POST"])
def send_message(user_id):

    if not user_id_in_db(user_id):
        return make_response(jsonify({"error" : "Invalid user ID"}), 400)

    if "msg_text" in request.form and "sender_id" in request.form and "time_sent" in request.form:
        msg_text = request.form["msg_text"]
        sender_id = request.form["sender_id"]
        recipient_id = user_id
        time_sent = request.form["time_sent"]
    else:
        return make_response(jsonify({"error" : "Missing form data"}), 400)


    db.session.add(Message(msg_text=msg_text, sender_id=sender_id, recipient_id=recipient_id, time_sent=time_sent))
    db.session.commit()

    return make_response(jsonify({"success" : "Message sent successfully"}), 200)



if __name__ == "__main__":
    app.run(debug=True)