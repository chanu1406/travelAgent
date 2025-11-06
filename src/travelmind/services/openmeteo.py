"""
Open-Meteo API Client

Client for fetching weather forecast data from Open-Meteo.

API Documentation: https://open-meteo.com/en/docs

Features:
- NO API KEY REQUIRED
- Completely free
- 7-day forecasts with hourly data
- Historical weather data
- Multiple weather variables (temp, precipitation, wind, etc.)

Rate limits:
- 10,000 requests per day per IP
- Generous for personal use
"""

from datetime import date
from typing import Any

import httpx


class OpenMeteoClient:
    """
    Client for Open-Meteo weather API.

    No API key required - completely free and open.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self) -> None:
        """Initialize Open-Meteo client."""
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        timezone: str = "auto",
    ) -> dict[str, Any]:
        """
        Fetch weather forecast for a location and date range.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: First forecast date
            end_date: Last forecast date
            timezone: Timezone name (e.g., "Asia/Tokyo") or "auto"

        Returns:
            Weather forecast data with daily and hourly breakdowns
        """
        raise NotImplementedError("Open-Meteo forecast fetching to be implemented")

    def _parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        Parse Open-Meteo API response into our internal format.

        Converts WMO weather codes to descriptions, organizes hourly data, etc.
        """
        raise NotImplementedError("Response parsing to be implemented")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


# WMO Weather interpretation codes
# Source: https://open-meteo.com/en/docs
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}
