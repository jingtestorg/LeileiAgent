"""Unit tests for the weather tool."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_geo_response():
    """Mock successful geocoding response for Berlin."""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "results": [
            {
                "name": "Berlin",
                "latitude": 52.5200,
                "longitude": 13.4050,
                "country": "Germany",
            }
        ]
    }
    return resp


@pytest.fixture
def mock_weather_response():
    """Mock successful weather response — clear sky, 22°C."""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "current": {
            "temperature_2m": 22.0,
            "weathercode": 0,
        }
    }
    return resp


@pytest.fixture
def mock_empty_geo_response():
    """Mock geocoding response when city is not found."""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"results": []}
    return resp


@pytest.mark.asyncio
async def test_get_weather_happy_path(mock_geo_response, mock_weather_response):
    """get_weather returns correct data for a valid city."""
    import sys
    sys.path.insert(0, "app")
    from tools.weather_tool import get_weather

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[mock_geo_response, mock_weather_response])
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_client)
    mock_context.__aexit__ = AsyncMock(return_value=False)

    with patch("tools.weather_tool.httpx.AsyncClient", return_value=mock_context):
        result = await get_weather.ainvoke({"city": "Berlin"})

    assert "city" in result
    assert "Berlin" in result["city"]
    assert result["temperature"] == 22.0
    assert result["unit"] == "°C"
    assert result["condition"] == "Clear sky"
    assert "error" not in result


@pytest.mark.asyncio
async def test_get_weather_city_not_found(mock_empty_geo_response):
    """get_weather returns error dict when city is not found."""
    import sys
    sys.path.insert(0, "app")
    from tools.weather_tool import get_weather

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_empty_geo_response)
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_client)
    mock_context.__aexit__ = AsyncMock(return_value=False)

    with patch("tools.weather_tool.httpx.AsyncClient", return_value=mock_context):
        result = await get_weather.ainvoke({"city": "NotARealCityXYZ"})

    assert "error" in result
    assert "NotARealCityXYZ" in result["error"]


@pytest.mark.asyncio
async def test_get_weather_timeout():
    """get_weather returns error dict on timeout."""
    import sys
    sys.path.insert(0, "app")
    import httpx
    from tools.weather_tool import get_weather

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_client)
    mock_context.__aexit__ = AsyncMock(return_value=False)

    with patch("tools.weather_tool.httpx.AsyncClient", return_value=mock_context):
        result = await get_weather.ainvoke({"city": "Berlin"})

    assert "error" in result
    assert "timed out" in result["error"].lower() or "timeout" in result["error"].lower()


def test_weather_code_mapping():
    """Weather code descriptions are returned for known codes."""
    import sys
    sys.path.insert(0, "app")
    from tools.weather_tool import _get_weather_description

    assert _get_weather_description(0) == "Clear sky"
    assert _get_weather_description(2) == "Partly cloudy"
    assert _get_weather_description(61) == "Light rain"
    assert _get_weather_description(71) == "Light snow"
    assert _get_weather_description(95) == "Thunderstorm"
