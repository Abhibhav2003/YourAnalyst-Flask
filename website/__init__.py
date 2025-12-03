from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from os import path
from flask_caching import Cache
from flask_login import LoginManager

load_dotenv() # looks for .env file in the project loads key-value pairs into environment variables os.environ
db = SQLAlchemy() # initializes SQLAlchemy object
DB_NAME = "database.db" # database name
cache = Cache()

def create_app():
   '''create_app function builds and configures the flask application,
   it avoids circular imports and allow easy testing.'''
   app = Flask(__name__) # create flask app
   app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") # sets secret key for signing cookies and session data.
   app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # Configures SQLAlchemy to use SQLite with the given DB name.
   db.init_app(app) # links the SQLAlchemy object 'db' with the app.

   app.config['SESSION_TYPE'] = 'filesystem' # session data stored on server not in client cookies.
   app.config['SESSION_PERMANENT'] = False # session expires when browser is closed.
   Session(app) # initializes flask-session for this app.

   app.config['CACHE_TYPE'] = 'FileSystemCache'
   app.config['CACHE_DIR'] = 'flask_cache'
   app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 min
   cache.init_app(app)

   from .views import views # import views
   from .auth import auth # import auth
   # blueprints split routes across multiple files/modules
   app.register_blueprint(views, url_prefix='/') # register blueprint
   app.register_blueprint(auth, url_prefix='/') # register blueprint

   from .models import User # import User model from models.
   create_database(app) # checks if DB file exists, creates it if not.

   login_manager = LoginManager() # handles login sessions.
   login_manager.login_view = 'auth.login' # tells Flask-Login where to redirect when a user isn't logged in.
   login_manager.init_app(app) # link to app

   @login_manager.user_loader # defines how to retrieve a User from the DB given their ID (stored in session).
   def load_user(id):
      user = cache.get(f"user:{id}")
      if not user:
          user = User.query.get(int(id))
          if user:
              cache.set(f"user:{id}", user)  # will expire in 5 min (default timeout)
      return user

   return app

def create_database(app):  # Checks if database file exists inside instance/.
   if not path.exists('instance/' + DB_NAME):
      with app.app_context(): # app_context required for DB operations before first request.
         db.create_all() # create db.
         print('Created Database!')
   else:
      print('Database already exists') # database exists.