from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app, redirect, url_for
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login, admin_control
from app.search import add_to_index, remove_from_index, query_index
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)),
            total,
        )

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            "items": [item.to_dict() for item in resources.items],
            "_meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": resources.pages,
                "total_items": resources.total,
            },
            "_links": {
                "self": url_for(endpoint, page=page, per_page=per_page, **kwargs),
                "next": url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                if resources.has_next
                else None,
                "prev": url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                if resources.has_prev
                else None,
            },
        }
        return data


followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    image = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    order = db.relationship("Order", backref="user", lazy=True)
    order_items = db.relationship("OrderItem", backref="Client_id", lazy="dynamic")
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return "User ID:  {}".format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)

    def to_dict(self, include_email=False):
        data = {
            "id": self.id,
            "username": self.username,
            "last_seen": self.last_seen.isoformat() + "Z",
            "about_me": self.about_me,
            "post_count": self.posts.count(),
            "follower_count": self.followers.count(),
            "followed_count": self.followed.count(),
            "_links": {
                "self": url_for("api.get_user", id=self.id),
                "followers": url_for("api.get_followers", id=self.id),
                "followed": url_for("api.get_followed", id=self.id),
                "avatar": self.avatar(128),
            },
        }
        if include_email:
            data["email"] = self.email
        return data

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(SearchableMixin, db.Model):
    __searchable__ = ["body"]
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Post {}>".format(self.body)


class CustomerOrderDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    address = db.Column(db.String(64))
    city = db.Column(db.String(64))
    mobile = db.Column(db.Integer)
    ship_add = db.Column(db.Boolean)
    odate = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    order_item = db.relationship("OrderItem", backref="client", lazy="dynamic")
    order = db.relationship("Order", backref="billing_add", lazy="dynamic")

    def __repr__(self):
        return "Customer order details: First Name: {}, Last Name: {}, Email: {}, Address: {}, Mobile: {}, City: {}".format(
            self.first_name,
            self.last_name,
            self.email,
            self.address,
            self.mobile,
            self.city,
        )


products_con = db.Table(
    "products",
    db.Column("order_item_id", db.Integer, db.ForeignKey("order_item.id")),
    db.Column("order_id", db.Integer, db.ForeignKey("order.id")),
)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_client = db.Column(db.Integer, db.ForeignKey("customer_order_details.id"))
    customer = db.Column(db.Integer, db.ForeignKey("user.id"))
    product = db.Column(db.Integer, db.ForeignKey("product.id"))
    prize = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    order_item_created_date = db.Column(db.DateTime, default=datetime.utcnow)
    product_item = db.relationship(
        "Order", secondary=products_con, backref=db.backref("orderitem", lazy="dynamic")
    )
    ordered = db.Column(db.Boolean, default=False)
    # special = db.Column(db.Integer, db.ForeignKey("special.id"))

    def __repr__(self):
        return "Order Item ID: {}".format(self.id)


class Product(SearchableMixin, db.Model):
    __searchable__ = ["category_id", "pname", "description"]

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    pname = db.Column(db.String(64), index=True)
    description = db.Column(db.String(140))
    prize = db.Column(db.Float)
    availabilty = db.Column(db.Boolean)
    picture = db.Column(db.String(150))
    store_id = db.Column(db.Integer, db.ForeignKey("retail_stores.id"))
    orderitem = db.relationship("OrderItem", backref="item", lazy=True)
    discount = db.Column(db.Integer)

    def __repr__(self):
        return "{}".format(self.pname)

    def __init__(
        self,
        category_id,
        pname,
        description,
        prize,
        availabilty,
        picture,
        store_id,
        discount,
    ):
        self.category_id = category_id
        self.pname = pname
        self.description = description
        self.prize = prize
        self.availabilty = availabilty
        self.picture = picture
        self.store_id = store_id
        self.discount = discount

    def get_item(self):
        id = self.id
        return redirect(url_for("main.item", id=id))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.Integer, db.ForeignKey("user.id"))
    product = db.relationship(
        "OrderItem", secondary=products_con, backref=db.backref("order", lazy="dynamic")
    )
    order_item = db.Column(db.Integer, db.ForeignKey("order_item.id"))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    ordered = db.Column(db.Boolean, default=False)
    billing_address = db.Column(db.Integer, db.ForeignKey("customer_order_details.id"))

    def __repr__(self):
        return "Order ID: {}".format(self.id)


class RetailStores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(64), nullable=False)
    category = db.relationship("Category", backref="rstore", lazy="dynamic")
    product = db.relationship("Product", backref="store", lazy="dynamic")
    # special = db.relationship("Specials", backref="retstore", lazy="dynamic")

    def __repr__(self):
        return "{}".format(self.store_name)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    store_id = db.Column(db.Integer, db.ForeignKey("retail_stores.id"))
    aisles_id = db.Column(db.Integer, db.ForeignKey("aisles.id"))
    product = db.relationship("Product", backref="catdetails", lazy="dynamic")
    # specials = db.relationship("Specials", backref="catspecial", lazy="dynamic")

    def __init__(self, name, store_id):
        self.name = name
        self.store_id = store_id

    def __repr__(self):
        return "{}".format(self.name)


class Aisles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    store_id = db.Column(db.Integer, db.ForeignKey("retail_stores.id"))
    category = db.relationship("Category", backref="aisles", lazy=True)

    def __repr__(self):
        return "{}".format(self.name)


# class Specials(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     pname = db.Column(db.String(64), index=True)
#     description = db.Column(db.String(140))
#     prize = db.Column(db.Float)
#     availabilty = db.Column(db.Boolean)
#     picture = db.Column(db.String(150))
#     store_id = db.Column(db.Integer, db.ForeignKey("retail_stores.id"))
#     orderitem = db.relationship("OrderItem", backref="special", lazy="dynamic")
#     discount = db.Column(db.Integer)


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_admin:
            return current_user.is_authenticated
        else:
            return redirect(url_for("main.index"))

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.index"))


admin_control.add_view(Controller(User, db.session))
admin_control.add_view(Controller(CustomerOrderDetails, db.session))
admin_control.add_view(Controller(OrderItem, db.session))
admin_control.add_view(Controller(Order, db.session))
admin_control.add_view(Controller(Product, db.session))
admin_control.add_view(Controller(RetailStores, db.session))
admin_control.add_view(Controller(Category, db.session))
admin_control.add_view(Controller(Aisles, db.session))
# admin_control.add_view(ModelView(Payment, db.session))

