from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, IntegerField, FloatField, \
    FieldList, SelectField
from flask_wtf.file import FileField
from wtforms import validators


class RepayForm(Form):
    id = HiddenField()

    event_id = IntegerField("Событие: ")

    my_id = IntegerField("я: ")

    repay_id = SelectField("Человек: ", coerce=int)

    repay_sum = FloatField("Сумма: ", [
        validators.DataRequired("Please enter your username."),
        validators.NumberRange(0.01, 100000, "Username should be from 0.01 to 100000 symbols")
    ])

    submit = SubmitField("Save")
