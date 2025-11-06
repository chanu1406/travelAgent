"""
Request Models

Pydantic models for user travel requests and parsed parameters.

These models ensure type safety and validation throughout the system.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class TravelRequest(BaseModel):
    """
    Structured representation of a travel planning request.

    Parsed from natural language by the Intent Agent.
    """

    destinations: list[str] = Field(
        description="List of cities or regions to visit"
    )
    start_date: date | None = Field(
        default=None,
        description="Trip start date (optional if duration is specified)"
    )
    end_date: date | None = Field(
        default=None,
        description="Trip end date (optional if duration is specified)"
    )
    duration_days: int | None = Field(
        default=None,
        description="Trip duration in days (alternative to explicit dates)"
    )
    interests: list[str] = Field(
        default_factory=list,
        description="User interests (e.g., 'temples', 'coffee shops', 'hiking')"
    )
    mobility: Literal["walking", "driving", "cycling", "transit"] = Field(
        default="walking",
        description="Preferred mode of transportation"
    )
    pace: Literal["relaxed", "moderate", "packed"] = Field(
        default="moderate",
        description="Preferred pace of activities"
    )
    max_walk_km_per_day: float = Field(
        default=10.0,
        description="Maximum walking distance per day in kilometers"
    )
    budget_level: Literal["budget", "moderate", "luxury"] | None = Field(
        default=None,
        description="Budget constraint level"
    )
    accommodation_location: tuple[float, float] | None = Field(
        default=None,
        description="(lat, lon) of hotel/accommodation if known"
    )
    must_see: list[str] = Field(
        default_factory=list,
        description="Specific POIs that must be included"
    )
    avoid: list[str] = Field(
        default_factory=list,
        description="Categories or specific places to avoid"
    )
    dietary_restrictions: list[str] = Field(
        default_factory=list,
        description="Dietary restrictions for restaurant suggestions"
    )

    # Metadata
    raw_query: str = Field(
        description="Original user query for reference"
    )


class TravelConstraints(BaseModel):
    """User constraints and preferences for itinerary building."""

    max_walk_km_per_day: float = 10.0
    max_pois_per_day: int = 6
    preferred_start_time: str = "09:00"
    preferred_end_time: str = "18:00"
    meal_break_duration_minutes: int = 60
    min_poi_visit_minutes: int = 30
    buffer_time_percentage: float = 0.15  # 15% buffer for unexpected delays
