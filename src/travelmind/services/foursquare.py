"""
Foursquare Places API Client

Client for fetching POIs, restaurants, and attractions from Foursquare.

API Documentation: https://docs.foursquare.com/developer/reference/places-api-overview

Free tier limits:
- 50,000 requests per day
- Rate limit: Good for development

Features:
- Search places by location and query
- Get detailed place information
- Rich categories (restaurants, cafes, museums, parks, etc.)
- Ratings, photos, hours, and more
"""

from typing import Any

import httpx

from ..models.poi import POI, OpeningHours


class FoursquareClient:
    """
    Client for Foursquare Places API.

    Requires API key from https://foursquare.com/developers/
    """

    BASE_URL = "https://api.foursquare.com/v3/places"

    def __init__(self, api_key: str) -> None:
        """
        Initialize Foursquare client.

        Args:
            api_key: Foursquare API key
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": api_key,
                "Accept": "application/json",
                "accept-language": "en",
            },
        )

    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        query: str | None = None,
        categories: list[str] | None = None,
        radius_meters: int = 5000,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Search for places near a location.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            query: Free-text search query (e.g., "coffee", "temples")
            categories: Foursquare category IDs to filter by
            radius_meters: Search radius in meters (max 100000)
            limit: Maximum results (max 50)

        Returns:
            List of place dictionaries from Foursquare API
        """
        params: dict[str, Any] = {
            "ll": f"{latitude},{longitude}",
            "radius": min(radius_meters, 100000),
            "limit": min(limit, 50),
        }

        if query:
            params["query"] = query

        if categories:
            params["categories"] = ",".join(categories)

        # Use the nearby endpoint instead of deprecated search
        response = await self.client.get(f"{self.BASE_URL}/nearby", params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    async def get_place_details(self, fsq_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific place.

        Args:
            fsq_id: Foursquare place ID

        Returns:
            Detailed place information
        """
        response = await self.client.get(
            f"{self.BASE_URL}/{fsq_id}",
            params={"fields": "fsq_id,name,location,categories,rating,hours,photos,website,description"},
        )
        response.raise_for_status()
        return response.json()

    def convert_to_poi(self, place_data: dict[str, Any]) -> POI:
        """
        Convert Foursquare place data to our POI model.

        Args:
            place_data: Raw place data from Foursquare API

        Returns:
            POI object
        """
        location = place_data.get("geocodes", {}).get("main", {})
        latitude = location.get("latitude", 0.0)
        longitude = location.get("longitude", 0.0)

        # Extract category
        categories = place_data.get("categories", [])
        primary_category = categories[0].get("name", "Unknown") if categories else "Unknown"
        tags = [cat.get("name", "") for cat in categories]

        # Extract address
        loc_info = place_data.get("location", {})
        address_parts = [
            loc_info.get("address"),
            loc_info.get("locality"),
            loc_info.get("region"),
        ]
        address = ", ".join(filter(None, address_parts)) or None

        # Rating (Foursquare uses 0-10 scale, convert to 0-5)
        raw_rating = place_data.get("rating")
        rating = (raw_rating / 2.0) if raw_rating else None

        # Photos
        photos = place_data.get("photos", [])
        image_url = None
        if photos:
            photo = photos[0]
            prefix = photo.get("prefix", "")
            suffix = photo.get("suffix", "")
            image_url = f"{prefix}original{suffix}" if prefix and suffix else None

        # Opening hours (simplified - Foursquare format is complex)
        opening_hours = None
        hours_data = place_data.get("hours")
        if hours_data and "regular" in hours_data:
            # TODO: Parse Foursquare hours format properly
            opening_hours = OpeningHours()

        return POI(
            id=place_data.get("fsq_id", ""),
            source="foursquare",
            name=place_data.get("name", "Unnamed Place"),
            category=primary_category,
            tags=tags,
            latitude=latitude,
            longitude=longitude,
            address=address,
            description=place_data.get("description"),
            opening_hours=opening_hours,
            estimated_visit_duration_minutes=self._estimate_visit_duration(primary_category),
            rating=rating,
            popularity_score=self._calculate_popularity(place_data),
            admission_fee=None,  # Foursquare doesn't provide this
            website=place_data.get("website"),
            phone=place_data.get("tel"),
            image_url=image_url,
        )

    def _estimate_visit_duration(self, category: str) -> int:
        """
        Estimate typical visit duration based on category.

        Args:
            category: Place category

        Returns:
            Estimated duration in minutes
        """
        category_lower = category.lower()

        if any(word in category_lower for word in ["museum", "gallery", "aquarium", "zoo"]):
            return 120
        elif any(word in category_lower for word in ["restaurant", "cafe", "coffee"]):
            return 60
        elif any(word in category_lower for word in ["temple", "shrine", "church", "monument"]):
            return 45
        elif any(word in category_lower for word in ["park", "garden", "viewpoint"]):
            return 60
        elif any(word in category_lower for word in ["shop", "store", "market"]):
            return 30
        else:
            return 60  # Default

    def _calculate_popularity(self, place_data: dict[str, Any]) -> float:
        """
        Calculate normalized popularity score from Foursquare data.

        Args:
            place_data: Raw place data

        Returns:
            Popularity score between 0.0 and 1.0
        """
        # Use rating as a proxy for popularity
        rating = place_data.get("rating", 5.0)
        # Normalize 0-10 scale to 0-1
        return min(rating / 10.0, 1.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
