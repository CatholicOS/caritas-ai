import os
from loguru import logger
try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None

SYSTEM_PROMPT = (
    "You are CaritasAI, a compassionate assistant helping connect volunteers with Catholic parishes and charities. "
    "Answer briefly, suggest next steps, and ask a clarifying question if needed."
)

class AgentService:
    def __init__(self):
        self.use_llm = bool(os.getenv("OPENAI_API_KEY")) and (ChatOpenAI is not None)
        if self.use_llm:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            logger.info("CaritasAI using OpenAI backend")
        else:
            self.llm = None
            logger.warning("CaritasAI running in STUB mode (no OPENAI_API_KEY or SDK not installed)")

    async def respond(self, message: str, user_id: str | None = None) -> str:
        if not self.use_llm:
            msg = message.lower()
            if "help" in msg and ("weekend" in msg or "today" in msg):
                return "I can help match you to a nearby parish event. What city are you in and what times work?"
            if "need" in msg:
                return "I'm here to help. Please share your location and what assistance you need (food, shelter, clothes)."
            return "How can I assist you with volunteering or finding help?"
        try:
            result = await self.llm.ainvoke([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ])
            return getattr(result, "content", str(result))
        except Exception:
            logger.exception("LLM failure; falling back to stub.")
            return "How can I assist you with volunteering or finding help?"
