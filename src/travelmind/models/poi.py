"""
POI (Point of Interest) Models

Pydantic models for attractions, restaurants, and activities.
"""

from pydantic import BaseModel, Field


class OpeningHours(BaseModel):
    """Opening hours for a POI."""

    monday: str | None = None
    tuesday: str | None = None
    wednesday: str | None = None
    thursday: str | None = None
    friday: str | None = None
    saturday: str | None = None
    sunday: str | None = None
    notes: str | None = Field(
        default=None,
        description="Special notes (e.g., 'Closed on public holidays')"
    )


class POI(BaseModel):
    """
    Point of Interest with all relevant metadata.

    Represents an attraction, restaurant, park, or any visitable location.
    """

    id: str = Field(description="Unique identifier (from data source)")
    source: str = Field(description="Data source: 'foursquare', 'osm', etc.")
    name: str
    category: str = Field(
        description="Primary category (e.g., 'temple', 'museum', 'cafe')"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Additional tags for filtering"
    )

    # Location
    latitude: float
    longitude: float
    address: str | None = None

    # Details
    description: str | None = None
    opening_hours: OpeningHours | None = None
    estimated_visit_duration_minutes: int = Field(
        default=60,
        description="Typical time to spend at this POI"
    )

    # Quality indicators
    rating: float | None = Field(
        default=None,
        ge=0.0,
        le=5.0,
        description="User rating (0-5 scale)"
    )
    popularity_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Normalized popularity score"
    )

    # Cost
    admission_fee: str | None = Field(
        default=None,
        description="Admission cost info (e.g., 'Free', '$10', '¥500')"
    )

    # Metadata
    website: str | None = None
    phone: str | None = None
    image_url: str | None = None


class POISearchResult(BaseModel):
    """Result set from a POI search query."""

    query: str = Field(description="Original search query")
    location: str = Field(description="Search location")
    pois: list[POI]
    total_found: int
    search_radius_km: float
