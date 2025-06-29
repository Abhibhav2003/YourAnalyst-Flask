import pandas as pd
import numpy as np
import scipy as scpy


def DropDuplicates(df,inplc):
    if inplc:
      df.drop_duplicates(inplace=inplc)
      return df
    
    else:
      new_df = df.drop_duplicates()
      return new_df

def overview(df):
    df.info()

def DropNa(df,inplc):
    if inplc:
      df.dropna(inplace=inplc)
      return df
    
    else:
      new_df = df.dropna()
      return new_df

def Avg(df,col):
    if type(df[col]) == 'int' or type(df[col]) == 'float'):
       return np.mean(df[col])
    
    else:
        print("Mean is not applicable on this Column")

def Median(df,col):
    if type(df[col]) == 'int' or type(df[col]) == 'float':
        return np.median(df[col])
    
    else:
        print("Median is not applicable on this Column")

def IQR(df,col):
    if type(df[col] == 'int' or df[col] == 'float'):
       iqr = df[col].quantile(0.75) - df[col].quantile(0.25)
       return iqr
    
    else:
        print("Error! IQR isn't applicable")
        
def FillNa():
    pass


def Outlier():
    pass

def Normalize():
    pass

def Standardize():
    pass

def Correlation():
    pass

def Covariance():
    pass

def GroupBy():
    pass

def Encoding():
    pass

def OneHotEncoding():
    pass

def LinearRegression():
    pass

def Graphs(chart_type):
    pass
