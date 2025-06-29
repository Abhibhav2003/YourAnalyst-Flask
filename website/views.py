from flask import Blueprint,send_file,render_template,request,redirect,flash,session
from flask_login import login_required,current_user
import pandas as pd
from website.services import scrape_data as scrp
from website.services import ai_analysis as ai
import pickle
import json
import io
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

        table_list = [df.to_html(classes="table table-dark table-striped table-bordered data-table", index=False) for df in dfs.values()]
        return render_template("display.html", tables=table_list)

    flash('Upload Data First', category='error')
    return redirect('/upload')


@views.route('/analyse', methods=['GET', 'POST'])
@login_required
def analyse():
    if request.method == 'POST':
        selected_key = request.form.get("selected_table")

        if not selected_key:
            flash("Please select a table.", category="error")
            return redirect('/display')

        encoded_data = session.get('tables')
        if not encoded_data:
            flash("No table data found in session", category="error")
            return redirect('/upload')

        dfs = pickle.loads(base64.b64decode(encoded_data))

        if selected_key not in dfs:
            flash("Selected table not found.", category="error")
            return redirect('/display')

        df = dfs[selected_key]
        json_str = df.to_json(orient='records')
        response_text = ai.enter_data("Analyse this json data",json_str)
        return render_template("analyse.html", response = response_text)

    flash('Click on Analyse button to proceed', category='error')
    return redirect('/display')


@views.route('/download_report', methods=['POST'])
def download_report():
    response_text = request.form.get('response')

    if not response_text:
        flash("No analysis found to download.", category="error")
        return redirect('/analyse')

    buffer = io.BytesIO()
    buffer.write(response_text.encode('utf-8'))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='analysis_report.md',
        mimetype='text/plain'
    )

@views.route('/manual-analysis',methods=['GET','POST'])
def manual_analysis():
    return render_template('manual_analysis.html')
