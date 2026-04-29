import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time

load_dotenv()


FMP_API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable"


def get_financial_ratios(ticker:str,limit:int=5) -> pd.DataFrame:

    url = f"{BASE_URL}/ratios"
    params = {
        "symbol":ticker,
        "limit" : limit,
        "apikey" : FMP_API_KEY
    }

    response = requests.get(url,params = params)

    if response.status_code !=200:
        raise ValueError(f"FMP API error: {response.status_code}")
    
    data = response.json()

    if not data:
        raise ValueError(f"No ratio data found for : {ticker}")
    
    df = pd.DataFrame(data)

    columns_to_keep =[
        "date",
        "debtEquityRatio",
        "currentRatio",
        "quickRatio",
        "interestCoverage",
        "returnOnAssets",
        "returnOnEquity",
        "debtRatio",
        "operatingProfitMargin",
        "netProfitMargin"
    ]

    available_columns = [c for c in columns_to_keep if c in df.columns]
    df = df[available_columns]

    df["ticker"] = ticker

    df = df.sort_values("date").reset_index(drop=True)
    
    return df

def get_key_metrics(ticker:str,limit:int=5) -> pd.DataFrame:

    url = f"{BASE_URL}/key-metrics"
    params = {
        "symbol":ticker,
        "limit": limit,
        "apikey": FMP_API_KEY
    }

    response = requests.get(url,params = params)

    if response.status_code !=200:
        raise ValueError(f"FMP API error : {response.status_code}")
    
    data = response.json()

    if not data:
        raise ValueError(f"No key metrics found for: {ticker} ")
    
    df = pd.DataFrame(data)

    columns_to_keep =[
        "date",
        "revenuePerShare",
        "netIncomePerShare",
        "freeCashFlowPerShare",
        "bookValuePerShare",
        "debtToEquity",
        "interestCoverage",
        "marketCap",
        "enterpriseValue",
        "peRatio",
        "priceToBookRatio"
     ]
    
    available_columns = [c for c in columns_to_keep if c in df.columns]
    df = df[available_columns]

    df["ticker"] = ticker
    df = df.sort_values("date").reset_index(drop=True)

    return df

def get_income_statement(ticker:str,limit:int=5) -> pd.DataFrame:

    url = f"{BASE_URL}/income-statement"
    params = {
        "symbol":ticker,
        "limit": limit,
        "apikey": FMP_API_KEY,
        "period": "annual"
    }

    response = requests.get(url,params = params)

    if response.status_code !=200:
        raise ValueError(f"FMP API error : {response.status_code}")
    
    data = response.json()

    if not data:
        raise ValueError(f"No key metrics found for: {ticker} ")
    
    df = pd.DataFrame(data)

    columns_to_keep =[
        "date",
        "revenue",
        "ebitda",
        "operatingIncome",
        "interestExpense",
        "netIncome",
        "eps"
     ]
    
    available_columns = [c for c in columns_to_keep if c in df.columns]
    df = df[available_columns]

    df["ticker"] = ticker
    df = df.sort_values("date").reset_index(drop=True)

    return df

def get_complete_fmp_data(ticker:str,limit:int=5) -> pd.DataFrame:

    ratios = get_financial_ratios(ticker,limit)
    metrics = get_key_metrics(ticker,limit)
    income = get_income_statement(ticker,limit)

    ratios["year"] = pd.to_datetime(ratios["date"]).dt.year
    metrics["year"] = pd.to_datetime(metrics["date"]).dt.year
    income["year"] = pd.to_datetime(income["date"]).dt.year

    metrics = metrics.drop(columns=["date","ticker"])
    income = income.drop(columns=["date","ticker"])

    df = ratios.merge(metrics,on="year",how="left")
    df = df.merge(income,on="year",how="left")

    df.sort_values("year").reset_index(drop=True)

    print(f" Complete FMP data: {len(df)} years, {len(df.columns)} columns")

    return df

if __name__ == "__main__":
    print("Testing FMP data pipeline...")

    ticker = "AAPL"
    
    print("\n--- Complete FMP Data ---")
    complete = get_complete_fmp_data(ticker)
    print(complete.to_string())

