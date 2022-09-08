from tokenize import String
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    FloatField,
    IntegerField,
    SelectField,
)
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    name = StringField("Name", [DataRequired()])
    email = StringField("Email", [DataRequired(), Email()])
    password = PasswordField("Password", [DataRequired()])
    password_confirmation = PasswordField(
        "Repeat password", [EqualTo("password", "passwords must match")]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", [DataRequired(), Email()])
    password = PasswordField("Password", [DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Log in")


class StockShortNameForm(FlaskForm):
    name = StringField("stock name", [DataRequired()])
    submit = SubmitField("get price")


class TopUpForm(FlaskForm):
    amount = FloatField("Amount", [DataRequired()])
    submit = SubmitField("get price")


class TradeForm(FlaskForm):
    name = StringField("stock short name", [DataRequired()])
    quantity = IntegerField("quantity", [DataRequired()])
    buy_sell = SelectField("Operation", [DataRequired()], choices=["buy", "sell"])
    submit = SubmitField("trade")
