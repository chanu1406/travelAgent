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

    def is_indoor(self) -> bool:
        """
        Determine if this POI is primarily indoors.

        Returns:
            True if indoor, False if outdoor
        """
        category_lower = self.category.lower()

        # Definitely indoor categories
        indoor_keywords = [
            "museum",
            "entertainment",
            "cafe",
            "restaurant",
            "bar",
            "pub",
            "shopping",
            "mall",
            "cinema",
            "theater",
            "theatre",
            "spa",
            "fitness",
            "gym",
        ]

        return any(keyword in category_lower for keyword in indoor_keywords)

    def is_outdoor(self) -> bool:
        """
        Determine if this POI is primarily outdoors.

        Returns:
            True if outdoor, False if indoor
        """
        category_lower = self.category.lower()

        # Definitely outdoor categories
        outdoor_keywords = [
            "park",
            "garden",
            "natural",
            "beach",
            "mountain",
            "viewpoint",
            "hiking",
            "sport.climbing",
        ]

        # Religious sites (temples, shrines) are often outdoor
        if any(keyword in category_lower for keyword in outdoor_keywords):
            return True

        # Temples, shrines, monuments are typically outdoor experiences
        if any(keyword in category_lower for keyword in ["religion", "heritage"]):
            return True

        return False

    def is_weather_sensitive(self) -> bool:
        """
        Determine if this POI experience is heavily affected by weather.

        Returns:
            True if weather-sensitive (should avoid in bad weather)
        """
        category_lower = self.category.lower()

        # Highly weather-dependent activities
        sensitive_keywords = [
            "beach",
            "hiking",
            "mountain",
            "viewpoint",
            "park",
            "garden",
            "natural",
            "sport.climbing",
        ]

        return any(keyword in category_lower for keyword in sensitive_keywords)

    def get_weather_suitability(self) -> str:
        """
        Get the weather preference for this POI.

        Returns:
            "indoor" - best for any weather (museums, cafes)
            "outdoor" - requires good weather (parks, temples)
            "flexible" - can work in various conditions
        """
        if self.is_indoor():
            return "indoor"
        elif self.is_weather_sensitive():
            return "outdoor"
        elif self.is_outdoor():
            return "outdoor"
        else:
            return "flexible"


class POISearchResult(BaseModel):
    """Result set from a POI search query."""

    query: str = Field(description="Original search query")
    location: str = Field(description="Search location")
    pois: list[POI]
    total_found: int
    search_radius_km: float
