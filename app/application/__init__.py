"""Initialize Flask Application."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_redis import FlaskRedis

db = SQLAlchemy()

def init_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)
    with app.app_context():
        from app.application.home import routes
        db.create_all()
        return app