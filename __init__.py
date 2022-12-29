from flask import Flask
from flask_cors import CORS
from firebase_admin import credentials, initialize_app

cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SECRET_KEY"] = '12345rtfescdvf'
    app.config["CORS_HEADERS"] = "Content-Type"

    from .userAPI import userAPI

    app.register_blueprint(userAPI, url_prefix='/user')

    return app
