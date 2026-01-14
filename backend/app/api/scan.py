from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import StreamingResponse
import json
import time

from core.engine import AnalysisEngine
from core.strategies_registry import get_strategy
from data.baostock_provider import data_provider

router = APIRouter()

class ScanRequest(BaseModel):
    date: str
    strategies: List[str]
    pool_type: str = "hs300"  # hs300, test, custom
    custom_pool: Optional[List[str]] = None

def scan_generator(request: ScanRequest):
    # 1. Determine Stock Pool
    pool = []
    if request.pool_type == "custom":
        pool = request.custom_pool or []
    elif request.pool_type == "test":
        # First 20 of HS300 for testing
        full_pool = data_provider.get_hs300_stocks(request.date)
        pool = full_pool[:20] if full_pool else []
    else:
        # Default HS300
        pool = data_provider.get_hs300_stocks(request.date)
    
    if not pool:
        # Yield an error or empty message
        # In NDJSON, we can yield a meta object or just stop.
        # Let's yield a metadata object first.
        yield json.dumps({"type": "meta", "total": 0, "message": "No stocks in pool"}) + "\n"
        return

    # Yield metadata
    yield json.dumps({"type": "meta", "total": len(pool), "message": "Starting scan"}) + "\n"

    # 2. Setup Engine
    selected_strategies = [get_strategy(k) for k in request.strategies]
    # Filter out None if any invalid keys were passed
    selected_strategies = [s for s in selected_strategies if s is not None]
    
    if not selected_strategies:
         yield json.dumps({"type": "error", "message": "No valid strategies selected"}) + "\n"
         return

    engine = AnalysisEngine(selected_strategies)

    # 3. Run Scan
    # We iterate and yield results
    for i, item in enumerate(pool):
        try:
            # Handle item type
            if isinstance(item, dict):
                code = item.get('code')
                name = item.get('name', '')
            else:
                code = item
                name = ''

            # We can optionally yield progress updates every N items if needed,
            # but usually the client counts the received items or we send a "progress" event.
            # Sending "progress" every item might be too much traffic if we just want results,
            # but for a "scanner", knowing what is being scanned is nice.
            
            # Let's just yield matches to keep it clean, 
            # OR yield a progress event every 10 stocks.
            if i % 10 == 0:
                 yield json.dumps({"type": "progress", "current": i, "total": len(pool)}) + "\n"

            result = engine.scan_one(code, request.date)
            if result:
                # Inject name if available
                if name:
                    result['name'] = name

                # Found a match!
                response_item = {
                    "type": "match",
                    "data": result
                }
                yield json.dumps(response_item) + "\n"
                
        except Exception as e:
            # Log error but continue
            code_str = item.get('code') if isinstance(item, dict) else item
            print(f"Error scanning {code_str}: {e}")
            yield json.dumps({"type": "error", "code": code_str, "message": str(e)}) + "\n"

    # Final Done message
    yield json.dumps({"type": "done", "total_scanned": len(pool)}) + "\n"


@router.post("/")
async def scan_stocks(request: ScanRequest):
    """
    Run a stock scan based on selected strategies.
    Returns a StreamingResponse (NDJSON) to handle long-running processes.
    
    Format:
    - {"type": "meta", "total": 300, ...}
    - {"type": "progress", "current": 10, ...}
    - {"type": "match", "data": {...}}
    - {"type": "done", ...}
    """
    return StreamingResponse(scan_generator(request), media_type="application/x-ndjson")
