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
    data = []

    try:
        result = db2.session.query(User).filter_by(user_id=user_id).first()
    except:
        return make_response(jsonify({"error" : "Invalid ID"}), 404)
    
    user = {"user_id" : result.user_id, "auth0_id" : result.auth0_id, "name" : result.full_name}
    data.append(user)

    return make_response(jsonify(data), 200)

@app.route("/api/v1.0/search/users/<query>", methods=["GET"])
def search_users(query):
    url = 'https://dev-1spzh9o1.eu.auth0.com/api/v2/users?q=name:*' + query + '*'
    headers = {'authorization' : 'Bearer ' + access_token}

    req = requests.get(url, headers=headers)
    js = req.json()

    data = []

    for result in js:
        try:
            user = {"auth0_id" : result['user_id'], "name" : result['name'], "email" : result['email']}
            data.append(user)
        except Exception:
            pass

    if data:
        return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify({"error" : "No results for this query"}), 404)

if __name__ == "__main__":
    app.run(debug=True)