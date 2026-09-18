"""Integration test: end-to-end agent flow with mocked LLM and tools."""
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, "app")


@pytest.fixture
def mock_weather_data():
    return {
        "city": "Berlin, Germany",
        "temperature": 18.5,
        "unit": "°C",
        "condition": "Partly cloudy",
    }


@pytest.fixture
def mock_location_result():
    return "Berlin"


@pytest.mark.asyncio
async def test_agent_greeting_end_to_end(mock_weather_data, mock_location_result):
    """Agent returns a greeting containing city and weather info when tools succeed."""
    from agent import SampleAgent
    from langchain_core.tools import tool

    # Create stub tools that return deterministic data
    @tool
    async def get_weather(city: str) -> dict:
        """Fetch weather for a city."""
        return mock_weather_data

    @tool
    async def resolve_location(text: str) -> str:
        """Extract location from text."""
        return mock_location_result

    # Mock the LLM response
    mock_llm_message = MagicMock()
    mock_llm_message.content = (
        "Good morning, Berlin, Germany! It's partly cloudy and 18.5°C today — "
        "perfect weather for a walk!"
    )

    mock_graph_result = {"messages": [mock_llm_message]}

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new=AsyncMock(return_value=mock_graph_result)):
        response = await agent.invoke(
            query="Hello from Berlin!",
            context_id="test-context-123",
            tools=[get_weather, resolve_location],
        )

    assert response.status == "completed"
    assert "Berlin" in response.message
    assert "18.5" in response.message or "partly cloudy" in response.message.lower()


@pytest.mark.asyncio
async def test_agent_fallback_greeting_on_error():
    """Agent returns a graceful error message when an exception occurs."""
    from agent import SampleAgent

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new=AsyncMock(side_effect=Exception("LLM unavailable"))):
        response = await agent.invoke(
            query="Hello from Paris!",
            context_id="test-context-456",
            tools=[],
        )

    assert response.status == "completed"
    assert "error" in response.message.lower() or "encountered" in response.message.lower()


@pytest.mark.asyncio
async def test_agent_stream_yields_processing_then_result():
    """stream() yields a processing status then a completed result."""
    from agent import SampleAgent

    mock_llm_message = MagicMock()
    mock_llm_message.content = "Hello, Tokyo! It's sunny and 25°C — enjoy your day!"

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new=AsyncMock(
        return_value={"messages": [mock_llm_message]}
    )):
        chunks = []
        async for chunk in agent.stream("Hi from Tokyo!", "ctx-789"):
            chunks.append(chunk)

    assert len(chunks) >= 2
    # First chunk is "Processing..."
    assert chunks[0]["is_task_complete"] is False
    assert "Processing" in chunks[0]["content"]
    # Last chunk is the completed greeting
    assert chunks[-1]["is_task_complete"] is True
    assert "Tokyo" in chunks[-1]["content"]
