from flask import Blueprint,render_template,request,redirect
from flask_login import login_required,current_user
import pandas as pd
views = Blueprint('views',__name__)

@views.route('/')
def start():
    return render_template('start.html')

@views.route('/home')
@login_required
def home():
    return render_template('home.html')

@views.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

@views.route('/display', methods=['POST'])
@login_required
def display():
    file = request.files.get('upload-file')
    if not file:
        return "No file uploaded", 400

    df = pd.read_csv(file)
    table_html = df.to_html(classes="table table-dark table-striped table-bordered data-table", index=False)
    return render_template("display.html", table=table_html)

@views.route('/analyse')
@login_required
def analyse():
    return ""