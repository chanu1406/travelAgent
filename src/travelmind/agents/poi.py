"""
POI (Point of Interest) Agent

Responsible for finding attractions, restaurants, and activities that match user interests.

Data sources:
- Geoapify Places API: Comprehensive POI data from OpenStreetMap and proprietary sources
- Filters by category, rating, and user preferences

The agent:
1. Geocodes the location name to coordinates
2. Translates user interests into Geoapify categories (e.g., "temples" → religious)
3. Fetches POIs from Geoapify API
4. Deduplicates and merges results
5. Ranks by relevance and quality
6. Returns structured POI data with coordinates, descriptions, and metadata

Output includes:
- Name, description, category
- Coordinates (lat/lon)
- Opening hours (if available)
- Estimated visit duration
- Rating/popularity score
- Tags matching user interests
"""

from typing import Any

from ..models.poi import POI
from ..services.geoapify import GeoapifyClient
from ..utils.config import settings


class POIAgent:
    """
    Discovers points of interest matching user preferences.

    Uses Geoapify Places API to find:
    - Attractions (museums, landmarks, viewpoints)
    - Food & drink (restaurants, cafes, bars)
    - Activities (parks, shops, entertainment)
    """

    # Map user interest keywords to Geoapify categories
    INTEREST_TO_CATEGORY = {
        # Religious/Cultural
        "temples": "religion",
        "temple": "religion",
        "shrines": "religion",
        "shrine": "religion",
        "churches": "religion.christian",
        "church": "religion.christian",
        "mosques": "religion.muslim",
        "mosque": "religion.muslim",

        # Food & Drink
        "coffee": "catering.cafe",
        "coffee shops": "catering.cafe",
        "cafe": "catering.cafe",
        "cafes": "catering.cafe",
        "restaurants": "catering.restaurant",
        "restaurant": "catering.restaurant",
        "food": "catering",
        "bars": "catering.bar",
        "bar": "catering.bar",

        # Culture & Entertainment
        "museums": "entertainment.museum",
        "museum": "entertainment.museum",
        "art": "entertainment.culture",
        "art galleries": "entertainment.culture",
        "gallery": "entertainment.culture",
        "galleries": "entertainment.culture",
        "theater": "entertainment.culture",
        "theatre": "entertainment.culture",

        # Nature & Outdoors
        "parks": "leisure.park",
        "park": "leisure.park",
        "hiking": "leisure.park",
        "nature": "leisure.park",
        "gardens": "leisure.park",
        "garden": "leisure.park",

        # Shopping
        "shopping": "commercial.shopping_mall",
        "shops": "commercial",
        "markets": "commercial.marketplace",
        "market": "commercial.marketplace",

        # Accommodation
        "hotels": "accommodation",
        "hotel": "accommodation.hotel",
    }

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize POI agent with Geoapify client.

        Args:
            api_key: Geoapify API key (uses settings.geoapify_api_key if not provided)
        """
        if api_key is None:
            api_key = settings.geoapify_api_key
            if not api_key:
                raise ValueError("Geoapify API key is required (GEOAPIFY_API_KEY in .env)")

        self.client = GeoapifyClient(api_key=api_key)

    async def search(
        self,
        location: str,
        interests: list[str],
        radius_km: float = 10.0,
        limit: int = 50,
    ) -> list[POI]:
        """
        Search for POIs matching interests in a location.

        Args:
            location: City or region name
            interests: List of interest keywords (e.g., ["temples", "coffee"])
            radius_km: Search radius in kilometers
            limit: Maximum number of results per interest

        Returns:
            List of POI objects with name, coords, category, etc.
        """
        # Step 1: Geocode the location to get coordinates
        geocode_result = await self.client.geocode(location)
        if not geocode_result:
            raise ValueError(f"Could not geocode location: {location}")

        latitude = geocode_result["latitude"]
        longitude = geocode_result["longitude"]

        # Step 2: Map interests to Geoapify categories
        categories = []
        for interest in interests:
            interest_lower = interest.lower().strip()
            if interest_lower in self.INTEREST_TO_CATEGORY:
                categories.append(self.INTEREST_TO_CATEGORY[interest_lower])
            # If no mapping found, try searching with the raw keyword
            else:
                categories.append(None)  # Will use query parameter instead

        # Step 3: Search for POIs for each interest
        all_pois: list[POI] = []
        seen_ids: set[str] = set()

        for i, interest in enumerate(interests):
            category = categories[i]
            query = interest if category is None else None

            try:
                pois = await self.client.search_nearby(
                    latitude=latitude,
                    longitude=longitude,
                    query=query,
                    categories=category,
                    radius_meters=int(radius_km * 1000),
                    limit=limit,
                )

                # Deduplicate by id
                for poi in pois:
                    if poi.id not in seen_ids:
                        seen_ids.add(poi.id)
                        all_pois.append(poi)

            except Exception as e:
                # Log error but continue with other interests
                print(f"Warning: Failed to search for '{interest}': {e}")
                continue

        # Step 4: Sort by distance from center (closest first)
        all_pois.sort(key=lambda p: self._haversine_distance(
            latitude, longitude, p.latitude, p.longitude
        ))

        return all_pois

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points on Earth.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        from math import asin, cos, radians, sin, sqrt

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Earth radius in kilometers
        r = 6371.0

        return c * r

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.close()
