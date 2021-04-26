from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import User

import requests

search = Blueprint('search', __name__)

@search.route("/api/v1.0/search/users/<query>", methods=["GET"])
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

@search.route("/api/v1.0/search/books/<string:query>", methods=["GET"])
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
