from datetime import datetime
from flask import (
    jsonify,
    abort,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
    current_app,
    session,
    send_from_directory,
)
from flask_login import current_user, login_required
from functools import wraps
from app import db
from app.main.forms import (
    ContactUs,
    EditProfileForm,
    EmptyForm,
    PostForm,
    OrdersForm,
    ProductForm,
    Products,
    RetailStoreForm,
    CheckoutForm,
    Categories,
    SearchForm,
)
from app.models import (
    User,
    Post,
    Product,
    RetailStores,
    Category,
    CustomerOrderDetails,
    Aisles,
    OrderItem,
    Order,
)
from app.main import bp
from app.auth.email import send_email
from flask_babel import get_locale, _
from werkzeug.utils import secure_filename
import os
import imghdr
import paypalrestsdk
import json
from app.message import Messager

client = Messager(current_app.config["APP_VERIFY_CODE"])


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route("/", methods=["GET", "POST"])
@bp.route("/home", methods=["GET", "POST"])
def index():
    form = RetailStoreForm()
    store = RetailStores.query.all()
    cat1 = Category.query.all()
    return render_template(
        "index.html", title="Home", store=store, form=form, cat1=cat1
    )


@bp.route("/community", methods=["GET", "POST"])
@login_required
def community():
    cat1 = Category.query.all()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for("main.community"))
    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = (
        url_for("main.community", page=posts.next_num) if posts.has_next else None
    )
    prev_url = (
        url_for("main.community", page=posts.prev_num) if posts.has_prev else None
    )
    return render_template(
        "community.html",
        title="Community",
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        cat1=cat1,
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    cat1 = Category.query.all()
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = (
        url_for("main.user", username=user.username, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("main.user", username=user.username, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    form = EmptyForm()
    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form,
        cat1=cat1,
    )


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    cat1 = Category.query.all()
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit() and request.method == "POST":
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("main.user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template(
        "edit_profile.html",
        title="Edit Profile",
        form=form,
        user=current_user,
        cat1=cat1,
    )


def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")


@bp.route("/edit_profile/upload_images", methods=["POST"])
def upload_images():
    uploaded_file = request.files["file"]
    filename = secure_filename(uploaded_file.filename)
    if filename != "":
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config[
            "UPLOAD_EXTENSIONS"
        ] or file_ext != validate_image(uploaded_file.stream):
            abort(400)
        uploaded_file.save(os.path.join(current_app.config["UPLOAD_PATH"], filename))
        current_user.image = filename
        db.session.commit()
    return redirect(url_for("main.edit_profile"))


# @bp.route('/edit_profile/upload_images/<filename>')
# def upload(filename):
#     return send_from_directory(current_app.config['UPLOAD_PATH'], filename)


@bp.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("User {} not found.".format(username))
            return redirect(url_for("main.community"))
        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for("main.user", username=username))
        current_user.follow(user)
        db.session.commit()
        flash("You are following {}!".format(username))
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.community"))


@bp.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("User {} not found.".format(username))
            return redirect(url_for("main.community"))
        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for("main.user", username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash("You are not following {}.".format(username))
        return redirect(url_for("main.user", username=username))
    else:
        return redirect(url_for("main.community"))


@bp.route("/shop/<shopname>", methods=["GET", "POST"])
def shop(shopname):
    cat1 = Category.query.all()
    form = ProductForm()
    store = RetailStores.query.filter_by(store_name=shopname).first()
    page = request.args.get("page", 1, type=int)
    aisles = Aisles.query.paginate(
        page, current_app.config["SHOPAISLES_PER_PAGE"], False
    )
    next_url = (
        url_for("main.shop", shopname=shopname, page=aisles.next_num)
        if aisles.has_next
        else None
    )
    prev_url = (
        url_for("main.shop", shopname=shopname, page=aisles.prev_num)
        if aisles.has_prev
        else None
    )
    category = Category.query.all()
    return render_template(
        "shop2.html",
        aisles=aisles.items,
        form=form,
        next_url=next_url,
        prev_url=prev_url,
        category=category,
        shopname=shopname,
        store=store,
        cat1=cat1,
    )


@bp.route("/shop/<shopname>/product", methods=["GET", "POST"])
def items(shopname):
    cat1 = Category.query.all()
    page = request.args.get("page", 1, type=int)
    form = ProductForm()
    product = Product.query.paginate(page, current_app.config["PRODUCTS_PER_PAGE"])
    category = Category.query.all()
    return render_template(
        "products2.html",
        product=product,
        form=form,
        category=category,
        shopname=shopname,
        cat1=cat1,
    )


@bp.route("/shop/<shopname>/product/category/<int:id>")
def category(shopname, id):
    cat1 = Category.query.all()
    page = request.args.get("page", 1, type=int)
    form = ProductForm()
    cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_pro = Product.query.filter_by(category_id=cat.id).paginate(
        page, current_app.config["CATEGORY_PER_PAGE"]
    )
    category = Category.query.all()
    return render_template(
        "category.html",
        form=form,
        product=get_cat_pro,
        category=category,
        shopname=shopname,
        cat=cat,
        cat1=cat1,
    )


@bp.route("/shop/<shopname>/product/<int:id>", methods=["GET", "POST"])
def singleitem(shopname, id):
    cat1 = Category.query.all()
    product = Product.query.get_or_404(id)
    return render_template(
        "singleitem.html", shopname=shopname, product=product, cat1=cat1
    )


@bp.route("/shop/<shopname>/aisles/<int:id>", methods=["GET", "POST"])
def aisle(shopname, id):
    cat1 = Category.query.all()
    form = ProductForm()
    aisle = Aisles.query.filter_by(id=id).first()
    category1 = Category.query.filter_by(aisles_id=aisle.id).all()
    page = request.args.get("page", 1, type=int)
    category = Category.query.all()
    for cat in category1:
        product = Product.query.filter_by(category_id=cat.id).paginate(
            page, current_app.config["PRODUCTS_PER_PAGE"]
        )
    return render_template(
        "aisles.html",
        product=product,
        form=form,
        category=category,
        shopname=shopname,
        category1=category1,
        aisle=aisle,
        cat1=cat1,
    )


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cat1 = Category.query.all()
    form = CheckoutForm()
    if form.validate_on_submit():
        user = CustomerOrderDetails(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            mobile=form.mobile.data,
            ship_add=form.ship_address.data,
        )
        db.session.add(user)
        db.session.commit()
        if "Shoppingcart" not in session or len(session["Shoppingcart"]) <= 0:
            return redirect(url_for("main.index"))
        for key, pro in session["Shoppingcart"].items():
            subtotal = float(pro["prize"]) * int(pro["quantity"])
            order_item = OrderItem(
                order_client=user.id,
                customer=current_user.id,
                product=key,
                prize=subtotal,
                quantity=pro["quantity"],
                ordered=True,
            )
            db.session.add(order_item)
            db.session.commit()
        order = Order.query.filter_by(customer=current_user.id, ordered=False).first()
        if not order:
            ordering = Order(
                customer=current_user.id,
                order_item=order_item.id,
                ordered=True,
                billing_address=user.id,
            )
            db.session.add(ordering)
            db.session.commit()
            return redirect(url_for("main.payment"))
    if "Shoppingcart" not in session or len(session["Shoppingcart"]) <= 0:
        return redirect(url_for("main.index"))
    subtotal = 0
    total = 0
    for key, pro in session["Shoppingcart"].items():
        if pro["discount"]:
            discount = (float(pro["discount"]) / 100) * float(pro["prize"])
            discount_prize = float(pro["prize"]) - discount
            subtotal += discount_prize * int(pro["quantity"])
            total = subtotal
        else:
            subtotal += float(pro["prize"]) * int(pro["quantity"])
            total = subtotal
    return render_template("checkout2.html", form=form, total=total, cat1=cat1)


@bp.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    cat1 = Category.query.all()
    client_id = os.environ.get("CLIENT_ID")
    subtotal = 0
    total = 0
    for key, pro in session["Shoppingcart"].items():
        if pro["discount"]:
            discount = (float(pro["discount"]) / 100) * float(pro["prize"])
            discount_prize = float(pro["prize"]) - discount
            subtotal += discount_prize * int(pro["quantity"])
            total = subtotal
        else:
            subtotal += float(pro["prize"]) * int(pro["quantity"])
            total = subtotal
    return render_template("payment.html", cat1=cat1, total=total, client_id=client_id)


paypalrestsdk.configure(
    {"mode": "sandbox", "client_id": "", "client_secret": ""}  # sandbox or live
)


@bp.route("/create-order", methods=["GET", "POST"])
@login_required
def create_order():
    payment = paypalrestsdk.Payment(
        {
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://localhost:3000/payment/execute",
                "cancel_url": "http://localhost:3000/",
            },
            "transactions": [
                {
                    "item_list": {
                        "items": [
                            {
                                "name": "testitem",
                                "sku": "12345",
                                "price": "500.00",
                                "currency": "USD",
                                "quantity": 1,
                            }
                        ]
                    },
                    "amount": {"total": "500.00", "currency": "USD"},
                    "description": "This is the payment transaction description.",
                }
            ],
        }
    )
    if payment.create():
        print("success!!!")
        print(payment.id)
    else:
        print(payment.error)

    return jsonify({"paymentID": payment.id})


@bp.route("/execute", methods=["POST"])
def execute():
    success = False
    payment = paypalrestsdk.Payment.find(request.form["paymentID"])
    if payment.execute({"payer_id": request.form["payerID"]}):
        print("Execute success!")
        success = True
    else:
        print(payment.error)
    return jsonify({"success": success})


def MagerDict(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@bp.route("/add_to_cart", methods=["POST"])
def addtocart():
    try:
        product_id = request.form.get("product_id")
        quantity = int(request.form.get("quantity"))
        product = Product.query.filter_by(id=product_id).first()
        if request.method == "POST":
            DictItem = {
                product_id: {
                    "name": product.pname,
                    "description": product.description,
                    "prize": product.prize,
                    "discount": product.discount,
                    "picture": product.picture,
                    "quantity": quantity,
                }
            }

            if "Shoppingcart" in session:
                print(session["Shoppingcart"])
                if product_id in session["Shoppingcart"]:
                    for key, item in session["Shoppingcart"].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item["quantity"] += 1
                else:
                    session["Shoppingcart"] = MagerDict(
                        session["Shoppingcart"], DictItem
                    )
                    return redirect(request.referrer)
            else:
                session["Shoppingcart"] = DictItem
                return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@bp.route("/cart", methods=["GET", "POST"])
def cart():
    cat1 = Category.query.all()
    if "Shoppingcart" not in session or len(session["Shoppingcart"]) <= 0:
        return redirect(url_for("main.index"))
    subtotal = 0
    total = 0
    for key, pro in session["Shoppingcart"].items():
        if pro["discount"]:
            discount = (float(pro["discount"]) / 100) * float(pro["prize"])
            discount_prize = float(pro["prize"]) - discount
            subtotal += discount_prize * int(pro["quantity"])
            total = subtotal
        else:
            subtotal += float(pro["prize"]) * int(pro["quantity"])
            total = subtotal
        # subtotal += float(pro["prize"]) * int(pro["quantity"])
        # total = subtotal

    return render_template("cart.html", total=total, cat1=cat1)


@bp.route("/updatecart/<int:code>", methods=["GET", "POST"])
def updatecart(code):
    if "Shoppingcart" not in session or len(session["Shoppingcart"]) <= 0:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        quantity = request.form.get("quantity")
        try:
            session.modified = True
            for k, pro in session["Shoppingcart"].items():
                if int(k) == code:
                    pro["quantity"] = quantity
                    flash("Update successful")
                    return redirect(url_for("main.cart"))
        except Exception as e:
            print(e)
            return redirect(url_for("main.cart"))


@bp.route("/removeitem/<int:id>")
def removeitem(id):
    if "Shoppingcart" not in session or len(session["Shoppingcart"]) <= 0:
        return redirect(url_for("main.index"))
    try:
        session.modified = True
        for k, pro in session["Shoppingcart"].items():
            if int(k) == id:
                session["Shoppingcart"].pop(k, None)
                return redirect(url_for("main.cart"))
    except Exception as e:
        print(e)
        return redirect(url_for("main.cart"))


@bp.route("/clearcart")
def clearcart():
    try:
        session.pop("Shoppingcart", None)
        return redirect(url_for("main.index"))
    except Exception as e:
        print(e)


@bp.route("/about", methods=["GET"])
def about():
    cat1 = Category.query.all()
    return render_template("about.html", cat1=cat1)


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    cat1 = Category.query.all()
    form = ContactUs()
    if form.validate_on_submit():
        name = request.form.get("name")
        subject = request.form.get("subject")
        email = request.form.get("email")
        message = request.form.get("message")
        send_email(
            subject,
            sender=current_app.config["ADMINS"][0],
            recipients=[current_app.config["ADMINS"][0]],
            text_body=render_template(
                "email/contactform.txt", name=name, message=message, email=email
            ),
            html_body=render_template(
                "email/contactform.html", name=name, message=message, email=email
            ),
        )
        flash("Message has been send, will get back to you as soon as possible")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form, cat1=cat1)


@bp.route("/terms")
def terms():
    cat1 = Category.query.all()
    return render_template("terms.html", cat1=cat1)


@bp.route("/policy")
def policy():
    cat1 = Category.query.all()
    return render_template("policy.html", cat1=cat1)


@bp.route("/search")
@login_required
def search():
    cat1 = Category.query.all()
    if not g.search_form.validate():
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)
    # posts, total = Post.search(g.search_form.q.data, page,
    #                            current_app.config['POSTS_PER_PAGE'])
    product, total = Product.search(
        g.search_form.q.data, page, current_app.config["POSTS_PER_PAGE"]
    )
    next_url = (
        url_for("main.search", q=g.search_form.q.data, page=page + 1)
        if total > page * current_app.config["POSTS_PER_PAGE"]
        else None
    )
    prev_url = (
        url_for("main.search", q=g.search_form.q.data, page=page - 1)
        if page > 1
        else None
    )
    return render_template(
        "search.html",
        title=_("Search"),
        product=product,
        next_url=next_url,
        prev_url=prev_url,
        total=total,
        cat1=cat1,
    )


@bp.route("/fb_webhook", methods=["GET"])
def fb_webhook():
    verification_code = current_app.config["APP_VERIFY_CODE"]
    verify_token = request.args.get("hub.verify_token")
    if verification_code == verify_token:
        return request.args.get("hub.challenge")


@bp.route("/fb_webhook", methods=["POST"])
def fb_receive_message():
    message_entries = json.loads(request.data.decode("utf8"))["entry"]
    for entry in message_entries:
        for message in entry["messaging"]:
            user_id = message["sender"]["id"]
            if message.get("message"):
                print("{sender[id]} says {message[text]}".format(**message))
                if "text" in message["text"]:
                    client.send_text(user_id, "Hi, How can I help")

    return "Hi"
