from flask import Flask
from routes import routes_blueprint
from models import create_tables, populate_initial_staff
import sqlite3
import random

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # Load configuration from config.py

    # Create tables and populate initial data
    create_tables()
    populate_initial_staff()

    # Register blueprints
    app.register_blueprint(routes_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
