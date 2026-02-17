from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from .config import DATABASE_URL, CORS_ORIGINS

socketio = SocketIO(cors_allowed_origins=CORS_ORIGINS)
app_instance = None


def create_app():
    global app_instance
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, origins=CORS_ORIGINS.split(","), supports_credentials=True)

    from .models.database import db

    db.init_app(app)
    socketio.init_app(app)

    from .api.routes import api_bp
    from .api.ws import ws_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(ws_bp, url_prefix="/ws")

    app_instance = app

    with app.app_context():
        db.create_all()

    return app


def get_app():
    return app_instance
