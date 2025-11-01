

"""
Chat API Routes with Event Data
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.services.ai_agent import agent
from app.services.db_service import search_volunteer_events
import re

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
    events: Optional[List[Dict[str, Any]]] = Field(None, description="Structured event data for map")
    location: Optional[Dict[str, str]] = Field(None, description="Extracted location")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Great! I found 3 volunteer opportunities near Baltimore...",
                "session_id": "user-123",
                "events": [],
                "location": {"city": "Baltimore", "state": "MD"}
            }
        }


def extract_location_from_message(message: str) -> Optional[Dict[str, str]]:
    """Extract location from user message."""
    # Common patterns: "in Brooklyn", "near Baltimore", "at Manhattan"
    patterns = [
        r'\bin\s+([A-Z][a-zA-Z\s]+?)(?:\s|,|$)',
        r'\bnear\s+([A-Z][a-zA-Z\s]+?)(?:\s|,|$)',
        r'\bat\s+([A-Z][a-zA-Z\s]+?)(?:\s|,|$)',
        r'\baround\s+([A-Z][a-zA-Z\s]+?)(?:\s|,|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            city = match.group(1).strip()
            # Clean up common words
            city = city.replace(' area', '').replace(' city', '')
            return {"city": city, "state": ""}
    
    return None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for interacting with CaritasAI agent.
    
    Returns both text response AND structured event data for the map.
    """
    try:
        # Get response from the agentic AI
        response_text = agent.chat(request.message)
        
        # Try to extract location and fetch events
        location = extract_location_from_message(request.message)
        events = None
        
        # If we found a location and the response mentions opportunities
        if location and location.get("city"):
            response_lower = response_text.lower()
            if any(word in response_lower for word in ['found', 'opportunit', 'event', 'volunteer']):
                try:
                    # Query events for the map
                    events_data = search_volunteer_events(
                        location=location["city"],
                        limit=20
                    )
                    
                    if events_data:
                        events = events_data
                        
                except Exception as e:
                    print(f"Error fetching events for map: {e}")
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            events=events,
            location=location
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/chat/reset")
async def reset_conversation(session_id: Optional[str] = None):
    """Reset the conversation history for a fresh start."""
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
    """Get the conversation history."""
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
