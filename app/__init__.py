import os
from flask import Flask
from .db import init_db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-secret"),
        DATABASE=os.environ.get("DATABASE_PATH", os.path.join(app.instance_path, "tracker.sqlite3")),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    init_db(app)
    from .routes import bp
    app.register_blueprint(bp)
    return app
