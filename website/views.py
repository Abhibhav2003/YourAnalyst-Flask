from flask import Blueprint,render_template

views = Blueprint('views',__name__)

@views.route('/')
def start():
    return render_template('start.html')