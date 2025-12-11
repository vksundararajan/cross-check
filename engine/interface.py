import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

AGENT_MAPPING = {
    "url_analyst": "url",
    "html_analyst": "html",
    "content_analyst": "content",
    "brand_analyst": "brand",
    "judgement_agent": "final"
}

def create_runner(app_name="cross-check"):
    session_service = InMemorySessionService()
    user_id = "user"
    session_id = "session"
    try:
        asyncio.run(session_service.create_session(
            app_name=app_name, 
            user_id=user_id, 
            session_id=session_id
        ))
    except Exception:
        pass

    runner = Runner(
        agent=root_agent, 
        app_name=app_name, 
        session_service=session_service
    )
    
    return runner, user_id, session_id

def stream_analysis(url_input: str):
    if not root_agent:
        raise ValueError("Root agent failed to load in engine.")

    runner, user_id, session_id = create_runner()
    user_msg = types.Content(
        role="user", 
        parts=[types.Part(text=url_input)]
    )

    for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_msg):
        yield event