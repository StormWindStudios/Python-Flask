from app import db
from datetime import datetime, timedelta
import os
from werkzeug.security import (
    generate_password_hash, 
    check_password_hash
)
from flask_login import UserMixin
from app import login
from hashlib import md5
import jwt
from time import time
import base64
from flask import current_app, url_for

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class Post(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(20)
    )

    body = db.Column(
        db.String(140)
    )

    timestamp = db.Column(
        db.DateTime,
        index=True,
        default = datetime.utcnow
    )

    author = db.relationship(
        'User',
        backref='user'
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def _asdict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'timesatmp': self.timestamp
        }

class User(UserMixin, db.Model): 

    id = db.Column(
        db.Integer, 
        primary_key=True, 
        unique=True
    )

    token = db.Column(
        db.String(32),
        index=True,
        unique=True
    )

    token_expiration = db.Column(
        db.DateTime
    )

    first_name = db.Column(
        db.String(20)
    )

    last_name = db.Column(
        db.String(20)
    )

    email = db.Column(
        db.String(120),
        index=True,
        unique=True
    )

    password_hash = db.Column(
        db.String(128)
    )

    about_me = db.Column(
        db.String(200)
    )

    last_seen = db.Column(
        db.DateTime, 
        default=datetime.utcnow
    )

    posts = db.relationship(
        'Post',
        lazy='dynamic'
    )

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()

        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)

        return self.token

    def revoke_token():
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)

        return followed.union(own).order_by(
            Post.timestamp.desc()
        )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size=80):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return current_app.config['AVATAR_IMAGE_URL'].format(
            digest,
            size
        )
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in },
            current_app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')
    
    def _asdict(self, include_email=False):

        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'about_me': self.about_me,
            'last_seen': self.last_seen,
            'post_count': self.posts.count(),
            'posts': [post._asdict() for post in self.posts],
            '_links': {
                'self': url_for('api.api_get_user', user_id=self.id),
                'followers': url_for('api.api_get_user_followers', user_id=self.id),
                'followed': url_for('api.api_get_user_followed', user_id=self.id),
                'avatar': self.avatar(128)
            }
        }

        if include_email:
            data['email'] = self.email

        return data

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return
        
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.email)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))