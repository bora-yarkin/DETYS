from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Length, Regexp
from app.models import User, Club


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = SelectField(
        "Role",
        choices=[("student", "Student"), ("club_manager", "Club Manager")],
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
    )
    # password = PasswordField(
    #     "Password",
    #     validators=[DataRequired(), EqualTo("confirm", message="Passwords must match")],
    # )
    # password = PasswordField(
    #     "Password",
    #     validators=[DataRequired(), Length(min=8), Regexp("^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)", message="Password must contain at least one uppercase letter, one lowercase letter, and one digit."), EqualTo("confirm", message="Passwords must match")],
    # )
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


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ClubCreationForm(FlaskForm):
    name = StringField("Club Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    contact_email = StringField("Contact Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Create Club")

    def __init__(self, *args, **kwargs):
        self.club_id = kwargs.pop("club_id", None)
        super(ClubCreationForm, self).__init__(*args, **kwargs)

    def validate_name(self, name):
        club = Club.query.filter_by(name=name.data).first()
        if club and (self.club_id is None or club.id != self.club_id):
            raise ValidationError("A club with this name already exists. Please choose a different name.")


class EventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    date = StringField("Event Date and Time", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    club_id = SelectField("Club", coerce=int, validators=[DataRequired()])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create Event")


class EventFeedbackForm(FlaskForm):
    event_id = HiddenField("Event ID", validators=[DataRequired()])
    rating = IntegerField("Rating (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField("Comment")
    submit = SubmitField("Submit Feedback")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Publish")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")


class MarkAsReadForm(FlaskForm):
    submit = SubmitField("Mark as Read")


class MarkAllNotificationsReadForm(FlaskForm):
    submit = SubmitField("Mark All as Read")


class NotificationPreferencesForm(FlaskForm):
    receive_event_notifications = BooleanField("Receive Event Notifications")
    receive_membership_notifications = BooleanField("Receive Membership Notifications")
    receive_feedback_notifications = BooleanField("Receive Feedback Notifications")
    submit = SubmitField("Update Preferences")


class ForumTopicForm(FlaskForm):
    title = StringField("Topic Title", validators=[DataRequired()])
    submit = SubmitField("Create Topic")


class ForumPostForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")
