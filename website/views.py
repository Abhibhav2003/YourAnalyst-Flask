from flask import Blueprint,render_template,request,redirect,flash,session
from flask_login import login_required,current_user
import pandas as pd
from website.services import scrape_data as scrp
import pickle
import base64

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
            dfs = {f'table{i}': df for i, df in enumerate(scrp.Scrape(url).values())}
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

            dfs = {'table0': df}

        session.clear()
        session['tables'] = base64.b64encode(pickle.dumps(dfs)).decode('utf-8')
        print(pickle.loads(base64.b64decode(session.get('tables'))))

        table_list = [df.to_html(classes="table table-dark table-striped table-bordered data-table", index=False) for df in dfs.values()]
        return render_template("display.html", tables=table_list)

    flash('Upload Data First', category='error')
    return redirect('/upload')


@views.route('/analyse', methods=['GET', 'POST'])
@login_required
def analyse():
    if request.method == 'POST':
        selected_tables = [key for key in request.form if key.startswith("table")]

        if not selected_tables:
            flash("Please select at least one table.", category="error")
            return redirect('/display')

        encoded_data = session.get('tables')
        if not encoded_data:
            flash("No table data found in session", category="error")
            return redirect('/upload')

        dfs = pickle.loads(base64.b64decode(encoded_data))

        # Ensure selected checkboxes match stored keys
        selected_dfs = [dfs[k] for k in dfs if k in selected_tables]

        if not selected_dfs:
            flash("No matching tables found.", category="error")
            return redirect('/display')

        # Just showing the first table for now
        return selected_dfs[0].to_html(index=False)

    flash('Click on Analyse button to proceed', category='error')
    return redirect('/display')