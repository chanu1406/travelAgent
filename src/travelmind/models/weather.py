"""
Weather Models

Pydantic models for weather forecast data.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class HourlyForecast(BaseModel):
    """Weather forecast for a specific hour."""

    timestamp: datetime
    temperature_celsius: float
    feels_like_celsius: float
    precipitation_probability: float = Field(ge=0.0, le=1.0)
    precipitation_mm: float = Field(ge=0.0)
    wind_speed_kmh: float
    weather_code: int = Field(
        description="WMO weather code (0=clear, 61=rain, etc.)"
    )
    weather_description: str = Field(
        description="Human-readable weather condition"
    )


class DailyForecast(BaseModel):
    """Weather forecast summary for a full day."""

    date: date
    temperature_max_celsius: float
    temperature_min_celsius: float
    precipitation_probability: float = Field(ge=0.0, le=1.0)
    precipitation_sum_mm: float = Field(ge=0.0)
    wind_speed_max_kmh: float
    weather_code: int
    weather_description: str
    sunrise: datetime
    sunset: datetime

    # Derived fields
    category: str = Field(
        default="good",
        description="'excellent', 'good', 'fair', 'indoor', 'challenging'"
    )
    best_activity_window: tuple[int, int] | None = Field(
        default=None,
        description="(start_hour, end_hour) for best outdoor conditions"
    )

    # Hourly breakdown
    hourly: list[HourlyForecast] = Field(default_factory=list)


class WeatherForecast(BaseModel):
    """Complete weather forecast for a trip."""

    location: str
    latitude: float
    longitude: float
    timezone: str
    forecasts: list[DailyForecast] = Field(
        description="Daily forecasts, chronologically ordered"
    )
