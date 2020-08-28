from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User
import sqlite3

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
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

class OrdersForm(FlaskForm):
    name = StringField('', validators=[Length(min=1), DataRequired()],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    mobile_num = StringField('', validators=[Length(min=1), DataRequired()],
                             render_kw={'autofocus': True, 'placeholder': 'Mobile'})
    quantity = SelectField('', validators=[DataRequired()],
                           choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    order_place = StringField('', validators=[Length(min=1), DataRequired()],
                              render_kw={'placeholder': 'Order Place'})

class ProductForm(FlaskForm):
    add_card = SubmitField('Add To Card')
    check_out = SubmitField('Check Out')

class RetailStoreForm(FlaskForm):
    submin = SubmitField('Enter')