from flask_wtf import Form
from wtforms import SubmitField, HiddenField
from wtforms import validators
from wtforms.fields.html5 import DateField


class EventUnionForm(Form):
    event_id = HiddenField()

    start_date = DateField("С: ", [validators.DataRequired("Please start date.")], format="%Y-%m-%d")

    end_date = DateField("По: ", [validators.DataRequired("Please start date.")], format="%Y-%m-%d")

    submit = SubmitField("Подробнее")
