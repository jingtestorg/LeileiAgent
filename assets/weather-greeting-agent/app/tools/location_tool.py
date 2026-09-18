"""Location tool: extracts city/location name from free-text user input."""
import logging
import re

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Common location indicator phrases
_LOCATION_PATTERNS = [
    # "hello from Berlin", "greetings from New York"
    r"(?:hello|hi|hey|greetings|salutations)\s+from\s+([A-Z][a-zA-Z\s]+?)(?:\s*[!.,]|$)",
    # "I'm in Berlin", "I am in New York"
    r"(?:i'?m|i am|we'?re|we are)\s+in\s+([A-Z][a-zA-Z\s]+?)(?:\s*[!.,]|$)",
    # "from London", "from San Francisco"
    r"\bfrom\s+([A-Z][a-zA-Z\s]+?)(?:\s*[!.,]|$)",
    # "in Tokyo", "in Los Angeles today"
    r"\bin\s+([A-Z][a-zA-Z\s]+?)(?:\s+today|\s+right now|\s+currently|\s*[!.,]|$)",
    # "located in Paris", "currently in Amsterdam"
    r"(?:located|currently|based|living|visiting|staying)\s+in\s+([A-Z][a-zA-Z\s]+?)(?:\s*[!.,]|$)",
    # "weather in Berlin", "what's the weather in Rome"
    r"weather\s+in\s+([A-Z][a-zA-Z\s]+?)(?:\s*[?!.,]|$)",
]

# Cities that are single words but need special treatment (common false positives to exclude)
_EXCLUDE_WORDS = {"I", "Me", "My", "We", "The", "A", "An", "Is", "Are", "Was", "Be"}


@tool
async def resolve_location(text: str) -> str:
    """Extract a city or location name from free-text user input.

    Args:
        text: Free-text user message that may contain a location reference

    Returns:
        Extracted city name as a string, or empty string if none found
    """
    logger.info("Attempting to resolve location from text: %s", text[:100])

    for pattern in _LOCATION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Clean trailing punctuation or common trailing words
            location = re.sub(r"\s+(today|now|currently|right now|this morning|tonight)$", "", location, flags=re.IGNORECASE)
            location = location.rstrip(".,!?;:")

            # Filter out single-word false positives
            if location in _EXCLUDE_WORDS:
                continue

            if location:
                logger.info("M1.achieved: location extracted from user input: %s", location)
                return location

    # Fallback: look for any capitalized word sequence that could be a place name
    # Last resort — look for sequences like "City Name" at word boundaries
    fallback = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text)
    # Filter out common non-city capitalized words
    non_city = {"Hello", "Hi", "Hey", "Good", "Morning", "Evening", "Afternoon", "Please", "Thanks", "Thank"}
    for candidate in fallback:
        if candidate not in non_city and candidate not in _EXCLUDE_WORDS:
            logger.info("M1.achieved: location extracted from user input (fallback): %s", candidate)
            return candidate

    logger.info("M1.missed: could not extract location from user input")
    return ""
