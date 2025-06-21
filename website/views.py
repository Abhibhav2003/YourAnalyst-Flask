from flask import Blueprint,render_template,request,redirect,flash
from flask_login import login_required,current_user
import pandas as pd
from website.services import scrape_data as scrp

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

@views.route('/display', methods=['GET','POST'])
@login_required
def display():
    if request.method == "POST":
        if request.form.get('scrape-url'):
            url = request.form.get('scrape-url')
            dfs = scrp.Scrape(url)
            table_html = "".join([df.to_html(classes="table table-dark table-striped table-bordered data-table", index=False) for df in dfs.values()])
        
        else:
            file = request.files.get('upload-file')
            if not file or file.filename == '':
                flash("No file uploaded", category="error")
                return redirect(request.referrer)

            filename = file.filename.lower()

            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif filename.endswith('.txt'):
                df = pd.read_csv(file, sep=',')
            else:
                flash("File type not supported", category="error")
                return redirect(request.referrer)
            table_html = df.to_html(classes="table table-dark table-striped table-bordered data-table", index=False)
    return render_template("display.html", table=table_html)


@views.route('/analyse')
@login_required
def analyse():
    return ""