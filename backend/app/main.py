from app.parser import parse_transactions_csv
from fastapi import FastAPI
from fastapi import UploadFile, File
import pandas as pd
from io import BytesIO
import numpy as np
import math

app = FastAPI()
@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/upload/nordnet/transactions")
async def upload_transactions(file: UploadFile = File(...)):
    raw = await file.read()

    # Parse once
    df_out = parse_transactions_csv(raw).copy()

    # Make dates JSON-friendly
    df_out["booking_date"] = df_out["booking_date"].dt.date.astype(str)
    df_out["trade_date"] = df_out["trade_date"].dt.date.astype(str)

    # Preview (JSON-safe)
    preview = (
        df_out.head(200)
          .astype(object)
          .replace({np.nan: None})
          .to_dict(orient="records")
    )

    # Useful KPIs right away
    total_deposits = df_out.loc[df_out["category"] == "cash", "amount"].sum()
    total_buys = df_out.loc[df_out["type"] == "KJØPT", "gross"].sum()
    cash_left = total_deposits - total_buys

    return {
        "ok": True,
        "filename": file.filename,
        "rows": int(df_out.shape[0]),
        "preview": preview,
        "kpis": {
            "total_deposits": float(total_deposits) if pd.notna(total_deposits) else 0.0,
            "total_buys": float(total_buys) if pd.notna(total_buys) else 0.0,
            "cash_left": float(cash_left) if pd.notna(cash_left) else 0.0,
        },
    }

@app.post("/api/upload/nordnet/holdings")
async def upload_holdings(file: UploadFile = File(...)):
    raw = await file.read()
    
    df = None
    errors = []
    
    for encoding in ["utf-16", "utf-8-sig", "latin-1"]:
        for sep in [",", ";", "\t"]:
            try:
                df = pd.read_csv(BytesIO(raw), encoding=encoding, sep=sep)
                if df.shape[1] >= 2:
                    break
            except Exception as e:
                errors.append(f"Failed to decode with {encoding} and separator {sep}: {str(e)}")
                df = None
        if df is not None:
            break
        
    if df is None:
        return {"ok": False, "error": "Failed to parse CSV", "tried": errors[:5]}
    
    # lag en JSON-safe preview
    preview_df = df.head(5).copy()

    # tving object så None kan eksistere
    preview_df = preview_df.astype(object)

    # erstatt NaN/NaT/inf med None
    preview_df = preview_df.replace({np.nan: None})
    preview_df = preview_df.replace([np.inf, -np.inf], None)

    sample = preview_df.to_dict(orient="records")
    return {
    "ok": True,
    "filename": file.filename,
    "rows": int(df.shape[0]),
    "cols": int(df.shape[1]),
    "columns": list(df.columns),
    "sample": sample,
}