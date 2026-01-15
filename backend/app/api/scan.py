import logging
import json
from typing import List, Optional, Dict, Any, Generator

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from fastapi.responses import StreamingResponse

from core.engine import AnalysisEngine
from core.strategies_registry import get_strategy
from data.baostock_provider import data_provider

logger = logging.getLogger(__name__)
router = APIRouter()


class ScanRequest(BaseModel):
    """扫描请求模型"""
    
    date: str = Field(..., description="扫描日期 (YYYY-MM-DD)")
    strategies: List[str] = Field(..., min_length=1, description="策略列表")
    pool_type: str = Field(
        "hs300",
        description="股票池类型: hs300 (沪深300), zz1000 (中证1000), test (测试20只), custom (自定义)",
        pattern="^(hs300|zz1000|test|custom)$",
    )
    custom_pool: Optional[List[str]] = Field(
        None, description="自定义股票池 (pool_type=custom时必须提供)"
    )
    
    @validator("date")
    def validate_date(cls, v):
        """验证日期格式"""
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    @validator("strategies")
    def validate_strategies(cls, v):
        """验证策略列表"""
        if not v or len(v) == 0:
            raise ValueError("At least one strategy must be selected")
        return v


def scan_generator(request: ScanRequest) -> Generator[str, None, None]:
    """
    扫描生成器 - 流式返回扫描结果 (NDJSON格式)
    
    Yields:
        {"type": "meta", "total": 300, ...}
        {"type": "progress", "current": 10, "total": 300, "percentage": 3.3}
        {"type": "match", "data": {...}}
        {"type": "error", "code": "sh.600519", "message": "..."}
        {"type": "done", "total_scanned": 300, "total_matches": 25}
    """
    
    try:
        # 1. 确定股票池
        pool = []
        
        if request.pool_type == "custom":
            if not request.custom_pool:
                yield json.dumps({
                    "type": "error",
                    "message": "Custom pool is required when pool_type=custom"
                }) + "\n"
                return
            
            pool = request.custom_pool
            logger.info(f"Using custom pool with {len(pool)} stocks")
        
        elif request.pool_type == "test":
            # 仅使用20只股票进行快速测试
            full_pool = data_provider.get_hs300_stocks(request.date)
            pool = full_pool[:20] if full_pool else []
            logger.info(f"Using test pool with {len(pool)} stocks")
        
        elif request.pool_type == "zz1000":
            pool = data_provider.get_zz1000_stocks(request.date)
            logger.info(f"Using ZZ1000 pool with {len(pool)} stocks")
        
        else:  # hs300 (默认)
            pool = data_provider.get_hs300_stocks(request.date)
            logger.info(f"Using HS300 pool with {len(pool)} stocks")
        
        if not pool:
            yield json.dumps({
                "type": "error",
                "message": f"No stocks found in pool: {request.pool_type}"
            }) + "\n"
            return
        
        # 2. 发送元数据
        yield json.dumps({
            "type": "meta",
            "total": len(pool),
            "message": f"Starting scan with {len(request.strategies)} strategies",
            "date": request.date,
            "strategies": request.strategies,
        }) + "\n"
        
        # 3. 初始化引擎
        selected_strategies = [get_strategy(k) for k in request.strategies]
        selected_strategies = [s for s in selected_strategies if s is not None]
        
        if not selected_strategies:
            yield json.dumps({
                "type": "error",
                "message": f"No valid strategies found: {request.strategies}"
            }) + "\n"
            return
        
        logger.info(f"Using {len(selected_strategies)} strategies")
        engine = AnalysisEngine(selected_strategies)
        
        # 4. 执行扫描
        total_matches = 0
        
        for i, item in enumerate(pool):
            try:
                # 提取股票代码和名称
                if isinstance(item, dict):
                    code = item.get("code")
                    name = item.get("name", "")
                else:
                    code = item
                    name = ""
                
                # 每10只股票发送进度更新
                if i % 10 == 0 and i > 0:
                    percentage = round((i / len(pool)) * 100, 1)
                    yield json.dumps({
                        "type": "progress",
                        "current": i,
                        "total": len(pool),
                        "percentage": percentage,
                    }) + "\n"
                
                # 执行扫描
                result = engine.scan_one(code, request.date)
                
                if result:
                    # 如果有名称，注入结果
                    if name:
                        result["name"] = name
                    
                    total_matches += 1
                    yield json.dumps({
                        "type": "match",
                        "data": result,
                    }) + "\n"
                    logger.debug(f"Match found: {code}")
            
            except Exception as e:
                code_str = item.get("code") if isinstance(item, dict) else str(item)
                logger.warning(f"Error scanning {code_str}: {e}")
                yield json.dumps({
                    "type": "error",
                    "code": code_str,
                    "message": str(e),
                }) + "\n"
        
        # 5. 发送完成信息
        logger.info(f"Scan completed: {total_matches} matches found from {len(pool)} stocks")
        yield json.dumps({
            "type": "done",
            "total_scanned": len(pool),
            "total_matches": total_matches,
            "message": f"Scan completed successfully",
        }) + "\n"
    
    except Exception as e:
        logger.error(f"Scan generator error: {e}", exc_info=True)
        yield json.dumps({
            "type": "error",
            "message": f"Fatal error during scan: {str(e)}",
        }) + "\n"


@router.post("/")
async def scan_stocks(request: ScanRequest) -> StreamingResponse:
    """
    执行股票扫描
    
    使用流式响应 (NDJSON) 处理长时间运行的扫描任务
    
    Args:
        request: 扫描请求
    
    Returns:
        NDJSON 流式响应
    
    Example:
        ```
        {
            "date": "2024-01-15",
            "strategies": ["ma", "vol"],
            "pool_type": "hs300"
        }
        ```
    """
    logger.info(f"Scan request: {request.strategies} on {request.date} (pool: {request.pool_type})")
    
    return StreamingResponse(
        scan_generator(request),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/status")
async def get_scan_status() -> Dict[str, Any]:
    """
    获取扫描服务状态
    
    Returns:
        服务状态信息
    """
    try:
        return {
            "status": "ok",
            "message": "Scan service is running",
            "timestamp": str(__import__("datetime").datetime.now().isoformat()),
        }
    except Exception as e:
        logger.error(f"Error getting scan status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get scan status")
