from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    order = db.relationship('Order', backref='order', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(64), index=True)
    qauntity = db.Column(db.Integer)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    odate = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ddate = db.Column(db.DateTime, nullable=True)
    mobile = db.Column(db.Integer)
    prize = db.Column(db.Integer)

    # define CRUD operationmethods
    
    def __repr__(self):
        return '<Order {}>'.format(self.pname)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(64), index=True)
    prize = db.Column(db.Integer)
    availabilty = db.Column(db.Integer)
    category = db.Column(db.String(64))
    item = db.Column(db.String(64))
    picture = db.Column(db.Text)
    description = db.Column(db.String(140))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)    

    def __repr__(self):
        return '<Product {}>'.format(self.pname) 

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64))
    email = db.Column(db.String(64))
    types = db.Column(db.String(64))

    def __repr__(self):
        return '<Admin {}>'.format(self.fname) 

class RetailStores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return '{}'.format(self.store_name) 