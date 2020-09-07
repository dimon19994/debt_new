from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, IntegerField, FloatField, \
    FieldList, SelectField
from flask_wtf.file import FileField
from wtforms import validators


class CheckForm(Form):
    check_id = HiddenField()

    check_description = StringField("Описание: ", [
        validators.DataRequired("Please enter your username."),
        validators.Length(3, 200, "Username should be from 3 to 20 symbols")
    ])

    check_sum = FieldList(FloatField("Сумма: ", [
        validators.DataRequired("Please enter your username."),
        validators.NumberRange(0.01, 100000, "Username should be from 0.01 to 100000 symbols")
    ]), min_entries=0)

    check_item = FieldList(StringField("Продукт: ", [
        validators.DataRequired("Please enter your password."),
        validators.Length(3, 100, "Password should be from 5 to 100 symbols")
    ]), min_entries=0)

    item_cost = FieldList(FloatField("Цена продукта: ", [
        validators.DataRequired("Please enter your username."),
        validators.NumberRange(0.01, 100000, "Username should be from 0.01 to 100000 symbols")
    ]), min_entries=0)

    item_id = FieldList(HiddenField(), min_entries=0)

    check_sale = FloatField("Надбавка/Скидка (+/-): ", [
        # validators.DataRequired("Please enter your username."),
        validators.NumberRange(-1, 100000, "Username should be from 0.00 to 100000 symbols")

    ], default=0)

    item_type = FieldList(SelectField("Тип продукта: ", [validators.DataRequired("Please enter your birthday.")],
                                      choices=[('Алкоголь', 'Алкоголь'), ('Билеты', 'Билеты'),
                                               ('Вода', 'Вода'), ('Еда', 'Еда'),
                                               ('Квартира', 'Квартира'), ('Хрень', 'Хрень')]),
                                                min_entries=0)

    check_pay = FieldList(SelectField("Плательщик: ", coerce=int), min_entries=0)

    submit = SubmitField("Save")
