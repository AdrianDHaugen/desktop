import pandas as pd
from io import BytesIO  
import numpy as np
import math

def to_float_no(x):
    """Converts 1 234,56 / 1234,56 / 1234.56 / None to float, returns None if conversion fails."""
    if x is None:
        return None
    if isinstance(x, (int, float, np.number)):
        if pd.isna(x):
            return None 
        return float(x)
    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return None
    s = s.replace(" ", "").replace("\u00a0", "")  # Remove spaces and non-breaking spaces
    s = s.replace(",", ".")  # Replace comma with dot for decimal
    try:
        return float(s)
    except ValueError:
        return None
    
def parse_transactions_csv(raw):
    """Parses a CSV file of transactions, trying multiple encodings and separators. Returns a DataFrame or raises an error."""
    df = None
    for encoding in ["utf-16", "utf-8-sig", "latin-1"]:
        for sep in [";", ",", "\t"]:
            try:
                df = pd.read_csv(BytesIO(raw), encoding=encoding, sep=sep)
                if df.shape[1] >= 10:
                    break
            except Exception:
                df = None
        if df is not None:
            break
    if df is None:
        raise ValueError("Could not parse CSV with any of the tried encodings and separators.")
    
    # Standardize column names
    out = df.copy()
    out["booking_date"] = pd.to_datetime(out["Bokføringsdag"], errors="coerce")
    out["trade_date"] = pd.to_datetime(out["Handelsdag"], errors="coerce")
    out["type"] = df["Transaksjonstype"].astype(str)
    out["name"] = df["Verdipapir"]
    out["isin"] = df["ISIN"]
    
    out["qty"] = df["Antall"].map(to_float_no)
    out["price"] = df["Kurs"].map(to_float_no)
    out["amount"] = df["Beløp"].map(to_float_no)      # Negative for buys (cash outflow), positive for sells (cash inflow)
    out["gross"] = df["Kjøpsverdi"].map(to_float_no)  # Gross purchase value before fees (positive amount)
    out["fee"] = df["Kurtasje"].map(to_float_no)    
    # classify as trade or cash (dividend, interest, fee)
    out["category"] = np.where(out["isin"].isna(), "cash", "trade")

    # Clean up and sort
    out = out.sort_values("booking_date")
    return out