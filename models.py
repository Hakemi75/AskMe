from peewee import Model, CharField, TextField, IntegerField, ForeignKeyField, DateTimeField, SqliteDatabase
from flask_login import UserMixin
from datetime import datetime

database = SqliteDatabase("message_box.db")


class BaseModel(Model):
    class Meta:
        database = database


class User(UserMixin, BaseModel):
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    bio = TextField(default="")
    youtube_url = TextField(null=True)
    twitter_url = TextField(null=True)
    github_url = TextField(null=True)
    website_url = TextField(null=True)
    total_likes = IntegerField(default=0)
    total_answers = IntegerField(default=0)


class Question(BaseModel):
    user = ForeignKeyField(User, backref="questions")
    content = TextField()
    created_at = DateTimeField(default=datetime.now)
    likes = IntegerField(default=0)


class Answer(BaseModel):
    user = ForeignKeyField(User, backref="answers")
    question = ForeignKeyField(Question, backref="answers")
    content = TextField()
    created_at = DateTimeField(default=datetime.now)
    likes = IntegerField(default=0)


class Comment(BaseModel):
    user = ForeignKeyField(User, backref="comments")
    answer = ForeignKeyField(Answer, backref="comments")
    content = TextField()
    created_at = DateTimeField(default=datetime.now)


class Like(BaseModel):
    user = ForeignKeyField(User, backref="likes")
    question = ForeignKeyField(Question, backref="liked_by", null=True)
    answer = ForeignKeyField(Answer, backref="liked_by", null=True)


def create_tables():
    with database:
        database.create_tables([User, Question, Answer, Comment, Like])
