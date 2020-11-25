from flask_wtf import FlaskForm
import flask_wtf.file as flask_file
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
import wtforms.validators as validators
import flaskblog.models as models
import flask_login


class RegistrationFrom(FlaskForm):
    """
    This class is represent the sign up form
    """
    username = StringField('Username', validators=[
        validators.DataRequired(), validators.Length(min=4, max=20)])
    email = StringField(
        'Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(), validators.Length(min=8, max=255)])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.DataRequired(), validators.EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = models.User.query.filter_by(username=username.data).first()
        if user:
            raise validators.ValidationError(
                'That username already taken. Please select another username')

    def validate_email(self, email):
        user = models.User.query.filter_by(email=email.data).first()
        if user:
            raise validators.ValidationError(
                'That email already taken. Please select another email')


class LoginFrom(FlaskForm):
    """
    This class is represent the sign in form
    """
    email = StringField('Email', validators=[
        validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(), validators.Length(min=8, max=255)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountFrom(FlaskForm):
    """
    This class is represent the sign up form
    """
    username = StringField('Username', validators=[
        validators.DataRequired(), validators.Length(min=4, max=20)])
    email = StringField(
        'Email', validators=[validators.DataRequired(), validators.Email()])
    picture = flask_file.FileField('Update Profile Picture', validators=[
        flask_file.file_allowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Udpate')

    def validate_username(self, username):
        if username.data != flask_login.current_user.username:
            user = models.User.query.filter_by(username=username.data).first()
            if user:
                raise validators.ValidationError(
                    'That username already taken. Please select another username')

    def validate_email(self, email):
        if email.data != flask_login.current_user.email:
            user = models.User.query.filter_by(email=email.data).first()
            if user:
                raise validators.ValidationError(
                    'That email already taken. Please select another email')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    content = TextAreaField('Content', validators=[validators.DataRequired()])
    submit = SubmitField('Post It!')


class RequestResetForm(FlaskForm):
    # forgot your password?
    # in this Form you will enter your email and than you will 
    #   recive an link to this email inorder to reset your password
    email = StringField(
        'Email', validators=[validators.DataRequired(), validators.Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = models.User.query.filter_by(email=email.data).first()
        if not user:
            raise validators.ValidationError(
                'There is no account with this Email')


class ResetPasswordForm(FlaskForm):
    # after you request the reset, this Form get involved when you right your new password
    password = PasswordField('Password', validators=[
        validators.DataRequired(), validators.Length(min=8, max=255)])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.DataRequired(), validators.EqualTo('password')])
    submit = SubmitField('Reset Password')
