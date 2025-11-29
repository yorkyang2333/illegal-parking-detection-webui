import os
from models import db


def init_db(app):
    """Initialize the database"""
    # Configure database
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, 'instance')

    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    db_path = os.path.join(instance_path, 'users.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with app
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()
        print(f"Database initialized at {db_path}")


def get_db():
    """Get database instance"""
    return db
