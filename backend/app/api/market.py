from fastapi import APIRouter, HTTPException, Query
from data.baostock_provider import data_provider
import datetime
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.get("/index")
async def get_market_index(
    code: str = Query("sh.000001", description="Index code, default is SSE Composite"),
    days: int = Query(90, description="Number of days to look back")
) -> Dict[str, Any]:
    """
    Get market index daily bars (e.g., SSE Composite sh.000001).
    """
    try:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days)
        
        # Format dates for Baostock (YYYY-MM-DD)
        end_str = end_date.strftime("%Y-%m-%d")
        start_str = start_date.strftime("%Y-%m-%d")
        
        df = data_provider.get_daily_bars(code, start_str, end_str)
        
        if df is None or df.empty:
            return {
                "code": code,
                "data": []
            }
            
        # Calculate change and pct_change for the latest day if data exists
        latest_change = 0.0
        latest_pct_change = 0.0
        
        if len(df) > 1:
            last = df.iloc[-1]
            prev = df.iloc[-2]
            latest_change = float(last['close']) - float(prev['close'])
            # Avoid division by zero
            if float(prev['close']) != 0:
                latest_pct_change = (latest_change / float(prev['close'])) * 100
        
        # Convert DataFrame to list of dicts
        # date needs to be string, other numeric fields should be floats
        records = df.to_dict(orient="records")
        
        return {
            "code": code,
            "latest_date": records[-1]['date'] if records else None,
            "latest_close": records[-1]['close'] if records else 0,
            "change": round(latest_change, 2),
            "pct_change": round(latest_pct_change, 2),
            "data": records
        }

    except Exception as e:
        print(f"Error fetching market index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")
