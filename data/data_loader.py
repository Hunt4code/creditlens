import pandas as pd
from sec_fetcher import get_financial_snapshot
from fmp_fetcher import get_complete_fmp_data


def load_company_data(ticker: str) -> pd.DataFrame:
    
    print(f"\nLoading data for {ticker}...")

    
    sec_data = get_financial_snapshot(ticker)
    fmp_data = get_complete_fmp_data(ticker)

    
    sec_data["year"] = pd.to_datetime(sec_data["date"]).dt.year

    df = sec_data.merge(
        fmp_data,
        on="year",
        how="left",
        suffixes=("_sec", "_fmp")
    )

    if "InterestExpense" in df.columns and "interestExpense" in df.columns:
        df["interest_expense"] = df["InterestExpense"].fillna(
            df["interestExpense"]
        )
    elif "InterestExpense" in df.columns:
        df["interest_expense"] = df["InterestExpense"]
    else:
        df["interest_expense"] = df["interestExpense"]

    df = df.rename(columns={
        "Assets": "total_assets",
        "Liabilities": "total_liabilities",
        "StockholdersEquity": "stockholders_equity",
        "RetainedEarningsAccumulatedDeficit": "retained_earnings",
        "OperatingIncomeLoss": "operating_income",
        "CashAndCashEquivalentsAtCarryingValue": "cash",
        "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue_sec"
    })

    if "revenue" in df.columns:
        df["total_revenue"] = df["revenue"]
    elif "revenue_sec" in df.columns:
        df["total_revenue"] = df["revenue_sec"]

    # Keep ticker clean
    if "ticker_sec" in df.columns:
        df["ticker"] = df["ticker_sec"]
    elif "ticker_x" in df.columns:
        df["ticker"] = df["ticker_x"]

    columns_to_keep = [
        "ticker",
        "year",
        "total_assets",
        "total_liabilities",
        "stockholders_equity",
        "retained_earnings",
        "operating_income",
        "cash",
        "total_revenue",
        "interest_expense",
        "ebitda",
        "netIncome",
        "marketCap",
        "currentRatio",
        "operatingProfitMargin",
        "netProfitMargin"
    ]

    available = [c for c in columns_to_keep if c in df.columns]
    df = df[available]

    df = df.sort_values("year").reset_index(drop=True)

    print(f"  Merged dataset: {len(df)} years, {len(df.columns)} columns")
    print(f"  Columns: {list(df.columns)}")

    return df


if __name__ == "__main__":
    df = load_company_data("AAPL")
    print("\nFinal merged DataFrame:")
    print(df.to_string())