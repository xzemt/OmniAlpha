from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import market, strategies, scan, stock, alpha, ai, settings
import uvicorn
import os

app = FastAPI(
    title="OmniAlpha API",
    description="Backend API for BlackOil-OmniAlpha Quantitative System",
    version="0.1.0"
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
async def root():
    return {"message": "Welcome to OmniAlpha API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
