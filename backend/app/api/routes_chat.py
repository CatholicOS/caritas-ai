"""
Chat API Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.ai_agent import agent

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to volunteer this weekend in Baltimore",
                "session_id": "user-123"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI agent's response")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Great! I found 3 volunteer opportunities near Baltimore...",
                "session_id": "user-123"
            }
        }


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for interacting with CaritasAI agent.
    
    The agent can:
    - Find volunteer opportunities based on location and skills
    - Connect people in need with Catholic resources
    - Register volunteers for events
    - Provide parish analytics
    
    The agent uses tools to search databases and take actions.
    """
    try:
        # Get response from the agentic AI
        response_text = agent.chat(request.message)
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/chat/reset")
async def reset_conversation(session_id: Optional[str] = None):
    """
    Reset the conversation history for a fresh start.
    
    Useful when:
    - Starting a new topic
    - After completing a task
    - Testing the agent
    """
    try:
        agent.reset_conversation()
        return {
            "message": "Conversation reset successfully",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting conversation: {str(e)}"
        )


@router.get("/chat/history")
async def get_conversation_history(session_id: Optional[str] = None):
    """
    Get the conversation history.
    
    Returns the list of messages in the current conversation.
    """
    try:
        history = agent.get_conversation_history()
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": [
                {
                    "type": msg.type,
                    "content": msg.content
                }
                for msg in history
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )