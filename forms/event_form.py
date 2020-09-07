from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, IntegerField, SelectField
from flask_wtf.file import FileField
from wtforms import validators


class EventForm(Form):
    event_id = HiddenField()

    event_name = StringField("Name: ", [
        validators.DataRequired("Please enter your name."),
        validators.Length(3, 20, "Name should be from 3 to 20 symbols")
    ])

    event_place = StringField("Place: ", [
        validators.DataRequired("Please enter your place."),
        validators.Length(3, 20, "Place should be from 3 to 20 symbols")
    ])

    event_date = DateField("Birthday: ", [validators.DataRequired("Please enter your birthday.")])

    event_friends = SelectField("Birthday: ", coerce=int)

    submit = SubmitField("Save")



