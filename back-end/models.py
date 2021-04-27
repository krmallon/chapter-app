# coding: utf-8
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()
metadata = Base.metadata


class Achievement(Base):
    __tablename__ = 'Achievement'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    badge = Column(String)


class Action(Base):
    __tablename__ = 'Action'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)


class Activity(Base):
    __tablename__ = 'Activity'

    id = Column(Integer, primary_key=True, server_default=text("nextval('activity_id_seq'::regclass)"))
    user_id = Column(Integer)
    action_id = Column(Integer)
    object_id = Column(Integer)
    target_id = Column(Integer)
    date_created = Column(DateTime(True))


class Book(Base):
    __tablename__ = 'Book'

    book_id = Column(Integer, primary_key=True, server_default=text("nextval('book_id_seq'::regclass)"))
    ISBN = Column(String)
    title = Column(String)
    author = Column(String)
    publish_date = Column(String)
    page_count = Column(Integer)
    image_link = Column(String)


class BookRecDatum(Base):
    __tablename__ = 'BookRecData'

    book_id = Column(Integer, primary_key=True)
    isbn = Column(String)
    authors = Column(String)
    published_year = Column(String)
    title = Column(String)


class Group(Base):
    __tablename__ = 'Group'

    id = Column(Integer, primary_key=True, server_default=text("nextval('group_id_seq'::regclass)"))
    name = Column(String)
    description = Column(String)
    founder_id = Column(Integer)


class Object(Base):
    __tablename__ = 'Object'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Rating(Base):
    __tablename__ = 'Ratings'

    user_id = Column(Integer, primary_key=True, nullable=False)
    book_id = Column(Integer, primary_key=True, nullable=False)
    rating = Column(Integer)


class UpdateType(Base):
    __tablename__ = 'UpdateType'

    id = Column(Integer, primary_key=True)
    type = Column(String)


class User(Base):
    __tablename__ = 'User'

    user_id = Column(Integer, primary_key=True, server_default=text("nextval('user_id_seq'::regclass)"))
    auth0_id = Column(String)
    full_name = Column(String)
    nickname = Column(String)
    email = Column(String)
    image = Column(String)


class AchievementProgres(Base):
    __tablename__ = 'Achievement_Progress'

    user_id = Column(Integer, primary_key=True, nullable=False)
    achievement_id = Column(ForeignKey('Achievement.id'), primary_key=True, nullable=False)
    target = Column(Integer)
    current = Column(Integer)
    date_earned = Column(Date)

    achievement = relationship('Achievement')


class BookRecommendation(Base):
    __tablename__ = 'BookRecommendation'

    id = Column(Integer, primary_key=True, server_default=text("nextval('book_rec_sequence'::regclass)"))
    rec_book_id = Column(ForeignKey('Book.book_id'))
    rec_source_id = Column(ForeignKey('Book.book_id'))
    user_id = Column(ForeignKey('User.user_id'))

    rec_book = relationship('Book', primaryjoin='BookRecommendation.rec_book_id == Book.book_id')
    rec_source = relationship('Book', primaryjoin='BookRecommendation.rec_source_id == Book.book_id')
    user = relationship('User')


class Comment(Base):
    __tablename__ = 'Comment'

    comment_id = Column(Integer, primary_key=True)
    object_id = Column(Integer)
    commenter_id = Column(ForeignKey('User.user_id'))
    text = Column(String)
    time_submitted = Column(Date)
    target_id = Column(Integer)

    commenter = relationship('User')


class Follow(Base):
    __tablename__ = 'Follow'

    id = Column(Integer, primary_key=True, server_default=text("nextval('follow_id_seq'::regclass)"))
    user_id = Column(ForeignKey('User.user_id'))
    follower_id = Column(ForeignKey('User.user_id'))
    follow_date = Column(Date)

    follower = relationship('User', primaryjoin='Follow.follower_id == User.user_id')
    user = relationship('User', primaryjoin='Follow.user_id == User.user_id')


