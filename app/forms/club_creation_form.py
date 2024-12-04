from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from app.models.club import Club


class ClubCreationForm(FlaskForm):
    name = StringField("Club Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    contact_email = StringField("Contact Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Create Club")

    def validate_name(self, name):
        club = Club.query.filter_by(name=name.data).first()
        if club:
            raise ValidationError("A club with this name already exists. Please choose a different name.")
