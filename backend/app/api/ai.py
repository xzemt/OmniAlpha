from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from backend.app.api.settings import load_settings_from_file
from llm.interface import LLMAgent
import json
import asyncio

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list = [] # List of {role, content}
    context: str = "general" 

def get_market_context():
    """
    Fetches real-time market context.
    For now, we will return a placeholder or read from the last data file.
    In a real scenario, this would query the DataProvider.
    """
    # TODO: Connect to DataProvider
    return "Market Status: The Shanghai Composite Index closed at 3,050 points yesterday. Tech sector volume is increasing."

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the AI Assistant using the configured provider.
    """
    settings = load_settings_from_file()
    
    # Convert Pydantic settings to dict
    ai_settings = settings.ai.model_dump()
    
    # Initialize Agent
    agent = LLMAgent(ai_settings)
    
    # Get Context
    market_context = get_market_context()
    
    # Prepare messages history (ensure valid format)
    messages = []
    for msg in request.history:
        # Validate role
        role = msg.get("role")
        if role not in ["user", "assistant", "system"]:
            continue
        messages.append({"role": role, "content": msg.get("content", "")})
    
    # Add current message
    messages.append({"role": "user", "content": request.message})

    async def event_generator():
        async for chunk in agent.chat_stream(messages, context_data=market_context):
            # Server-Sent Events format
            yield f"data: {json.dumps({'content': chunk})}\\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )