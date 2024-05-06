from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from .model import User
from .database import db
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

cursor = db["user"]
login_manager = LoginManager()
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "DDE 546 WD65DW DW23"
    bcrypt = Bcrypt(app)
    login_manager.init_app(app)

    from .views import views


    app.register_blueprint(views, url_prefix="/")
    return app


@login_manager.user_loader
def load_user(user_id):
    user_id = json.loads(user_id)
    result = cursor.find_one({"_id": ObjectId(user_id)})
    user = User(id=result['_id'], first_name=result['first_name'], last_name=result['last_name'], email=result['email'], active=True, anonymous=False, authenticated=True)
    return user