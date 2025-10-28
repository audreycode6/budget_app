from flask import Flask
from dotenv import load_dotenv
import os

# expose extensions at package level so tests can do: from budget_app import db
from .extensions import db, migrate

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)

    # Default config (production/dev)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev_secret'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'postgresql://audrey@localhost:5432/budget_db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Override for testing if provided
    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so SQLAlchemy knows about them
    from budget_app import models
 
    # Register routes blueprint AFTER db.init_app
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app