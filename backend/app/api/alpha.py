from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import inspect
from data.baostock_provider import data_provider
from alpha.factors.gtja191 import GTJA191
import datetime

router = APIRouter()

@router.get("/factors", response_model=List[Dict[str, str]])
async def get_alpha_factors():
    """
    Get list of available alpha factors (currently GTJA191).
    """
    factors = []
    # Inspect GTJA191 class for alpha methods
    for name, method in inspect.getmembers(GTJA191, predicate=inspect.isfunction):
        if name.startswith("alpha"):
            # Try to extract docstring as description
            doc = inspect.getdoc(method)
            desc = "GTJA191 Alpha Factor"
            if doc:
                lines = doc.split('\n')
                # Try to find a meaningful description line
                for line in lines:
                    if "含义:" in line:
                        desc = line.replace("含义:", "").strip()
                        break
            
            factors.append({
                "key": name,
                "name": name.upper(),
                "description": desc,
                "category": "Momentum/Volatility" # General categorization
            })
    
    # Sort by key
    factors.sort(key=lambda x: x['key'])
    return factors

@router.get("/calculate")
async def calculate_alpha(
    code: str = Query(..., description="Stock code (e.g., sh.600000)"),
    factor: str = Query(..., description="Factor key (e.g., alpha001)"),
    days: int = Query(730, description="Number of days of history to use")
) -> Dict[str, Any]:
    """
    Calculate a specific alpha factor for a stock.
    """
    try:
        # 1. Fetch Data
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days)
        
        df = data_provider.get_daily_bars(
            code, 
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {code}")
            
        # Ensure numeric types
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col])
        
        # 2. Initialize Engine
        engine = GTJA191(df)
        
        # 3. Calculate Factor
        if not hasattr(engine, factor):
            raise HTTPException(status_code=400, detail=f"Factor {factor} not found")
            
        calc_func = getattr(engine, factor)
        result_series = calc_func()
        
        # 4. Format Result
        # Combine date, price, and factor value
        result_df = pd.DataFrame({
            "date": df['date'],
            "close": df['close'],
            "value": result_series
        })
        
        # Replace Infinity with NaN
        result_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        # Filter out NaNs (common in beginning of series due to rolling windows)
        result_df = result_df.dropna()
        
        # Limit to last 100 points for chart clarity if list is too long
        if len(result_df) > 500:
             result_df = result_df.tail(500)
             
        return {
            "code": code,
            "factor": factor,
            "data": result_df.to_dict(orient="records")
        }

    except Exception as e:
        print(f"Error calculating alpha: {e}")
        raise HTTPException(status_code=500, detail=str(e))