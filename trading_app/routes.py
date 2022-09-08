from trading_app import app, db, bcrypt, forms, TOKEN
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from trading_app.models import Transaction, User
from datetime import datetime, timedelta
import requests


@app.route("/")
def index():
    if current_user.is_authenticated:
        print(current_user.id)
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


@app.route("/top_up", methods=["GET", "POST"])
@login_required
def top_up():
    form = forms.TopUpForm()
    if form.validate_on_submit():
        t = Transaction(
            transaction_amount=form.amount.data,
            transaction_type="top up",
            stock_name=None,
            user_id=current_user.id,
        )
        db.session.add(t)
        db.session.commit()
        flash("Funds have been added to your account", "success")
        return redirect(url_for("index"))
    return render_template("top_up.html", form=form)


@app.route("/account_summary")
@login_required
def account_summary():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    cash_balance = sum([transaction.transaction_amount for transaction in transactions])
    all_stock_names = set(
        [
            transaction.stock_name
            for transaction in transactions
            if transaction.stock_name is not None
        ]
    )
    stocks = {}
    for stock in all_stock_names:
        stock_quantity = sum(
            [
                transaction.stock_quantity
                for transaction in transactions
                if transaction.stock_name == stock
            ]
        )
        if stock_quantity != 0:
            stocks[stock] = stock_quantity
    return render_template("summary.html", cash_balance=cash_balance, stocks=stocks)


@app.route("/trade", methods=["GET", "POST"])
@login_required
def trade():
    form = forms.TradeForm()
    if form.validate_on_submit():
        transactions = Transaction.query.filter_by(user_id=current_user.id)
        yesterday = datetime.now() - timedelta(1)
        yesterday = datetime.strftime(yesterday, "%Y-%m-%d")
        if form.buy_sell.data == "buy":
            cash_balance = sum(
                [transaction.transaction_amount for transaction in transactions.all()]
            )

            url = f"https://api.polygon.io/v1/open-close/{form.name.data}/{yesterday}?adjusted=true&apiKey={TOKEN}"
            r = requests.get(url)
            data = r.json()
            if data["status"] != "OK":
                flash("Stock does not exist", "error")
            else:
                price = data["close"]
                required_balance = price * form.quantity.data
                if cash_balance >= required_balance:
                    t = Transaction(
                        transaction_amount=-required_balance,
                        transaction_type=form.buy_sell.data,
                        stock_name=form.name.data,
                        stock_quantity=form.quantity.data,
                        user_id=current_user.id,
                    )
                    db.session.add(t)
                    db.session.commit()
                    flash(
                        f"Shares purchased: {form.name.data}, quantity: {form.quantity.data}",
                        "success",
                    )
                else:
                    flash(
                        f"inssufficient funds required: {required_balance}, curently on balance {cash_balance}",
                        "warning",
                    )
        if form.buy_sell.data == "sell":
            transactions = transactions.filter_by(stock_name=form.name.data).all()
            stocks_left = sum(
                [
                    transaction.stock_quantity
                    for transaction in transactions
                    if transaction.stock_name == form.name.data
                ]
            )
            if stocks_left >= form.quantity.data:
                url = f"https://api.polygon.io/v1/open-close/{form.name.data}/{yesterday}?adjusted=true&apiKey={TOKEN}"
                r = requests.get(url)
                data = r.json()
                price = data["close"]

                t = Transaction(
                    transaction_amount=price * form.quantity.data,
                    transaction_type=form.buy_sell.data,
                    stock_name=form.name.data,
                    stock_quantity=-form.quantity.data,
                    user_id=current_user.id,
                )
                db.session.add(t)
                db.session.commit()
                flash(
                    f"Shares sold: {form.name.data}, quantity: {form.quantity.data}",
                    "success",
                )
            else:
                flash(
                    f"inssufficient stock {form.name.data} amount: {stocks_left}",
                    "warning",
                )
    return render_template("trade.html", form=form)


@app.route("/get_price", methods=["GET", "POST"])
@login_required
def get_price():
    form = forms.StockShortNameForm()
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
    return render_template("get_price.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
