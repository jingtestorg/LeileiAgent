"""Weather tool: fetches current weather conditions for a given city using Open-Meteo."""
import logging

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Weather code to human-readable description mapping (WMO Weather interpretation codes)
WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Moderate showers",
    82: "Violent showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def _get_weather_description(code: int) -> str:
    """Map WMO weather code to a human-readable description."""
    if code in WEATHER_CODE_MAP:
        return WEATHER_CODE_MAP[code]
    # Fallback for ranges not explicitly listed
    if 1 <= code <= 3:
        return "Partly cloudy"
    if 45 <= code <= 48:
        return "Foggy"
    if 51 <= code <= 55:
        return "Drizzly"
    if 61 <= code <= 65:
        return "Rainy"
    if 71 <= code <= 77:
        return "Snowy"
    if 80 <= code <= 82:
        return "Showery"
    if 95 <= code <= 99:
        return "Thunderstorm"
    return "Cloudy"


@tool
async def get_weather(city: str) -> dict:
    """Fetch current weather conditions for a city.

    Args:
        city: Name of the city (e.g. 'Berlin', 'New York', 'Tokyo')

    Returns:
        dict with keys: city, temperature, unit, condition
        On error: dict with key: error
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Step 1: Geocode city name to coordinates
            geo_resp = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "en", "format": "json"},
            )
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()

            results = geo_data.get("results", [])
            if not results:
                logger.info("M2.missed: weather data retrieval failed — city not found: %s", city)
                return {"error": f"City '{city}' not found. Please check the city name and try again."}

            location = results[0]
            lat = location["latitude"]
            lon = location["longitude"]
            resolved_city = location.get("name", city)
            country = location.get("country", "")

            # Step 2: Fetch current weather
            weather_resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,weathercode",
                    "timezone": "auto",
                },
            )
            weather_resp.raise_for_status()
            weather_data = weather_resp.json()

            current = weather_data.get("current", {})
            temperature = current.get("temperature_2m")
            weathercode = current.get("weathercode", 0)

            if temperature is None:
                logger.info("M2.missed: weather data retrieval failed — no temperature data for %s", city)
                return {"error": f"Weather data unavailable for '{city}' at this time."}

            condition = _get_weather_description(weathercode)
            display_city = f"{resolved_city}, {country}" if country else resolved_city

            logger.info("M2.achieved: weather data retrieved successfully for %s", display_city)
            return {
                "city": display_city,
                "temperature": round(temperature, 1),
                "unit": "°C",
                "condition": condition,
            }

    except httpx.TimeoutException:
        logger.info("M2.missed: weather data retrieval failed — request timed out")
        return {"error": "Weather service timed out. Please try again."}
    except httpx.HTTPStatusError as e:
        logger.info("M2.missed: weather data retrieval failed — HTTP error: %s", e)
        return {"error": f"Weather service returned an error: {e.response.status_code}"}
    except Exception as e:
        logger.info("M2.missed: weather data retrieval failed — unexpected error: %s", e)
        return {"error": f"Failed to fetch weather data: {str(e)}"}
