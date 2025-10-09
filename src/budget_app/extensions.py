from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create extension objects but do NOT bind them to the app yet
db = SQLAlchemy()
migrate = Migrate()
