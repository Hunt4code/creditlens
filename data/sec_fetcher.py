import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time

load_dotenv()

HEADERS = {
    "User-Agent": "creditlens hrishi@example.com"
}

def get_cik_from_ticker(ticker:str)->str:

    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url,headers=HEADERS)
    data = response.json()

    ticker_upper =  ticker.upper()
    for key,company in data.items():
        if company["ticker"] == ticker_upper:

            cik = str(company["cik_str"]).zfill(10)
            return cik
        
    raise ValueError(f"Ticker {ticker} not found in SEC database")

def get_company_facts(cik:str)->dict:

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url,headers=HEADERS)

    if response.status_code != 200:
        raise ValueError(f"Could not fetch data for cik : {cik}")
    
    time.sleep(0.5)
    
    return response.json()

def extract_financial_metric(facts:dict, concept:str)-> pd.DataFrame:

    try:

        data = facts["facts"]["us-gaap"][concept]["units"]["USD"]
        df = pd.DataFrame(data)

        df = df[df["form"] == "10-K"]

        df = df[["end", "val"]].rename(columns={"end": "date", "val": concept})
        df = df.sort_values("date").drop_duplicates(subset="date", keep="last")
    
        return df

    except KeyError:
        print(f"Warning: concept {concept} not found for this company")
        return pd.DataFrame()
    

def get_financial_snapshot(ticker:str)->pd.DataFrame:

    print(f"Fetching financial snapshot for {ticker}...")

    cik = get_cik_from_ticker(ticker)
    print(f"  CIK: {cik}")

    facts = get_company_facts(cik)

    concepts = [
        "Assets",
        "Liabilities",
        "StockholdersEquity",
        "RetainedEarningsAccumulatedDeficit",
        "OperatingIncomeLoss",
        "InterestExpense",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "CashAndCashEquivalentsAtCarryingValue"
    ]

    base = extract_financial_metric(facts,"Assets")

    if base.empty:
        raise ValueError(f"No asset data found for {ticker}")
    
    for concept in concepts[1:]:
        df = extract_financial_metric(facts,concept)
        if not df.empty:
            base = base.merge(df,on="date",how="left")

    base["ticker"] = ticker
    base = base.tail(5).reset_index(drop=True)

    print(f"  Got {len(base)} years of data")
    return base       


if __name__ == "__main__":
    print("Testing SEC data pipeline...")
    
    snapshot = get_financial_snapshot("AAPL")
    print("\nFinancial Snapshot:")
    print(snapshot.to_string())

