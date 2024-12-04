from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange


class EventFeedbackForm(FlaskForm):
    event_id = HiddenField("Event ID", validators=[DataRequired()])
    rating = IntegerField("Rating (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField("Comment")
    submit = SubmitField("Submit Feedback")
