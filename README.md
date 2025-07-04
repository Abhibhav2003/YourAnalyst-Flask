#  YourAnalyst - Smart Data Analysis Dashboard

**YourAnalyst** is an advanced yet easy-to-use web-based data analysis platform built with **Flask**.  
It empowers users to clean, transform, visualize, and analyze datasets without writing a single line of code.

> **Special Feature:** Integrated **Gemini API (Google AI)** for generating AI-powered data insights and automated reports.

---

##  Features

-  Upload & Preview CSV datasets  
-  Manual Data Cleaning:
  - Drop Nulls, Fill Nulls with Mean, Remove Duplicates  
  - Type Conversion (int, float, string)  
-  Data Transformations:
  - Normalization & Standardization  
  - Encoding Categorical Data  
  - PCA & Clustering
-  Statistical Analysis:
  - Basic Stats, Outlier Detection, Correlation, Covariance
-  Visualizations:
  - Histogram, Bar, Line, Scatter (Auto-handles categorical/numeric)
  - Dashboard-style HTML downloads for your charts
-  AI Analysis:
  - Generate automatic data reports using Gemini API
-  History Tracking (Undo last action)
-  Download Options:
  - Modified CSV
  - Charts as standalone Dashboard HTML

---

##  Powered By

- **Flask** (Python Backend)
- **Pandas** & **NumPy** (Data Analysis)
- **Matplotlib** (Visualization)
- **scikit-learn** (ML: PCA, Clustering)
- **Google Gemini API** (AI-Powered Reports)

---

##  Screenshots

| Dashboard Page | AI Analysis Report |
|----------------|-------------------|
| ![Dashboard Screenshot](static/screenshots/dashboard.png) | ![AI Report Screenshot](static/screenshots/ai_report.png) |

---

##  Setup Instructions

Clone Repository
```
git clone https://github.com/yourusername/youranalyst.git
cd youranalyst
```

## Create Virtual Environment & Install Dependencies
```
python -m venv venv
venv\Scripts\activate # On Mac: source venv/bin/activate   
pip install -r requirements.txt
```

## Run the App
```
python run.py
```

# Deployment
```
Link : https://youranalyst.onrender.com/
```