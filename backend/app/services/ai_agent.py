"""
CaritasAI Agentic Agent with Database Integration
"""

from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Import database service functions
from .db_service import (
    get_nearby_parishes,
    search_volunteer_events,
    register_volunteer_for_event,
    get_parish_analytics
)

# Load environment variables
load_dotenv()


class CaritasAI:
    """
    CaritasAI - Agentic AI Agent with Database Integration
    
    Now connected to PostgreSQL + PostGIS for real data!
    """

    def __init__(
        self, 
        model_name: str = None, 
        temperature: float = 0.7
    ):
        """Initialize CaritasAI agent with database-connected tools."""
        
        self.model_name = model_name or os.getenv("CARITAS_MODEL", "gpt-4o")
        self.temperature = temperature
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create database-connected tools
        self.tools = self._create_tools()
        
        self.agent = self._create_agent()
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def _create_tools(self) -> List[Tool]:
        """Create tools that connect to the database."""
        
        def search_opportunities(location_and_details: str) -> str:
            """
            Search for volunteer opportunities in the database.
            
            Args:
                location_and_details: Location and optional details (e.g., "Baltimore, weekend, food pantry")
            
            Returns:
                String with formatted opportunities
            """
            try:
                # Parse the input
                parts = location_and_details.lower().split(",")
                location = parts[0].strip() if parts else location_and_details
                
                # Check for date keywords
                start_date = None
                end_date = None
                skills_list = None
                
                full_text = location_and_details.lower()
                
                if "weekend" in full_text or "saturday" in full_text or "sunday" in full_text:
                    today = datetime.now()
                    days_until_saturday = (5 - today.weekday()) % 7
                    if days_until_saturday == 0:
                        days_until_saturday = 7
                    start_date = today + timedelta(days=days_until_saturday)
                    end_date = start_date + timedelta(days=2)
                
                # Check for skill keywords
                skill_keywords = ["food", "pantry", "sorting", "packing", "tutoring", "teaching"]
                found_skills = [skill for skill in skill_keywords if skill in full_text]
                if found_skills:
                    skills_list = found_skills
                
                # Query database
                events = search_volunteer_events(
                    location=location,
                    skills=skills_list,
                    start_date=start_date,
                    end_date=end_date,
                    limit=5
                )
                
                if not events:
                    return f"I couldn't find any volunteer opportunities in {location} right now. Try expanding your search or check back later!"
                
                # Format response
                response = f"Found {len(events)} volunteer opportunities near {location}:\n\n"
                
                for i, event in enumerate(events, 1):
                    event_date = datetime.fromisoformat(str(event['event_date']))
                    response += f"{i}. **{event['title']}** (Event ID: {event['id']})\n"
                    response += f"   - Parish: {event['parish_name']}\n"
                    response += f"   - Date: {event_date.strftime('%A, %B %d, %Y')}\n"
                    response += f"   - Location: {event.get('parish_address', '')}, {event['parish_city']}\n"
                    if event.get('skills_needed'):
                        response += f"   - Skills Needed: {', '.join(event['skills_needed'])}\n"
                    spots = event.get('max_volunteers', 'Unlimited')
                    if spots != 'Unlimited':
                        spots_left = spots - event.get('registered_volunteers', 0)
                        response += f"   - Spots Available: {spots_left}\n"
                    response += "\n"
                
                response += "Interested in any of these? Just let me know and provide your name and email - I'll handle the registration!"
                
                return response
                
            except Exception as e:
                return f"I had trouble searching for events: {str(e)}. Please try again!"

        def find_parishes(location_and_need: str) -> str:
            """
            Find Catholic parishes and resources.
            
            Args:
                location_and_need: Location and type of need (e.g., "Baltimore, food assistance")
            
            Returns:
                String with formatted parishes
            """
            try:
                parts = location_and_need.split(",")
                location = parts[0].strip()
                
                # Map keywords to services
                services = None
                if len(parts) > 1:
                    need = parts[1].strip().lower()
                    if "food" in need:
                        services = ["food pantry", "soup kitchen"]
                    elif "counsel" in need:
                        services = ["counseling"]
                
                parishes = get_nearby_parishes(
                    city=location,
                    services=services,
                    limit=5
                )
                
                if not parishes:
                    return f"I couldn't find any parishes in {location}. Try a nearby city?"
                
                response = f"Found {len(parishes)} Catholic resources near {location}:\n\n"
                
                for i, parish in enumerate(parishes, 1):
                    response += f"{i}. **{parish['name']}**\n"
                    response += f"   - Address: {parish['address']}, {parish['city']}, {parish['state']} {parish.get('zip_code', '')}\n"
                    if parish.get('services'):
                        response += f"   - Services: {', '.join(parish['services'])}\n"
                    response += f"   - Email: {parish.get('email', 'Contact via website')}\n\n"
                
                response += "All services are confidential and available to everyone."
                
                return response
                
            except Exception as e:
                return f"I had trouble finding parishes: {str(e)}. Please try again!"

        def register_for_event(registration_info: str) -> str:
            """
            Register a volunteer for an event.
            
            Args:
                registration_info: Format "event_id|volunteer_name|volunteer_email" 
                                  Example: "123|John Doe|john@example.com"
            
            Returns:
                String with registration confirmation or error
            """
            try:
                # Parse the registration info
                parts = registration_info.split("|")
                
                if len(parts) != 3:
                    return "❌ Invalid format. I need: event_id, your name, and your email separated by |"
                
                event_id_str = parts[0].strip()
                volunteer_name = parts[1].strip()
                volunteer_email = parts[2].strip()
                
                # Validate
                if not event_id_str.isdigit():
                    return f"❌ Invalid event ID: {event_id_str}"
                
                if not volunteer_email or "@" not in volunteer_email:
                    return "❌ Please provide a valid email address"
                
                if not volunteer_name:
                    return "❌ Please provide your name"
                
                # Convert event_id to int
                event_id_int = int(event_id_str)
                
                # Call database function
                result = register_volunteer_for_event(
                    volunteer_email=volunteer_email,
                    event_id=event_id_int,
                    volunteer_name=volunteer_name
                )
                
                if not result.get("success"):
                    return f"❌ Registration failed: {result.get('error', 'Unknown error')}"
                
                response = f"✅ **Registration Successful!**\n\n"
                response += f"Event: {result['event_title']}\n"
                response += f"Date: {result['event_date']}\n"
                response += f"Parish: {result['parish_name']}\n\n"
                response += f"✉️ Confirmation sent to: {volunteer_email}\n\n"
                response += "Thank you for serving your community! 🙏"
                
                return response
                
            except Exception as e:
                return f"❌ Registration failed: {str(e)}"

        def get_analytics(parish_name: str) -> str:
            """Get analytics for a parish."""
            try:
                analytics = get_parish_analytics(parish_name)
                
                if analytics.get("error"):
                    return f"Couldn't find parish: {analytics['error']}"
                
                response = f"**Analytics for {analytics['parish_name']}** ({analytics['city']})\n\n"
                response += f"📊 Overall Statistics:\n"
                response += f"   - Total Events: {analytics['total_events']}\n"
                response += f"   - Upcoming: {analytics['upcoming_events']}\n"
                response += f"   - Past Events: {analytics['past_events']}\n"
                response += f"   - Total Registrations: {analytics['total_registrations']}\n\n"
                response += f"📅 This Month:\n"
                response += f"   - Events: {analytics['this_month']['events']}\n"
                response += f"   - New Registrations: {analytics['this_month']['registrations']}\n\n"
                response += f"🔧 Services Offered:\n"
                response += f"   - {', '.join(analytics.get('services_offered', ['N/A']))}\n"
                
                return response
                
            except Exception as e:
                return f"Error getting analytics: {str(e)}"

        # Define tools with database functions
        tools = [
            Tool(
                name="search_volunteer_opportunities",
                description="Search for volunteer opportunities. Input should be location and optional details like 'Baltimore, weekend, food pantry'",
                func=search_opportunities
            ),
            Tool(
                name="find_nearby_parishes",
                description="Find Catholic parishes and charities. Input should be location and optional need like 'Baltimore, food assistance'",
                func=find_parishes
            ),
            Tool(
                name="register_volunteer",
                description="Register a volunteer for an event. YOU must extract the event_id from conversation context, extract name and email from user's natural language, then format as 'event_id|name|email'. Example: if user says 'My name is John Doe, email john@test.com' and they're interested in event 42, YOU call this with '42|John Doe|john@test.com'. The user should never see this format!",
                func=register_for_event
            ),
            Tool(
                name="get_parish_analytics",
                description="Get analytics for a parish. Input should be parish name.",
                func=get_analytics
            )
        ]
        
        return tools

    def _create_agent(self):
        """Create the agent with system prompt."""
        
        system_prompt = """You are CaritasAI, a compassionate AI assistant serving the Catholic Church's 
mission of evangelization through service. You have access to a real database of parishes, events, and volunteers!

Your Mission:
- Connect volunteers with real service opportunities
- Guide people to actual Catholic parishes and charities
- Register volunteers for events in the database
- Provide real analytics to parish administrators

Your Personality:
- Warm, compassionate, and faith-filled
- Action-oriented and practical
- Professional yet approachable

Guidelines:
1. For Volunteers:
   - Ask about location, availability, and skills
   - Use search_volunteer_opportunities to find REAL events
   - Show them specific opportunities with Event IDs clearly displayed
   - **REMEMBER the Event ID** when they show interest in an event
   - When they provide name and email naturally (like "My name is John, email john@email.com"):
     * Extract their name and email
     * Use the Event ID you remembered from the search
     * Call register_volunteer with format: "event_id|name|email"
   - The user should NEVER have to format anything - you do it automatically!

2. For Those in Need:
   - Listen with compassion
   - Ask about location and type of need
   - Use find_nearby_parishes to find REAL resources
   - Show specific parishes with contact info

3. For Parish Staff:
   - Use get_parish_analytics for REAL data
   - Provide actionable insights

CRITICAL Registration Flow:
Step 1: Show events with clear Event IDs (e.g., "Event ID: 42")
Step 2: When user shows interest, REMEMBER that Event ID
Step 3: When user provides name/email in ANY natural format, YOU extract it and format as: "event_id|name|email"
Example: User says "My name is Christopher Wachira and my email is wanjohi@cua.edu"
         You call: register_volunteer("42|Christopher Wachira|wanjohi@cua.edu")
The user should have a natural conversation - YOU handle all the technical formatting!"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return agent

    def chat(self, message: str) -> str:
        """Process user message with database-connected tools."""
        try:
            result = self.agent_executor.invoke({"input": message})
            return result["output"]
        except Exception as e:
            return f"I apologize, but I encountered an issue: {str(e)}. Please try again."

    def reset_conversation(self):
        """Clear conversation memory."""
        self.memory.clear()
        
    def get_conversation_history(self):
        """Get conversation history."""
        return self.memory.chat_memory.messages


# Singleton instance
agent = CaritasAI()