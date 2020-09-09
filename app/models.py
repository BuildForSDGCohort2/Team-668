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
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')

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

class CustomerOrderDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64)) 
    email = db.Column(db.String(64)) 
    address = db.Column(db.String(64)) 
    city = db.Column(db.String(64))
    mobile = db.Column(db.Integer)
    odate = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    order_item = db.relationship('OrderItem', backref='client', lazy=True)
    
    def __repr__(self):
        return '<Customer order details: {}>'.format(self.first_name)

class OrderItem(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    order_client = db.Column(db.Integer, db.ForeignKey('customer_order_details.id'))
    product = db.Column(db.Integer, db.ForeignKey('product.id'))
    prize = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    pname = db.Column(db.String(64), index=True)
    description = db.Column(db.String(140))
    prize = db.Column(db.Float)
    availabilty = db.Column(db.Integer)
    picture = db.Column(db.Text)
    store_id = db.Column(db.Integer, db.ForeignKey('retail_stores.id')) 
    order = db.relationship('OrderItem', backref='item', lazy=True)  

    def __repr__(self):
        return '<Product {}>'.format(self.pname) 

class RetailStores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(64), nullable=False)
    categoryrel = db.relationship('Category', backref='rstore', lazy=True)
    productsrel = db.relationship('Product', backref='store', lazy=True)

    def __repr__(self):
        return '{}'.format(self.store_name) 

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    store_id = db.Column(db.Integer, db.ForeignKey('retail_stores.id'))
    product_items = db.relationship('Product', backref='catdetails', lazy=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64))
    email = db.Column(db.String(64))
    types = db.Column(db.String(64))

    def __repr__(self):
        return '<Admin {}>'.format(self.fname) 

class Supervisor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64), index=True)

