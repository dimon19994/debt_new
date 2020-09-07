from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, IntegerField
from flask_wtf.file import FileField
from wtforms import validators


class PersonForm(Form):
    person_id = HiddenField()

    person_email = StringField("Email: ", [
        validators.DataRequired("Please enter your email."),
        validators.Email("Wrong email format")
    ])

    person_username = StringField("Username: ", [
        validators.DataRequired("Please enter your username."),
        validators.Length(3, 20, "Username should be from 3 to 20 symbols")
    ])

    person_password = PasswordField("Password: ", [
        validators.DataRequired("Please enter your password."),
        validators.Length(8, 20, "Password should be from 8 to 20 symbols")
    ])

    person_name = StringField("Name: ", [
        validators.DataRequired("Please enter your name."),
        validators.Length(3, 20, "Name should be from 3 to 20 symbols")
    ])

    person_surname = StringField("Surname: ", [
        validators.DataRequired("Please enter your surname."),
        validators.Length(3, 20, "Surname should be from 3 to 20 symbols")
    ])

    person_card = StringField("Curd number: ", [
        validators.DataRequired("Please enter your curd number."),
        validators.length(16, 16, "Curd number should be 16 symbols")
    ])

    submit = SubmitField("Save")


