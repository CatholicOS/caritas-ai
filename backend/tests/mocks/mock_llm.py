"""
Mock Objects for AI Agent Testing

Provides mock LLM responses to avoid calling OpenAI API during tests
"""

from unittest.mock import Mock, MagicMock


class MockOpenAI:
    """Mock OpenAI client for testing."""
    
    def __init__(self):
        self.chat = MockChat()
    
    class MockChat:
        """Mock chat completions."""
        
        def __init__(self):
            self.completions = MockCompletions()
        
        class MockCompletions:
            """Mock completions."""
            
            @staticmethod
            def create(**kwargs):
                """Mock create method."""
                return {
                    "choices": [
                        {
                            "message": {
                                "content": "I found 2 volunteer opportunities in Baltimore...",
                                "role": "assistant"
                            }
                        }
                    ]
                }


class MockLangChainLLM:
    """Mock LangChain LLM for testing."""
    
    def __init__(self):
        self.responses = {
            "search": "Found 3 volunteer opportunities near you...",
            "register": "✅ Registration successful!",
            "default": "I'm here to help you find volunteer opportunities."
        }
    
    def predict(self, prompt: str, **kwargs):
        """Mock predict method."""
        if "search" in prompt.lower() or "volunteer" in prompt.lower():
            return self.responses["search"]
        elif "register" in prompt.lower():
            return self.responses["register"]
        else:
            return self.responses["default"]
    
    def __call__(self, prompt: str, **kwargs):
        """Make the mock callable."""
        return self.predict(prompt, **kwargs)


class MockAgentExecutor:
    """Mock LangChain AgentExecutor for testing."""
    
    def __init__(self):
        self.call_count = 0
    
    def invoke(self, inputs: dict):
        """Mock invoke method."""
        self.call_count += 1
        
        message = inputs.get("input", "").lower()
        
        if "brooklyn" in message or "baltimore" in message:
            return {
                "output": """Found 2 volunteer opportunities:
                
1. Weekend Food Pantry at St. Mary's Church
   - Date: Saturday, November 1, 2025
   - Location: Brooklyn, NY
   - Event ID: 7
   
Would you like to register?"""
            }
        elif "register" in message or "@" in message:
            return {
                "output": "✅ Registration Successful! You're all set for the event."
            }
        else:
            return {
                "output": "I'm here to help you find volunteer opportunities!"
            }


def get_mock_llm():
    """Factory function to get a mock LLM."""
    return MockLangChainLLM()


def get_mock_agent_executor():
    """Factory function to get a mock agent executor."""
    return MockAgentExecutor()


def get_mock_openai_client():
    """Factory function to get a mock OpenAI client."""
    return MockOpenAI()


# Pytest fixtures for mocks
def mock_ai_agent_dependencies(monkeypatch):
    """
    Monkeypatch AI agent dependencies for testing.
    
    Usage:
        def test_something(test_db, monkeypatch):
            mock_ai_agent_dependencies(monkeypatch)
            # Test code here
    """
    # Mock OpenAI
    monkeypatch.setattr(
        "app.services.ai_agent.ChatOpenAI",
        lambda **kwargs: get_mock_llm()
    )
    
    # Mock AgentExecutor
    monkeypatch.setattr(
        "app.services.ai_agent.AgentExecutor",
        lambda **kwargs: get_mock_agent_executor()
    )


# Sample mock responses for different scenarios
MOCK_RESPONSES = {
    "search_brooklyn": """Found 2 volunteer opportunities in Brooklyn:
    
1. Weekend Food Pantry (Event ID: 7)
   - Date: Saturday, October 30, 2025
   - Location: 1230 65th St, Brooklyn
   - Skills: Packing, sorting
   - Spots: 7 available
   
2. Tutoring Session (Event ID: 8)
   - Date: Sunday, October 31, 2025
   - Location: 456 Main St, Brooklyn
   - Skills: Teaching
   - Spots: 5 available

Interested? Just provide your name and email!""",
    
    "search_no_results": "I couldn't find any volunteer opportunities in that area right now. Try expanding your search or check back later!",
    
    "registration_success": """✅ Registration Successful!

Event: Weekend Food Pantry
Date: 2025-10-30
Parish: St. Mary's Church

✉️ Confirmation sent to: volunteer@email.com

Thank you for serving your community! 🙏""",
    
    "registration_full": "❌ Registration failed: Event is full",
    
    "registration_duplicate": "❌ Registration failed: Volunteer already registered for this event",
    
    "find_parishes": """Found 3 Catholic resources near Baltimore:

1. St. Mary's Church
   - Address: 123 Main St, Baltimore, MD
   - Services: Food pantry, Counseling
   
2. Holy Spirit Parish
   - Address: 456 Oak Ave, Baltimore, MD
   - Services: Food pantry, Tutoring
   
All services are confidential and available to everyone."""
}


def get_mock_response(scenario: str) -> str:
    """Get a mock response for a specific scenario."""
    return MOCK_RESPONSES.get(scenario, "I'm here to help!")