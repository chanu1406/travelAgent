"""
Itinerary Models

Pydantic models for finalized trip itineraries.
"""

from datetime import date, time

from pydantic import BaseModel, Field

from .poi import POI


class ItineraryItem(BaseModel):
    """A single item in the itinerary (POI visit, meal, travel, etc.)."""

    type: str = Field(
        description="'poi', 'meal', 'travel', 'rest', 'free_time'"
    )
    start_time: time
    end_time: time
    duration_minutes: int

    # For POI items
    poi: POI | None = None

    # For travel items
    travel_mode: str | None = Field(
        default=None,
        description="'walking', 'driving', 'transit'"
    )
    distance_km: float | None = None
    origin_coords: tuple[float, float] | None = None
    destination_coords: tuple[float, float] | None = None

    # General
    title: str = Field(description="Display title for this item")
    description: str | None = Field(
        default=None,
        description="Additional notes or details"
    )
    notes: str | None = Field(
        default=None,
        description="User-editable notes"
    )

    # Metadata
    locked: bool = Field(
        default=False,
        description="If true, this item won't be modified by HITL edits"
    )


class DayItinerary(BaseModel):
    """Itinerary for a single day."""

    date: date
    day_number: int = Field(description="Day 1, 2, 3, etc.")
    items: list[ItineraryItem]

    # Summary stats
    total_walking_km: float = 0.0
    total_poi_count: int = 0
    total_active_minutes: int = 0

    # Weather context
    weather_summary: str | None = None
    weather_category: str | None = None


class Itinerary(BaseModel):
    """
    Complete trip itinerary.

    The final output of the planning process, ready for export.
    """

    # Trip metadata
    title: str = Field(description="Trip title (e.g., '4 Days in Kyoto')")
    destinations: list[str]
    start_date: date
    end_date: date
    total_days: int

    # Daily schedules
    days: list[DayItinerary]

    # Trip summary
    total_pois: int
    total_walking_km: float
    interests_covered: list[str] = Field(
        default_factory=list,
        description="List of user interests addressed"
    )

    # User context
    user_notes: str | None = Field(
        default=None,
        description="User-provided notes or preferences"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about infeasible constraints or issues"
    )

    # Version control for HITL
    version: int = Field(
        default=1,
        description="Version number for tracking HITL edits"
    )
    finalized: bool = Field(
        default=False,
        description="True if user has approved this itinerary"
    )
