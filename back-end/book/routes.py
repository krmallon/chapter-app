from flask import Blueprint, make_response, jsonify, request
from models import Book, Reading, WantsToRead, HasRead, Activity, BookRecommendation, Goal
from extensions import db
from achievement.routes import check_achievement
import requests
import datetime

book = Blueprint('book', __name__)

def isbn_in_bookRecData(isbn):
    return db.session.query(BookRecDatum).filter_by(isbn=isbn).scalar() is not None

@book.route("/api/v1.0/bookinDB/<string:ISBN>", methods=["GET"])
def book_in_db(ISBN):
    return make_response(jsonify(db.session.query(Book.ISBN).filter_by(ISBN=ISBN).first() is not None), 200) 
    # change to .scalar() instead of first when unique constraint is added to ISBN column  

# think this can be removed (make sure though)
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

@book.route("/api/v1.0/addbooktodb", methods=["POST"])
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

@book.route("/api/v1.0/book_id/<isbn>", methods=["GET"])
def get_book_id_by_ISBN(isbn):
    book = db.session.query(Book.book_id).filter(Book.ISBN==isbn).first()

    data_to_return = []

    if book is not None:
        data_to_return.append(book.book_id)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "Book not found in DB"}), 404)

@book.route("/api/v1.0/books/<string:isbn>", methods=["GET"])
def get_one_book(isbn):
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn
    r = requests.get(url)
    js = r.json()

    if "items" not in js:
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

@book.route("/api/v1.0/books/<string:isbn>/<string:user_id>/currentlyreading", methods=["POST"])
def add_currently_reading(isbn, user_id):
    try:
        book = db.session.query(Book).filter_by(ISBN=isbn).first()
        book_id = book.book_id

        db.session.add(Reading(user_id=user_id, book_id=book_id, start_date=datetime.date.today()))
        db.session.add(Activity(user_id=user_id, action_id=4, object_id=1, date_created=datetime.datetime.now(), target_id=book_id))
        db.session.commit()

        return make_response( jsonify( {"success" : "Added to bookshelf"}), 201 )
    except Exception:
        return make_response( jsonify( {"error" : "Failed to add to shelf"}), 404)

@book.route("/api/v1.0/user/<string:user_id>/currentlyreading", methods=["GET"])
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


@book.route("/api/v1.0/books/<string:isbn>/<string:user_id>/currentlyreading", methods=["DELETE"])
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


@book.route("/api/v1.0/books/<string:isbn>/<string:user_id>/wanttoread", methods=["POST"])
def add_want_to_read(isbn, user_id):
    try:
        book = db.session.query(Book).filter_by(ISBN=isbn).first()
        book_id = book.book_id

        db.session.add(WantsToRead(user_id=user_id, book_id=book_id, date_added=datetime.date.today()))
        # db.session.add(Activity(user_id=user_id, action_id=2, object_id=1, date_created=datetime.date.today(), target_id=book_id))
        db.session.commit()
        
        return make_response( jsonify( {"success" : "Added to bookshelf"}), 201 )
    except Exception:
        return make_response( jsonify( {"error" : "Failed to add to shelf"}), 404)


@book.route("/api/v1.0/user/<string:user_id>/wantstoread", methods=["GET"])
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
        
@book.route("/api/v1.0/books/<string:isbn>/<string:user_id>/wanttoread", methods=["DELETE"])
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


@book.route("/api/v1.0/books/<string:isbn>/<string:user_id>/hasread", methods=["POST"])
def add_has_read(isbn, user_id):
    try:
        book = db.session.query(Book).filter_by(ISBN=isbn).first()
        book_id = book.book_id

        # update date selection
        db.session.add(HasRead(user_id=user_id, book_id=book_id, start_date=datetime.date.today(), finish_date=datetime.date.today()))
        db.session.add(Activity(user_id=user_id, action_id=3, object_id=1, date_created=datetime.datetime.now(), target_id=book_id))
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

@book.route("/api/v1.0/user/<string:user_id>/hasread", methods=["GET"])
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

@book.route("/api/v1.0/books/<string:isbn>/<string:user_id>/hasread", methods=["DELETE"])
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