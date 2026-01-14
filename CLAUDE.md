# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OmniAlpha is a modular quantitative trading research platform for A-share markets with a FastAPI + React architecture. Key features include real-time market data, stock scanning strategies, Alpha factor analysis, and LLM integration for natural language stock selection.

## Development Commands

### Frontend
```bash
cd frontend
npm install              # Install dependencies
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # TypeScript check + Vite build
npm run lint             # ESLint check
```

### Backend
```bash
uvicorn backend.app.main:app --reload --port 8000  # Start FastAPI server
# API docs at http://localhost:8000/docs
```

### Python Tests
```bash
pytest                                    # All tests with coverage
pytest -m unit                            # Unit tests only
pytest -m integration                     # Integration tests only
pytest tests/unit/test_xxx.py             # Specific test file
pytest tests/unit/test_xxx.py::TestClass::test_method  # Specific test
pytest --cov --cov-report=html            # Generate HTML coverage report
```

## Architecture

```
OmniAlpha/
├── backend/app/api/       # FastAPI routes (market, stock, scan, ai, alpha)
├── core/                  # Shared Python logic (engine, strategies, data)
├── strategies/            # StockStrategy implementations (technical, fundamental)
├── data/                  # Baostock provider, cached CSV data
├── alpha/                 # GTJA191 factor library
├── llm/                   # LLM integration with streaming support
├── frontend/src/          # React app with pages (Home, Technical, Alpha, AI)
└── tests/                 # Pytest suite with fixtures in conftest.py
```

**Data Flow**: Frontend → Vite proxy (`/api` → `localhost:8000`) → FastAPI → Baostock data provider → Streaming response (NDJSON/SSE)

## Key Patterns

### Strategy Pattern
All strategies extend `StockStrategy` and return `(bool, dict)`:
```python
class CustomStrategy(StockStrategy):
    @property
    def name(self):
        return "strategy_name"

    def check(self, code, df):
        if df is None or df.empty:
            return False, {}
        return True, {'metric': value}
```
Register in `strategies/__init__.py` → `STRATEGY_REGISTRY`

### Data Provider
`data_provider` (BaostockProvider singleton) provides:
- `get_hs300_stocks(date)` - Stock list
- `get_daily_bars(code, date, lookback_days)` - OHLCV DataFrame with columns: `date, open, high, low, close, volume, amount, pctChg, peTTM, pbMRQ, turn, isST`

### API Endpoints
- `POST /api/scan` - Stock scanning (streaming NDJSON)
- `POST /api/ai/chat` - AI chat (streaming SSE)
- `GET /api/market/index` - Market index data

## Code Conventions

- **Python**: snake_case functions/variables, PascalCase classes, UPPER_SNAKE_CASE constants
- **Imports**: stdlib → third-party → local (absolute from project root)
- **Tests**: `@pytest.mark.unit` class `Test<ClassName>` with `test_<scenario>` methods
- **DataFrames**: Check `None/empty` first, use `.copy()` to avoid SettingWithCopyWarning
