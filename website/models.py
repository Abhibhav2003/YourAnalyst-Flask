from . import db # SQLAlchemy instance
from flask_login import UserMixin # UserMixin is a Flask-Login helper class that adds default
                                  # implementations of certain methods required for authentication

class User(db.Model,UserMixin):# db.Model makes this a SQLAlchemy Model
    '''This is a User model that stores information about the user, such as 
       id, email, hashed password and username'''
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(150),unique=True,nullable=False) 
    password = db.Column(db.String(256), unique=True,nullable=False) # hashed password string
    username = db.Column(db.String(20),unique=True,nullable=False)