from extensions import db
from flask import Blueprint, make_response, jsonify, request
from models import Group, UserGroup, User, Post
from achievement.routes import check_achievement

group = Blueprint('group', __name__)


@group.route("/api/v1.0/groups", methods=["GET"])
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

@group.route("/api/v1.0/user/<string:user_id>/groups", methods=["GET"])
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

@group.route("/api/v1.0/groups/new", methods=["POST"])
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
@group.route("/api/v1.0/groups/edit", methods=["PUT"])
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
@group.route("/api/v1.0/groups/delete", methods=["DELETE"])
def delete_group():
    if "group_id" in request.form:
        group_id = request.form["group_id"]

    group = db.session.query(Group).filter(Group.id==group_id).first()
    db.session.delete(group)
    db.session.commit()

    return make_response(jsonify({}), 204)

@group.route("/api/v1.0/groups/<string:group_id>", methods=["GET"])
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


@group.route("/api/v1.0/groups/<string:group_id>/members", methods=["GET"])
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

@group.route("/api/v1.0/groups/<string:group_id>/join", methods=["POST"])
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
@group.route("/api/v1.0/groups/<string:group_id>/leave", methods=["DELETE"])
def leave_group(group_id):
    if "user_id" in request.form:
        user_id = request.form["user_id"]

    entry = db.session.query(UserGroup).filter(UserGroup.group_id==group_id, UserGroup.user_id==user_id).first()
    db.session.delete(entry)
    db.session.commit()

    return make_response(jsonify({}), 204)

@group.route("/api/v1.0/groups/<string:group_id>/posts", methods=["GET"])
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

@group.route("/api/v1.0/groups/<string:group_id>/posts", methods=["POST"])
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
@group.route("/api/v1.0/groups/posts/<string:post_id>", methods=["PUT"])
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
@group.route("/api/v1.0/groups/posts", methods=["DELETE"])
def delete_group_post(): 
    if "post_id" in request.form:
        post_id = request.form["post_id"]
        post = db.session.query(Post).filter(Post.id==post_id).first()
        db.session.delete(post)
    
    db.session.commit()
    
    return make_response(jsonify({}), 204)