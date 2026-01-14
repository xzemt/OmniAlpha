from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import time
import asyncio

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: str = "general" # 'general', 'strategy', 'code'

async def mock_llm_stream(prompt: str):
    """
    Simulates a streaming response from an LLM.
    """
    response_template = f"Received your request: '{prompt}'.\n\nHere is a simulated analysis based on the current market context:\n\n1. **Market Trend**: The market is currently showing signs of consolidation.\n2. **Strategy Suggestion**: Consider looking at low-volatility stocks with high dividend yields.\n\n```python\n# Example Filter\ndef filter_stocks(df):\n    return df[(df['volatility'] < 0.02) & (df['dividend_yield'] > 0.04)]\n```\n\nThis is a placeholder response for the AI module."
    
    tokens = response_template.split(' ')
    for token in tokens:
        yield f"data: {token} \n\n"
        await asyncio.sleep(0.05) # Simulate network/processing delay
    yield "data: [DONE]\n\n"

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the AI Assistant. Returns a server-sent event stream.
    """
    return StreamingResponse(
        mock_llm_stream(request.message),
        media_type="text/event-stream"
    )

