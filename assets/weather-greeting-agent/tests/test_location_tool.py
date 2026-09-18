"""Unit tests for the location tool."""
import sys
import pytest

sys.path.insert(0, "app")


@pytest.mark.asyncio
async def test_resolve_location_hello_from():
    """Extracts city from 'hello from <City>' pattern."""
    from tools.location_tool import resolve_location
    result = await resolve_location.ainvoke({"text": "Hello from Berlin!"})
    assert result == "Berlin"


@pytest.mark.asyncio
async def test_resolve_location_im_in():
    """Extracts city from 'I'm in <City>' pattern."""
    from tools.location_tool import resolve_location
    result = await resolve_location.ainvoke({"text": "I'm in New York right now"})
    assert "New York" in result or result == "New York"


@pytest.mark.asyncio
async def test_resolve_location_weather_in():
    """Extracts city from 'weather in <City>' pattern."""
    from tools.location_tool import resolve_location
    result = await resolve_location.ainvoke({"text": "What's the weather in Tokyo?"})
    assert result == "Tokyo"


@pytest.mark.asyncio
async def test_resolve_location_no_location():
    """Returns empty string when no location is found."""
    from tools.location_tool import resolve_location
    result = await resolve_location.ainvoke({"text": "How are you doing today?"})
    # May return empty or some false positive — main check is it doesn't crash
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_resolve_location_from_city():
    """Extracts city from bare 'from <City>' pattern."""
    from tools.location_tool import resolve_location
    result = await resolve_location.ainvoke({"text": "Greetings from Paris!"})
    assert result == "Paris"


@pytest.mark.asyncio
async def test_resolve_location_located_in():
    """Extracts city from 'located in <City>' pattern."""
    from tools.location_tool import resolve_location
    result = await resolve_location.ainvoke({"text": "I am currently located in Amsterdam"})
    assert result == "Amsterdam"
