from fastapi import APIRouter
from typing import List, Dict, Any
from core.strategies_registry import STRATEGY_REGISTRY, get_strategy

router = APIRouter()

@router.get("/", response_model=List[Dict[str, str]])
async def get_strategies():
    """
    Get list of available strategies with metadata.
    """
    strategies = []
    for key, strategy_cls in STRATEGY_REGISTRY.items():
        # Instantiate to get properties
        strategy_instance = strategy_cls()
        strategies.append({
            "key": key,
            "name": strategy_instance.name,
            "description": strategy_instance.description,
            "category": "Technical" if key in ['ma', 'vol', 'turn'] else "Fundamental" # Simple categorization
        })
    return strategies
