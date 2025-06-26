# code/alpha_api.py

import requests
import pandas as pd
from datetime import datetime

API_KEY = "6ENFS17A99N08KAH"

def get_news(ticker):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "apikey": API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()

    if "feed" not in data:
        print("[ERROR]", data)
        return pd.DataFrame()

    df = pd.DataFrame([{
        "title": a.get("title", ""),
        "link": a.get("url", ""),
        "time_published": a.get("time_published", ""),
        "summary": a.get("summary", ""),
        "source": a.get("source", "")
    } for a in data["feed"]])

    # 🔧 FIX: Correct time format with seconds
    df['Date Time'] = pd.to_datetime(df['time_published'], format="%Y%m%dT%H%M%S")
    df['title + link'] = df.apply(lambda row: f'<a href="{row["link"]}" target="_blank">{row["title"]}</a>', axis=1)
    return df



def get_price_history(ticker, earliest_datetime):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": ticker,
        "interval": "60min",
        "outputsize": "full",
        "apikey": API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()

    if "Time Series (60min)" not in data:
        print("[ERROR]", data)
        return pd.DataFrame()

    time_series = data["Time Series (60min)"]
    df = pd.DataFrame.from_dict(time_series, orient='index')
    df.index = pd.to_datetime(df.index)
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df = df[df.index >= earliest_datetime]
    df = df.sort_index()

    df = df.rename_axis("Date Time").reset_index()
    df["Price"] = df["Close"].astype(float)

    return df
