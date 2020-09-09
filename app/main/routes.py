from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, OrdersForm, ProductForm, RetailStoreForm
from app.models import User, Post, Product, RetailStores, Category
from app.main import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = RetailStoreForm()
    store = RetailStores.query.all()
    return render_template('index.html', title='Home', store=store, form=form)

@bp.route('/community', methods=['GET', 'POST'])
@login_required
def community():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.community'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.community', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.community', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('community.html', title='Community', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.community'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.community'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.community'))
        if user == current_user:
            flash('You cannot unfollow yourself!') 
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.community'))

@bp.route('/shop/<shopname>', methods=['GET', 'POST'])
def shop(shopname):
    form = ProductForm()
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(
        page, current_app.config['SHOPAISLES_PER_PAGE'], False)
    category = Category.query.all()
    next_url = url_for('main.shop', shopname=shopname, page=products.next_num) \
        if products.has_next else None
    prev_url = url_for('main.shop', shopname=shopname, page=products.prev_num) \
        if products.has_prev else None
    return render_template('shop.html', products=products.items, form=form, next_url=next_url, prev_url=prev_url, category=category, shopname=shopname)

@bp.route('/shop/<shopname>/product', methods=['GET', 'POST'])
def items(shopname):
    form = ProductForm()
    product = Product.query.all()
    category = Category.query.all()
    return render_template('products.html', product=product, form=form, category=category, shopname=shopname)

@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')

@bp.route('/cart', methods=['GET', 'POST'])
def cart():
    return render_template('cart.html')

@bp.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')