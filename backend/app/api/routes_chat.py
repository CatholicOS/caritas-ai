from fastapi import APIRouter
from pydantic import BaseModel
from ..services.ai_agent import AgentService

router = APIRouter()
agent = AgentService()

class ChatRequest(BaseModel):
    user_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = await agent.respond(req.message, user_id=req.user_id)
    return ChatResponse(reply=reply)
