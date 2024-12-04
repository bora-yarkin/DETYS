from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models.user import User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = SelectField("Role", choices=[("student", "Student"), ("club_manager", "Club Manager")], validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo("confirm", message="Passwords must match")])
    confirm = PasswordField("Confirm Password")
    submit = SubmitField("Register")

    # Custom validators to ensure unique username and email
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is already taken. Please choose another.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is already registered. Please use a different email address.")
