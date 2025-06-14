from flask import Blueprint,render_template,request,redirect
from flask_login import login_required,current_user
views = Blueprint('views',__name__)

@views.route('/')
def start():
    return render_template('start.html')

@login_required
@views.route('/home')
def home():
    return render_template('home.html',message=current_user.username)