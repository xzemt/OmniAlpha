import logging
import os
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from backend.app.api import market, strategies, scan, stock, alpha, ai, settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OmniAlpha API",
    description="Backend API for BlackOil-OmniAlpha Quantitative System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration - 生产环境应该更严格
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

# 添加 GZIP 压缩中间件 (性能优化)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 请求日志中间件 (监控和调试)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求的详细信息"""
    start_time = datetime.now()
    
    # 记录请求
    logger.info(
        f"→ {request.method} {request.url.path} "
        f"(Client: {request.client.host if request.client else 'unknown'})"
    )
    
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (datetime.now() - start_time).total_seconds()
        
        # 记录响应
        logger.info(
            f"← {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s"
        )
        
        return response
    
    except Exception as exc:
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"✗ {request.method} {request.url.path} "
            f"Error: {str(exc)} Time: {process_time:.3f}s"
        )
        raise


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if os.getenv("DEBUG") else "An error occurred",
            "timestamp": datetime.now().isoformat(),
        },
    )


# Register Routers
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])
app.include_router(scan.router, prefix="/api/scan", tags=["Scan"])
app.include_router(stock.router, prefix="/api/stock", tags=["Stock"])
app.include_router(alpha.router, prefix="/api/alpha", tags=["Alpha"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root() -> Dict[str, Any]:
    """API 根端点"""
    return {
        "message": "Welcome to OmniAlpha API",
        "version": "0.1.0",
        "docs": "http://localhost:8000/docs",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """健康检查端点"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("=" * 60)
    logger.info("OmniAlpha API 启动成功")
    logger.info(f"Docs: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("=" * 60)
    logger.info("OmniAlpha API 已关闭")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
