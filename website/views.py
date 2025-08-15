from flask import Blueprint,send_file,render_template,request,redirect,flash,session
from flask_login import login_required
import pandas as pd
from website.services import scrape_data as scrp , ai_analysis as ai, analyze
import pickle
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

@views.route('/documentation',methods=['GET'])
@login_required
def documentation():
    return render_template('documentation.html')


@views.route('/display', methods=['GET','POST'])
@login_required
def display():
    '''This function stores the dataframe in the session state'''
    
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
    '''This function receives result from Gemini API'''
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
    '''This function lets the user download the analysis report'''
    response_text = request.form.get('response')

    if not response_text:
        flash("No analysis found to download.", category="error")
        return redirect('/analyse')

    buffer = io.BytesIO() # creating an in-memory file
    buffer.write(response_text.encode('utf-8')) # write into this file
    buffer.seek(0) # bring the pointer again to the start

    return send_file(
        buffer, # this is the file
        as_attachment=True, # Save the file instead of displaying it
        download_name='analysis_report.md', # this should be the name
        mimetype='text/plain' # and this is the file format
    )

@views.route('/manual-analysis', methods=['GET', 'POST'])
@login_required
def manual_analysis():
    '''This function provides various functions for statistical analysis 
       and dashboard creation'''
    
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

    saved_charts = session.get('saved_charts')
    if isinstance(saved_charts, str):
       charts = pickle.loads(base64.b64decode(saved_charts))
    elif isinstance(saved_charts, list):
       charts = saved_charts
    else:
       charts = []


    if request.method == 'POST':
        action = request.form.get('action')
        if action != 'undo':
           session['undo_state'] = session['tables']
        try:
            if action == 'info':
                results['info'] = analyze.information(df)
            elif action == 'drop_nulls':
                df = analyze.drop_na(df)
                
            elif action == 'fill_nulls_mean':
                df = analyze.fill_na_mean(df)

            elif action == 'remove_duplicates':
                df = analyze.drop_duplicates(df)

            elif action == 'normalize':
                df = analyze.normalize(df, selected_columns)

            elif action == 'standardize':
                df = analyze.standardize(df, selected_columns)

            elif action == 'encode_categorical':
                df = analyze.encode_categorical(df, selected_columns)

            elif action == 'regression':
                feature_cols = selected_columns[:-1]
                target_col = selected_columns[-1]
                results['Linear Regression'] = analyze.linear_regression(df, feature_cols, target_col)

            elif action == 'cluster':
                selected_columns = request.form.getlist('columns')
                n_clusters = int(request.form.get('n_clusters', 3))  
                n_init = int(request.form.get('n_init', 10))         
                if not selected_columns:
                  flash("Please select at least one column for clustering.", category="error")
                else:
                  df = analyze.apply_clustering(df, selected_columns, n_clusters=n_clusters, n_init=n_init)

            elif action == 'basic_stats':
                results['Basic Stats'] = analyze.basic_stats(df, selected_columns)

            elif action == 'outliers':
                results['Outliers'] = {}
                for col in selected_columns:
                    results['Outliers'][col] = analyze.detect_outliers(df, col)

            elif action == 'association':
                results['Correlation'] = analyze.correlation(df, selected_columns)
                results['Covariance'] = analyze.covariance(df, selected_columns)

            elif action in ['histogram', 'scatter', 'bar', 'line', 'countplot', 'boxplot']:
                chart_html = analyze.plot_chart(df, selected_columns, action)
                charts.append({'type': action.capitalize(), 'html': chart_html})
                session['saved_charts'] = base64.b64encode(pickle.dumps(charts)).decode('utf-8')
                
            elif action == 'change_dtype':
                col = request.form.get('convert_column')
                dtype = request.form.get('convert_dtype')
                df = analyze.change_column_type(df, col, dtype)

            elif action == 'undo':
                undo_state = session.get('undo_state')
                if undo_state:
                    dfs = pickle.loads(base64.b64decode(undo_state))
                    df = list(dfs.values())[0]
                    flash("Undo successful. Reverted to previous state.", category="info")
                else:
                    flash("No undo history found.", category="warning")

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

@views.route('/manual-analysis/download-csv', methods=['GET'])
def download_manual_csv():
    encoded_data = session.get('tables')
    if not encoded_data:
        flash("No table data found in session", category="error")
        return redirect('/manual-analysis')
    
    dfs = pickle.loads(base64.b64decode(encoded_data))
    df = list(dfs.values())[0]

    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='modified_data.csv'
    )

@views.route('/download_dashboard', methods=['GET'])
def download_dashboard():
    saved_charts = session.get('saved_charts')
    if not saved_charts:
        flash("No charts saved for dashboard.", category="error")
        return redirect('/manual-analysis')

    try:
        if isinstance(saved_charts, str):
            charts = pickle.loads(base64.b64decode(saved_charts))
        else:
            charts = saved_charts
    except (pickle.UnpicklingError, base64.binascii.Error):
        flash("Error processing chart data.", category="error")
        return redirect('/manual-analysis')

    if not isinstance(charts, list):
        flash("Invalid chart data format.", category="error")
        return redirect('/manual-analysis')

    for chart in charts:
        if not isinstance(chart, dict) or 'type' not in chart or 'html' not in chart:
            flash("Invalid chart data format.", category="error")
            return redirect('/manual-analysis')

    html_content = """
    <html>
    <head>
        <title>My Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { background-color: #121212; color: white; font-family: Arial; }
            .dashboard { display: flex; flex-wrap: wrap; gap: 20px; padding: 20px; }
            .chart { border: 2px solid #333; border-radius: 8px; padding: 10px; background: #1e1e1e; flex: 1 1 45%; }
            img { max-width: 100%; height: auto; border-radius: 5px; }
            h2 { text-align: center; }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">Dashboard</h1>
        <div class="dashboard">
    """

    for chart in charts:
        html_content += f"""
        <div class="chart">
            <h2>{chart['type']}</h2>
            {chart['html']}
        </div>
        """

    html_content += """
        </div>
    </body>
    </html>
    """

    buffer = io.BytesIO()
    buffer.write(html_content.encode('utf-8'))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='dashboard.html',
        mimetype='text/html'
    )

@views.route('/clear_dashboard', methods=['POST'])
def clear_dashboard():
    session.pop('saved_charts', None)
    flash("Dashboard cleared successfully!", category="success")
    return redirect('/manual-analysis')