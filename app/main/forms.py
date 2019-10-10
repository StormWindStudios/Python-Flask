from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField,
    BooleanField, 
    SubmitField,
    TextAreaField
)
from wtforms.validators import (
    DataRequired,
    ValidationError,
    Email,
    EqualTo,
    Length
)
from app.main.models import User
from flask_login import current_user



class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    about_me = TextAreaField('About Me:', validators=[Length(min=0, max=200)])
    submit = SubmitField('Save')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user.email != current_user.email:
                raise ValidationError('Email address already taken!')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=20)])
    body = TextAreaField('Post Body', validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    submit = SubmitField('Publish')
