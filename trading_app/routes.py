from trading_app import app, db, bcrypt, forms, TOKEN
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user
from trading_app.models import User
from datetime import datetime, timedelta
import requests


@app.route("/")
def index():
    if current_user.is_authenticated:
        print(current_user)
    else:
        print("not authenticated")
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            if current_user.is_authenticated:
                print(current_user)
            else:
                print("no current user")
            next_page = request.args.get("next")
            print("login successful")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Login failure, please check details", "danger")
    return render_template("login.html", form=form, title="login")


@app.route("/register", methods=["GET", "POST"])
def register():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            name=form.name.data, email=form.email.data, password=encrypted_password
        )
        db.session.add(user)
        db.session.commit()
        flash(f"User: {form.email.data} was successfully created, please log in")
        return redirect(url_for("login"))
    return render_template("register.html", form=form, title="register")


@app.route("/reimbursement", methods=["GET", "POST"])
@login_required
def reimbursement():
    pass


@app.route("/account_summary", methods=["GET", "POST"])
@login_required
def account_summary():
    pass


@app.route("/trade", methods=["GET", "POST"])
@login_required
def trade():
    pass


@app.route("/get_price", methods=["GET", "POST"])
@login_required
def get_price():
    form = forms.StockShortName()
    if form.validate_on_submit():
        yesterday = datetime.now() - timedelta(1)
        yesterday = datetime.strftime(yesterday, "%Y-%m-%d")
        url = f"https://api.polygon.io/v1/open-close/{form.name.data}/{yesterday}?adjusted=true&apiKey={TOKEN}"
        print(url)
        r = requests.get(url)
        data = r.json()
        if data["status"] != "OK":
            flash("Stock does not exist")
        else:
            print(data["close"])
            return render_template(
                "get_price.html", form=form, stock_price=data["close"]
            )
    return render_template("get_price.html", form=form, stock_price=9999)


@app.route("/logout")
@login_required
def logout():
    pass
