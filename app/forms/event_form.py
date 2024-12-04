from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields import DateTimeLocalField


class EventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    date = DateTimeLocalField("Event Date and Time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    submit = SubmitField("Create Event")
