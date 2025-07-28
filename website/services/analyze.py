import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io

def information(df):
    buffer = io.StringIO()
    df.info(buf=buffer) 
    return buffer.getvalue()

def drop_duplicates(df, inplace=False):
    """Drop duplicate rows from the dataframe."""
    return df.drop_duplicates(inplace=inplace) if inplace else df.drop_duplicates()

def drop_na(df, inplace=False):
    """Drop rows with missing values."""
    return df.dropna(inplace=inplace) if inplace else df.dropna()

def fill_na_mean(df):
    """Fill NA values with mean (numeric columns only)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df.fillna(df[numeric_cols].mean())

def basic_stats(df, cols):
    """Compute descriptive statistics for selected numeric columns."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    if not numeric_cols:
        raise ValueError("No numeric columns selected for Basic Stats.")
    return df[numeric_cols].describe(include='all').to_dict()

def detect_outliers(df, col):
    """Detect outliers in a numeric column using IQR method."""
    if not pd.api.types.is_numeric_dtype(df[col]):
        raise ValueError(f"Column '{col}' is not numeric.")
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
    return outliers.to_dict()

def normalize(df, cols):
    """Normalize selected numeric columns (Min-Max Scaling)."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    scaler = MinMaxScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

def standardize(df, cols):
    """Standardize selected numeric columns (Z-score Normalization)."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

def encode_categorical(df, cols):
    """Encode categorical columns with Label Encoding."""
    for col in cols:
        df[col] = LabelEncoder().fit_transform(df[col].astype(str))
    return df

def linear_regression(df, feature_cols, target_col):
    """Perform linear regression on specified features and target."""
    # Check if columns exist
    for col in feature_cols + [target_col]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe.")

    # Check if features and target are numeric
    for col in feature_cols + [target_col]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' must be numeric for linear regression.")

    # Prepare data
    X = df[feature_cols].values
    y = df[target_col].values

    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Predict
    df['LinearRegression_Prediction'] = model.predict(X)

    # Prepare output
    results = {
        'coefficients': dict(zip(feature_cols, model.coef_)),
        'intercept': model.intercept_,
        'predictions': df['LinearRegression_Prediction'].tolist(),
        'r_squared': model.score(X, y)
    }
    return results


def apply_clustering(df, cols, n_clusters=3):
    """Apply KMeans Clustering on selected numeric columns."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    if not numeric_cols:
        raise ValueError("No numeric columns selected for Clustering.")
    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    df['Cluster'] = kmeans.fit_predict(df[numeric_cols])
    return df

def correlation(df, cols):
    """Calculate correlation matrix for selected numeric columns."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    if not numeric_cols:
        raise ValueError("No numeric columns selected for Correlation.")
    return df[numeric_cols].corr().to_dict()

def covariance(df, cols):
    """Calculate covariance matrix for selected numeric columns."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    if not numeric_cols:
        raise ValueError("No numeric columns selected for Covariance.")
    return df[numeric_cols].cov().to_dict()


def plot_chart(df, cols, chart_type):
    sns.set_style('dark')
    if not cols:
        raise ValueError("No columns selected for plotting.")
    
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    
    if chart_type == 'histogram':
        if len(cols) == 1:
          fig = px.histogram(df, x = cols[0])
        else:
            raise ValueError("Histogram takes in 1 variable but two were passed")
    elif chart_type == 'bar':
        if len(cols) < 2:
            raise ValueError("Bar chart requires two columns.")
        fig = px.bar(df, x = cols[0], y = cols[1])
    elif chart_type == 'line':
        if len(cols) == 2: 
           fig = px.line(df, x=cols[0], y=cols[1]) 
        else:
            raise ValueError("Line chart requires two columns")
    elif chart_type == 'scatter':
        if len(numeric_cols) < 2:
            raise ValueError("Scatter plot requires two numeric columns.")
        fig = px.scatter(df, x = numeric_cols[0], y = numeric_cols[1])
    
    elif chart_type == 'countplot':
        if len(cols) == 1:
            fig = px.bar(df[cols[0]].value_counts().reset_index(), 
                x= cols[0], 
                y='count',
                title=f'Countplot of {cols[0]}')
        else:
            raise ValueError("Countplot takes 1 argument only")
    
    elif chart_type == 'boxplot':
        if len(cols) == 1:
            fig = px.box(df, y=cols[0], points="all")
        elif len(cols) == 2:
            fig = px.box(df, x=cols[0], y=cols[1], points="all")
            
    return fig.to_html(full_html=False)


def change_column_type(df, col, dtype):
    """Change the data type of a column with error handling."""
    if dtype == 'int':
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('int')
    elif dtype == 'float':
        df[col] = pd.to_numeric(df[col], errors='coerce')
    elif dtype == 'str':
        df[col] = df[col].astype(str)
    else:
        raise ValueError(f"Unsupported dtype: {dtype}")
    return df