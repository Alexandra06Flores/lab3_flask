import os
from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv

load_dotenv()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")
    mail.init_app(app)

    from .auth import auth_bp
    from .panel import panel_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(panel_bp)

    from .db import crear_admin_inicial
    crear_admin_inicial()

    return app