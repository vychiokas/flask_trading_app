from trading_app import db
from sqlalchemy import DateTime
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.String(50))
    email = db.Column("Email", db.String(180), unique=True, nullable=False)
    password = db.Column("Password", db.String(100), nullable=False)


class Transaction(db.Model, UserMixin):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True)
    transaction_amount = db.Column("Transaction_amount", db.Float, nullable=False)
    transaction_type = db.Column(
        "Transaction_type", db.String(10), nullable=False
    )  # BUY / SELL / REIMBURSEMENT
    stock_name = db.Column("Stock_name", db.String(20), nullable=True)
    date = db.Column("Date", DateTime, default=datetime.now())
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", lazy=True)