class FriendRecommendation(Base):
    __tablename__ = 'FriendRecommendation'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('User.user_id'))
    rec_friend_id = Column(ForeignKey('User.user_id'))

    rec_friend = relationship('User', primaryjoin='FriendRecommendation.rec_friend_id == User.user_id')
    user = relationship('User', primaryjoin='FriendRecommendation.user_id == User.user_id')


class Goal(Base):
    __tablename__ = 'Goal'

    id = Column(Integer, primary_key=True, server_default=text("nextval('goal_id_sequence'::regclass)"))
    target = Column(Integer)
    current = Column(Integer)
    user_id = Column(ForeignKey('User.user_id'))
    year = Column(Integer)

    user = relationship('User')


class HasRead(Base):
    __tablename__ = 'HasRead'

    user_id = Column(ForeignKey('User.user_id'), primary_key=True, nullable=False)
    book_id = Column(ForeignKey('Book.book_id'), primary_key=True, nullable=False)
    start_date = Column(Date)
    finish_date = Column(Date)

    book = relationship('Book')
    user = relationship('User')


class Like(Base):
    __tablename__ = 'Like'

    id = Column(Integer, primary_key=True)
    object_type = Column(Integer)
    object_id = Column(Integer)
    user_id = Column(ForeignKey('User.user_id'))

    user = relationship('User')


class Message(Base):
    __tablename__ = 'Message'

    msg_id = Column(Integer, primary_key=True, server_default=text("nextval('msg_id_seq'::regclass)"))
    msg_text = Column(String)
    sender_id = Column(ForeignKey('User.user_id'))
    recipient_id = Column(ForeignKey('User.user_id'))
    time_sent = Column(DateTime(True))
    read = Column(Boolean)

    recipient = relationship('User', primaryjoin='Message.recipient_id == User.user_id')
    sender = relationship('User', primaryjoin='Message.sender_id == User.user_id')


class Post(Base):
    __tablename__ = 'Post'

    id = Column(Integer, primary_key=True, server_default=text("nextval('post_id_seq'::regclass)"))
    group_id = Column(ForeignKey('Group.id'))
    author_id = Column(ForeignKey('User.user_id'))
    text = Column(String)
    title = Column(String)

    author = relationship('User')
    group = relationship('Group')


class Reading(Base):
    __tablename__ = 'Reading'

    user_id = Column(ForeignKey('User.user_id'), primary_key=True, nullable=False)
    book_id = Column(ForeignKey('Book.book_id'), primary_key=True, nullable=False)
    start_date = Column(Date)

    book = relationship('Book')
    user = relationship('User')


class Review(Base):
    __tablename__ = 'Review'

    id = Column(Integer, primary_key=True, server_default=text("nextval('review_id_seq'::regclass)"))
    reviewer_id = Column(ForeignKey('User.user_id'))
    book_id = Column(ForeignKey('Book.book_id'))
    rating = Column(Numeric)
    text = Column(String)

    book = relationship('Book')
    reviewer = relationship('User')


class Status(Base):
    __tablename__ = 'Status'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('User.user_id'))
    update_type = Column(Integer)
    description = Column(String)
    likes = Column(Integer)

    user = relationship('User')


class UserAchievement(Base):
    __tablename__ = 'User_Achievement'

    user_id = Column(ForeignKey('User.user_id'), primary_key=True, nullable=False)
    achievement_id = Column(ForeignKey('Achievement.id'), primary_key=True, nullable=False)
    date_earned = Column(Date)

    achievement = relationship('Achievement')
    user = relationship('User')


class UserGroup(Base):
    __tablename__ = 'User_Group'

    user_id = Column(ForeignKey('User.user_id'), primary_key=True, nullable=False)
    group_id = Column(ForeignKey('Group.id'), primary_key=True, nullable=False)
    join_date = Column(Date)

    group = relationship('Group')
    user = relationship('User')


class WantsToRead(Base):
    __tablename__ = 'WantsToRead'

    user_id = Column(ForeignKey('User.user_id'), primary_key=True, nullable=False)
    book_id = Column(ForeignKey('Book.book_id'), primary_key=True, nullable=False)
    date_added = Column(Date)

    book = relationship('Book')
    user = relationship('User')
