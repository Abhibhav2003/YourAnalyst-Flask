import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

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
    return df[numeric_cols].describe().to_dict()

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
    """Standardize selected numeric columns (Z-score Standardization)."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

def encode_categorical(df, cols):
    """Encode categorical columns with Label Encoding."""
    for col in cols:
        df[col] = LabelEncoder().fit_transform(df[col].astype(str))
    return df

def apply_pca(df, cols, n_components=2):
    """Apply PCA on selected numeric columns."""
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    if not numeric_cols:
        raise ValueError("No numeric columns selected for PCA.")
    pca = PCA(n_components=min(n_components, len(numeric_cols)))
    components = pca.fit_transform(df[numeric_cols])
    for i in range(components.shape[1]):
        df[f'PCA_{i+1}'] = components[:, i]
    return df

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
    """Generate a plot and return base64-encoded PNG image string."""
    sns.set_style('dark')
    plt.figure(figsize=(6, 4))

    if not cols:
        raise ValueError("No columns selected for plotting.")
    
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]

    if chart_type == 'histogram':
        if len(cols) == 1:
            df[cols[0]].value_counts().plot(kind='bar')
            plt.xlabel(cols[0])
            plt.ylabel("Frequency")
        else:
            if not numeric_cols:
                raise ValueError("No numeric columns available for histogram.")
            df[numeric_cols].hist(bins=20)
    elif chart_type == 'bar':
        if len(cols) == 1:
            df[cols[0]].value_counts().plot(kind='bar')
            plt.xlabel(cols[0])
            plt.ylabel("Frequency")
        else:
            if not pd.api.types.is_numeric_dtype(df[cols[0]]) and not pd.api.types.is_numeric_dtype(df[cols[1]]):
                raise ValueError(f"Column '{cols[1]}' must be numeric for bar plot.")
            plt.bar(df[cols[0]].astype(str), df[cols[1]])
            plt.xlabel(cols[0])
            plt.ylabel(cols[1])
    elif chart_type == 'line':
        if len(cols) == 1:
            df[cols[0]].value_counts().sort_index().plot(kind='line')
            plt.xlabel(cols[0])
            plt.ylabel("Frequency")
        else:
            df[numeric_cols].plot()
    elif chart_type == 'scatter':
        if len(numeric_cols) >= 2:
            plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]])
            plt.xlabel(numeric_cols[0])
            plt.ylabel(numeric_cols[1])
        else:
            raise ValueError("Scatter plot requires at least two numeric columns.")
    else:
        raise ValueError("Unsupported chart type or insufficient columns.")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    return encoded

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