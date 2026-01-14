from fastapi import APIRouter, HTTPException, Query
from data.baostock_provider import data_provider
import datetime
import pandas as pd
from typing import Dict, Any, List

router = APIRouter()

@router.get("/{code}")
async def get_stock_detail(
    code: str,
    days: int = Query(250, description="Number of days to look back")
) -> Dict[str, Any]:
    """
    Get detailed stock data including K-lines and calculated indicators (MA, RSI).
    """
    try:
        end_date = datetime.date.today()
        # Ensure we have enough data for MA60 and RSI
        start_date = end_date - datetime.timedelta(days=days + 60)
        
        end_str = end_date.strftime("%Y-%m-%d")
        start_str = start_date.strftime("%Y-%m-%d")
        
        df = data_provider.get_daily_bars(code, start_str, end_str)
        
        if df is None or df.empty:
             raise HTTPException(status_code=404, detail="Stock data not found")

        # --- Indicator Calculation ---
        # Ensure numeric types
        numeric_cols = ['close', 'volume']
        for col in numeric_cols:
             df[col] = pd.to_numeric(df[col], errors='coerce')

        # Moving Averages
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # RSI Calculation (Simple 14-day)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        # Avoid division by zero
        rs = rs.fillna(0)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Trim to requested days (approx)
        # We fetched extra for calculation, now we slice the last 'days' rows (or actual dates if preferred)
        # Here we just take the tail corresponding to 'days' roughly, 
        # but since 'days' is calendar days, let's just return what we have (cleaned)
        # or better, just return the valid part.
        
        df = df.fillna(0) # Replace NaNs (especially at start) with 0 for JSON safety
        
        records = df.to_dict(orient="records")
        
        # Get latest metrics
        last_row = records[-1]
        
        return {
            "code": code,
            "info": {
                "latest_date": last_row['date'],
                "close": last_row['close'],
                "peTTM": last_row.get('peTTM', 0),
                "pbMRQ": last_row.get('pbMRQ', 0),
                "turn": last_row.get('turn', 0),
                "volume": last_row['volume']
            },
            "data": records
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching stock detail for {code}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
