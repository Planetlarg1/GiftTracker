import os

# Cross-site request forgery protection
WTF_CSRF_ENABLED = True
SECRET_KEY = 'a-very-secret-secret'

# SQLite Config
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')