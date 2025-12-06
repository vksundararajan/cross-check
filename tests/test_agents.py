import pytest
import dotenv

from pathlib import Path
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
from engine.agent import root_agent

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    env_path = Path(__file__).parent.parent / "engine/.env"
    if not env_path.exists():
        env_path = "engine/.env"        
    dotenv.load_dotenv(str(env_path))


@pytest.mark.asyncio
async def test_legitimate():
    user_input = "https://vksundararajan.github.io/VIBE"

    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = UserContent(parts=[Part(text=user_input)])
    all_responses = []
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
             all_responses.append(event.content.parts[0].text)

    full_transcript = " ".join(all_responses).upper()
    assert "LEGITIMATE" in full_transcript
