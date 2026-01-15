import logging
import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Query

from data.baostock_provider import data_provider

logger = logging.getLogger(__name__)
router = APIRouter()

# 简单的缓存装饰器用于市场数据 (1小时)
_cache_timeout = 3600


def _get_cache_key(code: str, start_date: str, end_date: str) -> str:
    """生成缓存键"""
    return f"{code}:{start_date}:{end_date}"


@router.get("/index")
async def get_market_index(
    code: str = Query("sh.000001", description="Index code, default is SSE Composite"),
    days: int = Query(90, description="Number of days to look back", ge=1, le=365),
) -> Dict[str, Any]:
    """
    获取市场指数日线行情数据 (例如上证综指)
    
    Args:
        code: 指数代码 (默认: sh.000001)
        days: 回溯天数 (1-365)
    
    Returns:
        包含指数数据和最新价格变化的JSON
    """
    try:
        # 验证代码格式
        if not isinstance(code, str) or not code.strip():
            raise ValueError("Invalid code format")
        
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days)
        
        # 格式化日期 (YYYY-MM-DD)
        end_str = end_date.strftime("%Y-%m-%d")
        start_str = start_date.strftime("%Y-%m-%d")
        
        logger.info(f"Fetching market index: {code} from {start_str} to {end_str}")
        
        df = data_provider.get_daily_bars(code, start_str, end_str)
        
        if df is None or df.empty:
            logger.warning(f"No data found for code: {code}")
            return {
                "code": code,
                "data": [],
                "message": "No data available",
            }
        
        # 计算最新日期的变化
        latest_change = 0.0
        latest_pct_change = 0.0
        
        if len(df) > 1:
            try:
                last = df.iloc[-1]
                prev = df.iloc[-2]
                latest_close = float(last.get("close", 0))
                prev_close = float(prev.get("close", 0))
                
                latest_change = latest_close - prev_close
                
                if prev_close != 0:
                    latest_pct_change = (latest_change / prev_close) * 100
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Error calculating changes: {e}")
        
        # 转换为字典列表
        records = df.to_dict(orient="records")
        
        return {
            "code": code,
            "latest_date": records[-1].get("date") if records else None,
            "latest_close": float(records[-1].get("close", 0)) if records else 0.0,
            "change": round(latest_change, 2),
            "pct_change": round(latest_pct_change, 2),
            "total_records": len(records),
            "data": records,
        }
    
    except ValueError as e:
        logger.error(f"Validation error for market index: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching market index {code}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch market data: {str(e)}"
        )


@router.get("/hs300-list")
async def get_hs300_list(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
) -> Dict[str, Any]:
    """
    获取沪深300成分股列表
    
    Args:
        date: 查询日期 (YYYY-MM-DD)
    
    Returns:
        股票列表
    """
    try:
        logger.info(f"Fetching HS300 list for {date}")
        
        stocks = data_provider.get_hs300_stocks(date)
        
        if not stocks:
            logger.warning(f"No HS300 stocks found for {date}")
            return {"date": date, "stocks": [], "total": 0}
        
        return {
            "date": date,
            "stocks": stocks,
            "total": len(stocks),
        }
    
    except Exception as e:
        logger.error(f"Error fetching HS300 list for {date}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch HS300 list: {str(e)}")


@router.get("/status")
async def get_market_status() -> Dict[str, Any]:
    """
    获取市场状态
    
    Returns:
        市场开放状态和最后更新时间
    """
    try:
        today = datetime.date.today()
        weekday = today.weekday()
        
        # 周一-周五 (0-4)
        is_trading_day = weekday < 5
        
        return {
            "date": today.isoformat(),
            "weekday": weekday,
            "is_trading_day": is_trading_day,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting market status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get market status")
