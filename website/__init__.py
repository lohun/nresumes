from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "DDE 546 WD65DW DW23"

    from .views import views


    app.register_blueprint(views, url_prefix="/")
    return app