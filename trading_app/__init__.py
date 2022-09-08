# import configparser
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt

# config = configparser.ConfigParser()
# config.read("api.ini")
TOKEN = os.getenv("TOKEN")
FLASK_SECRET_KEY = os.getenv("SECRET_KEY")

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = FLASK_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "trading_app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
db.create_all()

from trading_app.models import User, Transaction

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    db.create_all()
    return User.query.get(int(user_id))


from trading_app import routes
