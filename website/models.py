from . import db
from flask_login import UserMixin 

class User(db.Model,UserMixin):
    '''This is a User model that stores information about the user, such as 
       id, email, hashed password and username'''
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(150),unique=True,nullable=False) 
    password = db.Column(db.String(256), unique=True,nullable=False)
    username = db.Column(db.String(20),unique=True,nullable=False)