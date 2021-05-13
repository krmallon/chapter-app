from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import User, Message
from sqlalchemy import and_, or_, func, desc
from user.routes import user_id_in_db
import datetime

message = Blueprint('message', __name__)

@message.route("/api/v1.0/user/<string:user_id>/messages/participants", methods=["GET"])
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

@message.route("/api/v1.0/user/<string:user_id>/messages/", methods=["GET"])
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

@message.route("/api/v1.0/user/<string:user_id>/messages/received", methods=["GET"])
def get_all_received_messages_by_user_id(user_id):
    data_to_return = []

    messages = db.session.query(Message.msg_id, Message.msg_text, Message.sender_id, Message.recipient_id, Message.time_sent, User.full_name, User.image).join(User, User.user_id==Message.sender_id).filter(Message.recipient_id==user_id)

    for message in messages:
        db.session.commit()
        msg = {"id" : message.msg_id, "text" : message.msg_text, "sender" : message.sender_id, "sender_name" : message.full_name, "sender_image" : message.image, "recipient" : message.recipient_id, "sent" : message.time_sent }
        data_to_return.append(msg)

    if data_to_return:
        return make_response(jsonify(data_to_return), 200)
    else:
        return make_response(jsonify({"error" : "No messages found"}), 404)




@message.route("/api/v1.0/user/<string:user_id>/messages/sent", methods=["GET"])
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

@message.route("/api/v1.0/messages/", methods=["GET"])
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


@message.route("/api/v1.0/user/<string:user_id>/contact", methods=["POST"])
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