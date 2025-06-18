from bs4 import BeautifulSoup
import requests
import pandas as pd
from flask import flash

def TableRows(webpage):
    soup = BeautifulSoup(webpage.content, "html.parser")
    list_of_tables = list(soup.find_all("table"))
    list_of_trs = []
    for i in list_of_tables:
        list_of_trs.append(i.find_all("tr"))
    return list_of_trs

def Extract(URL, HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/132.0.0.0 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'}):
    webpage = requests.get(URL, headers=HEADERS)
    if webpage.status_code == 200:
        return TableRows(webpage)
    else:
        return flash(webpage.status_code,category='error')

def Scrape(url):
    result = {}
    m = 1
    list_of_trs = Extract(url)
    if list_of_trs:
        for k in list_of_trs:
            headers = []
            rows = []
            for i in k:
                ths = [th.text.strip() for th in i.find_all("th")]
                if ths:
                    headers = ths 
                else:
                    data = [td.text.strip() for td in i.find_all("td")]
                    if data:
                        rows.append(data)
            index = "table" + str(m)
            result[index] = (headers, rows)
            m += 1
    return result

def CreateDf(result):
    dict_dfs = {}
    for k in result:
        headers, rows = result[k]
        if headers: 
            df = pd.DataFrame(rows, columns = headers)
        else: 
            df = pd.DataFrame(rows)
        dict_dfs[k] = df
    return dict_dfs

