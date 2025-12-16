import pytest
from unittest.mock import MagicMock, patch
from google.adk.events import Event
from google.genai import types
from engine.agent import UrlPreProcessor, url_validation_callback, exit_loop

@pytest.mark.asyncio
async def test_url_preprocessor_valid_url():
    """Test that the agent extracts a URL and updates state correctly."""
    agent = UrlPreProcessor(name="test_preprocessor")
    mock_ctx = MagicMock()
    user_event_content = types.Content(
        role="user",
        parts=[types.Part(text="Check: https://google.com")]
    )
    mock_event = Event(author="user", content=user_event_content)
    
    mock_ctx.session.events = [mock_event]
    mock_ctx.session.state = {} 

    with patch('engine.agent.process_website_data') as mock_process:
        mock_process.return_value = ("https://google.com", "<html></html>", "content")

        async for event in agent._run_async_impl(mock_ctx):
            pass

        assert mock_ctx.session.state["target_url"] == "https://google.com"
        assert mock_ctx.session.state["skip_llm_agent"] is True

@pytest.mark.asyncio
async def test_url_preprocessor_no_url():
    """Test that the agent handles input with NO url gracefully."""
    agent = UrlPreProcessor(name="test_preprocessor")
    mock_ctx = MagicMock()
    
    user_event_content = types.Content(
        role="user", parts=[types.Part(text="Hello")]
    )
    mock_event = Event(author="user", content=user_event_content)
    mock_ctx.session.events = [mock_event]
    mock_ctx.session.state = {} 

    async for event in agent._run_async_impl(mock_ctx):
        pass

    assert mock_ctx.session.state.get("skip_llm_agent") is False

def test_url_validation_callback_allow():
    """Test that the callback allows execution if skip_llm_agent is True."""
    mock_ctx = MagicMock()
    mock_ctx.state = {"skip_llm_agent": True}
    result = url_validation_callback(mock_ctx)
    
    assert result is None

def test_url_validation_callback_block():
    """Test that the callback BLOCKS execution if skip_llm_agent is False."""
    mock_ctx = MagicMock()
    mock_ctx.state = {"skip_llm_agent": False}
    result = url_validation_callback(mock_ctx)

    assert isinstance(result, types.Content)
    assert result.parts[0].text == "INVALID URL"
    assert result.role == "model"

def test_url_validation_callback_block_default():
    """Test that the callback BLOCKS execution if key is missing."""
    mock_ctx = MagicMock()
    mock_ctx.state = {}
    result = url_validation_callback(mock_ctx)
    
    assert isinstance(result, types.Content)
    assert result.parts[0].text == "INVALID URL"

def test_exit_loop_sets_escalate():
    """Test that exit_loop sets the escalate flag on tool context."""
    mock_tool_ctx = MagicMock()
    mock_tool_ctx.actions = MagicMock()
    mock_tool_ctx.actions.escalate = False
    
    result = exit_loop(mock_tool_ctx)
    
    assert mock_tool_ctx.actions.escalate is True
    assert result == {}