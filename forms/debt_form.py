from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, IntegerField, FloatField, \
    FieldList, SelectField, BooleanField
from wtforms.widgets.html5 import NumberInput
from flask_wtf.file import FileField
from wtforms import validators


class DebtForm(Form):

    debt_count = FieldList(IntegerField(default=0, widget=NumberInput(min=0, max=100)), min_entries=0)

    debt_all = FieldList(BooleanField(false_values=None), min_entries=0)

    item_id = FieldList(HiddenField(), min_entries=0)

    submit = SubmitField("Save")
