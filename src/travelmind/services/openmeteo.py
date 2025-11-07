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
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": timezone,
            "daily": ",".join([
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "weather_code",
                "sunrise",
                "sunset",
            ]),
            "hourly": ",".join([
                "temperature_2m",
                "apparent_temperature",
                "precipitation_probability",
                "precipitation",
                "wind_speed_10m",
                "weather_code",
            ]),
        }

        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()

        return self._parse_response(response.json())

    def _parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        Parse Open-Meteo API response into our internal format.

        Converts WMO weather codes to descriptions, organizes hourly data, etc.
        """
        daily = response.get("daily", {})
        hourly = response.get("hourly", {})

        # Parse daily forecasts
        daily_forecasts = []
        num_days = len(daily.get("time", []))

        for i in range(num_days):
            weather_code = daily["weather_code"][i]
            daily_forecasts.append({
                "date": daily["time"][i],
                "temperature_max_celsius": daily["temperature_2m_max"][i],
                "temperature_min_celsius": daily["temperature_2m_min"][i],
                "precipitation_sum_mm": daily["precipitation_sum"][i],
                "precipitation_probability": daily["precipitation_probability_max"][i] / 100.0,
                "wind_speed_max_kmh": daily["wind_speed_10m_max"][i],
                "weather_code": weather_code,
                "weather_description": WMO_CODES.get(weather_code, "Unknown"),
                "sunrise": daily["sunrise"][i],
                "sunset": daily["sunset"][i],
            })

        # Parse hourly forecasts (grouped by day)
        hourly_forecasts = []
        num_hours = len(hourly.get("time", []))

        for i in range(num_hours):
            weather_code = hourly["weather_code"][i]
            hourly_forecasts.append({
                "timestamp": hourly["time"][i],
                "temperature_celsius": hourly["temperature_2m"][i],
                "feels_like_celsius": hourly["apparent_temperature"][i],
                "precipitation_probability": hourly["precipitation_probability"][i] / 100.0,
                "precipitation_mm": hourly["precipitation"][i],
                "wind_speed_kmh": hourly["wind_speed_10m"][i],
                "weather_code": weather_code,
                "weather_description": WMO_CODES.get(weather_code, "Unknown"),
            })

        return {
            "location": f"{response.get('latitude')}, {response.get('longitude')}",
            "latitude": response.get("latitude"),
            "longitude": response.get("longitude"),
            "timezone": response.get("timezone"),
            "daily": daily_forecasts,
            "hourly": hourly_forecasts,
        }

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
