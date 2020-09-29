from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, SubmitField,TextAreaField, SelectField, BooleanField, IntegerField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import User
from flask_babel import lazy_gettext as _l
import sqlite3

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    file = FileField('File')
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CheckoutForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    mobile = IntegerField('Moble Number', validators=[DataRequired()])
    ship_address = BooleanField('Shipping address is the same as billing address')
    remeber_details = BooleanField('Remember details for next order')
    proceed = SubmitField('Proceed to Payment')

QUANTITY_CHOICES = [(i, str(i)) for i in range(1,30)]

class ProductForm(FlaskForm):
    title = StringField('')
    add_card = SubmitField('Add To Card')
    check_out = SubmitField('Check Out')
    quantity = SelectField('Quantity', validators=[DataRequired()], choices=QUANTITY_CHOICES)


class OrdersForm(FlaskForm):
    name = StringField('', validators=[Length(min=1), DataRequired()],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    mobile_num = StringField('', validators=[Length(min=1), DataRequired()],
                             render_kw={'autofocus': True, 'placeholder': 'Mobile'})
    quantity = SelectField('', validators=[DataRequired()],
                           choices=QUANTITY_CHOICES)
    order_place = StringField('', validators=[Length(min=1), DataRequired()],
                              render_kw={'placeholder': 'Order Place'})

class RetailStoreForm(FlaskForm):
    submin = SubmitField('Enter')


class Products(FlaskForm):
    category = StringField('Category')
    pname = StringField('Product Name')
    description = StringField('Decription')
    prize = DecimalField('Prize')
    availability = BooleanField('Availabile')
    picture = StringField('Picture')
    store_id = IntegerField('Store ID')
    submit = SubmitField('Add Product')

class Categories(FlaskForm):
    name = StringField('Category Name')
    store_id = IntegerField('Store ID')

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class UploadImages(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Submit')