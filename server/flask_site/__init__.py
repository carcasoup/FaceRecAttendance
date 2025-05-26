import os
from flask import Flask
from flask_site.extensions import db, migrate

from server.db import engine, Base
from server.config import DATABASE_URL


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # регистрируем маршруты
    from flask_site.routes import bp as site_bp
    app.register_blueprint(site_bp)

    # Единожды создаём схему через Base
    Base.metadata.create_all(bind=engine)
    return app