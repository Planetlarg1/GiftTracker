from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Set login view
    login_manager.login_view = 'auth.login'

    # Load user
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from .auth import auth_bp
    from .wishlist import wishlist_bp
    from .gifts import gifts_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(wishlist_bp, url_prefix='/wishlist')
    app.register_blueprint(gifts_bp, url_prefix='/gifts')

    # Redirect from home to login
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    return app
