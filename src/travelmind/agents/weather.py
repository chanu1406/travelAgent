"""
Weather Agent

Responsible for fetching weather forecasts to inform scheduling decisions.

Uses Open-Meteo API (free, no key required) to get:
- 7-day hourly forecasts
- Temperature, precipitation, wind
- Weather codes (clear, rain, snow, etc.)

The agent helps the Calendar Agent make smart scheduling decisions:
- Outdoor activities on nice days
- Indoor attractions during rain
- Avoid exposed viewpoints in high wind
- Adjust daily schedules based on temperature patterns

Weather data is cached to minimize API calls.
"""

from datetime import date
from typing import Any, Literal

from ..services.openmeteo import OpenMeteoClient


class WeatherAgent:
    """
    Fetches weather forecasts for trip planning.

    Uses Open-Meteo API to retrieve:
    - Temperature and "feels like" temp
    - Precipitation probability and amount
    - Wind speed
    - Weather conditions (clear, cloudy, rain, etc.)
    """

    def __init__(self) -> None:
        """Initialize weather agent with Open-Meteo client."""
        self.client = OpenMeteoClient()

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        """
        Fetch weather forecast for a location and date range.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: First day of trip
            end_date: Last day of trip

        Returns:
            Weather forecast data with daily and hourly breakdowns
        """
        return await self.client.get_forecast(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            timezone="auto",
        )

    def categorize_day(
        self, day_forecast: dict[str, Any]
    ) -> Literal["excellent", "good", "fair", "indoor", "challenging"]:
        """
        Categorize a day's weather as indoor-friendly, outdoor-friendly, etc.

        Args:
            day_forecast: Single day forecast data

        Returns:
            Category: "excellent", "good", "fair", "indoor", "challenging"
        """
        temp_max = day_forecast.get("temperature_max_celsius", 20)
        temp_min = day_forecast.get("temperature_min_celsius", 10)
        precipitation = day_forecast.get("precipitation_sum_mm", 0)
        precip_prob = day_forecast.get("precipitation_probability", 0)
        wind_speed = day_forecast.get("wind_speed_max_kmh", 0)

        # Excellent: Perfect outdoor weather
        if (
            10 <= temp_max <= 28
            and precipitation < 0.5
            and precip_prob < 0.2
            and wind_speed < 20
        ):
            return "excellent"

        # Good: Generally pleasant but not perfect
        if (
            5 <= temp_max <= 32
            and precipitation < 2
            and precip_prob < 0.4
            and wind_speed < 30
        ):
            return "good"

        # Fair: Acceptable for outdoor activities with precautions
        if precipitation < 5 and precip_prob < 0.6 and wind_speed < 40:
            return "fair"

        # Indoor: Heavy rain or extreme conditions
        if precipitation > 10 or precip_prob > 0.7 or wind_speed > 50:
            return "indoor"

        # Challenging: Poor but manageable
        return "challenging"

    def get_best_time_window(
        self, hourly_forecasts: list[dict[str, Any]], activity_type: str
    ) -> tuple[int, int]:
        """
        Find the best time window for an activity type.

        Args:
            hourly_forecasts: List of hourly forecast data for a day
            activity_type: "outdoor", "walking", "viewpoint", etc.

        Returns:
            Tuple of (start_hour, end_hour) for optimal conditions
        """
        if not hourly_forecasts:
            return (9, 18)  # Default 9 AM to 6 PM

        # Score each hour based on activity type
        scores = []
        for hour_data in hourly_forecasts:
            score = self._score_hour_for_activity(hour_data, activity_type)
            scores.append(score)

        # Find the best continuous window (minimum 4 hours)
        window_size = 4
        best_start = 0
        best_score = 0

        for i in range(len(scores) - window_size + 1):
            window_score = sum(scores[i : i + window_size])
            if window_score > best_score:
                best_score = window_score
                best_start = i

        # Extract hour from timestamp (assumes hourly_forecasts is sorted by time)
        start_hour = 9  # Default fallback
        end_hour = 18

        if hourly_forecasts:
            # Parse hour from timestamp (format: "2025-11-06T09:00")
            start_time = hourly_forecasts[best_start].get("timestamp", "")
            if "T" in start_time:
                start_hour = int(start_time.split("T")[1].split(":")[0])
                end_hour = min(start_hour + window_size, 20)  # Max 8 PM

        return (start_hour, end_hour)

    def _score_hour_for_activity(
        self, hour_data: dict[str, Any], activity_type: str
    ) -> float:
        """
        Score an hour's weather suitability for an activity.

        Args:
            hour_data: Hourly weather data
            activity_type: Type of activity

        Returns:
            Score from 0 (worst) to 10 (best)
        """
        temp = hour_data.get("temperature_celsius", 15)
        precip_prob = hour_data.get("precipitation_probability", 0)
        wind = hour_data.get("wind_speed_kmh", 0)

        score = 10.0

        # Temperature penalties
        if activity_type in ["outdoor", "walking", "viewpoint"]:
            if temp < 5 or temp > 35:
                score -= 5
            elif temp < 10 or temp > 30:
                score -= 2

        # Precipitation penalties
        score -= precip_prob * 8  # Heavy penalty for rain

        # Wind penalties (especially for viewpoints)
        if activity_type == "viewpoint":
            if wind > 40:
                score -= 5
            elif wind > 25:
                score -= 2

        return max(0, score)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.close()
