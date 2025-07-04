from flask import Blueprint,send_file,render_template,request,redirect,flash,session
from flask_login import login_required,current_user
import pandas as pd
from website.services import scrape_data as scrp , ai_analysis as ai, helpers
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

@views.route('/manual-analysis', methods=['GET', 'POST'])
@login_required
def manual_analysis():

    encoded_data = session.get('tables')
    if not encoded_data:
        flash("No table data found in session", category="error")
        return redirect('/upload')

    dfs = pickle.loads(base64.b64decode(encoded_data))
    df = list(dfs.values())[0]  

    columns = df.columns.tolist()
    selected_columns = request.form.getlist('columns') if request.method == 'POST' else []
    table_html = df.head(10).to_html(classes="styled-table", index=False)

    results = {}
    charts = []

    if request.method == 'POST':
        action = request.form.get('action')
        if not selected_columns and action != 'change_dtype':
            flash("Please select at least one column for analysis.", category="error")
            return redirect('/manual-analysis')

        try:
            if action == 'summary':
                results['Summary'] = helpers.basic_stats(df, selected_columns)
            elif action == 'drop_nulls':
                df = helpers.drop_na(df)
            elif action == 'fill_nulls_mean':
                df = helpers.fill_na_mean(df)
            elif action == 'remove_duplicates':
                df = helpers.drop_duplicates(df)
            elif action == 'normalize':
                df = helpers.normalize(df, selected_columns)
            elif action == 'standardize':
                df = helpers.standardize(df, selected_columns)
            elif action == 'encode_categorical':
                df = helpers.encode_categorical(df, selected_columns)
            elif action == 'pca':
                df = helpers.apply_pca(df, selected_columns)
            elif action == 'cluster':
                df = helpers.apply_clustering(df, selected_columns)
            elif action == 'basic_stats':
                results['Basic Stats'] = helpers.basic_stats(df, selected_columns)
            elif action == 'outliers':
                results['Outliers'] = {}
                for col in selected_columns:
                    results['Outliers'][col] = helpers.detect_outliers(df, col)
            elif action == 'confidence':
                results['Correlation'] = helpers.correlation(df, selected_columns)
                results['Covariance'] = helpers.covariance(df, selected_columns)
            elif action in ['histogram', 'scatter', 'bar', 'line']:
                encoded_image = helpers.plot_chart(df, selected_columns, action)
                charts.append({'type': action.capitalize(), 'image': encoded_image})
            elif action == 'change_dtype':
                col = request.form.get('convert_column')
                dtype = request.form.get('convert_dtype')
                if col and dtype:
                    df = helpers.change_column_type(df, col, dtype)
                    flash(f"Changed data type of column '{col}' to '{dtype}'.", category="success")
                else:
                    flash("Select both column and data type.", category="error")
            elif action == 'undo':
                dfs = pickle.loads(base64.b64decode(encoded_data))  # reload original data
                df = list(dfs.values())[0]
                flash("Reverted to last saved state.", category="info")
            else:
                flash("Invalid action.", category="error")
        except Exception as e:
            flash(f"Error during analysis: {str(e)}", category="error")

        dfs[list(dfs.keys())[0]] = df
        session['tables'] = base64.b64encode(pickle.dumps(dfs)).decode('utf-8')
        table_html = df.head(10).to_html(classes="styled-table", index=False)

    return render_template(
        'manual_analysis.html',
        columns=columns,
        selected_columns=selected_columns,
        table=table_html,
        results=results,
        charts=charts
    )
