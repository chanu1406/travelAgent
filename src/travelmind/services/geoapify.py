"""
Geoapify Places API Client

Client for fetching POIs, restaurants, and attractions from Geoapify.

API Documentation: https://apidocs.geoapify.com/docs/places/

Free tier limits:
- 3,000 requests per day
- Rate limit: Good for development

Features:
- Search places by location and category
- Rich POI data (restaurants, cafes, museums, parks, etc.)
- No credit card required for free tier
- Ratings, addresses, and more
"""

from typing import Any

import httpx

from ..models.poi import POI, OpeningHours


class GeoapifyClient:
    """
    Client for Geoapify Places API.

    Requires API key from https://www.geoapify.com/
    """

    BASE_URL = "https://api.geoapify.com/v2/places"

    def __init__(self, api_key: str) -> None:
        """
        Initialize Geoapify client.

        Args:
            api_key: Geoapify API key
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        query: str | None = None,
        categories: str | None = None,
        radius_meters: int = 5000,
        limit: int = 50,
    ) -> list[POI]:
        """
        Search for places near a location.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            query: Free-text search query (e.g., "coffee", "temples")
            categories: Geoapify category filter string (e.g., "tourism.attraction" or "catering.cafe")
            radius_meters: Search radius in meters (max 50000)
            limit: Maximum results (max 500)

        Returns:
            List of POI objects
        """
        params: dict[str, Any] = {
            "lat": latitude,
            "lon": longitude,
            "radius": min(radius_meters, 50000),
            "limit": min(limit, 500),
            "apiKey": self.api_key,
        }

        if categories:
            params["categories"] = categories

        if query:
            params["filter"] = f"circle:{longitude},{latitude},{min(radius_meters, 50000)}"
            params["text"] = query

        response = await self.client.get(f"{self.BASE_URL}", params=params)
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        # Convert raw features to POI objects
        return [self.convert_to_poi(feature) for feature in features]

    async def get_place_details(self, place_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific place.

        Args:
            place_id: Geoapify place ID

        Returns:
            Detailed place information
        """
        params = {
            "id": place_id,
            "apiKey": self.api_key,
        }

        response = await self.client.get(f"{self.BASE_URL}", params=params)
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])
        return features[0] if features else {}

    def convert_to_poi(self, place_data: dict[str, Any]) -> POI:
        """
        Convert Geoapify place data to our POI model.

        Args:
            place_data: Raw place data from Geoapify API (GeoJSON feature)

        Returns:
            POI object
        """
        properties = place_data.get("properties", {})
        geometry = place_data.get("geometry", {})
        coordinates = geometry.get("coordinates", [0, 0])

        # Geoapify uses [lon, lat] order
        longitude = coordinates[0]
        latitude = coordinates[1]

        # Extract category
        categories = properties.get("categories", [])
        primary_category = categories[0] if categories else "Unknown"

        # Clean up category name (remove dots, capitalize)
        category_display = primary_category.split(".")[-1].replace("_", " ").title()

        # Extract address
        address = properties.get("formatted", properties.get("address_line1"))

        # Extract name
        name = properties.get("name", properties.get("address_line1", "Unnamed Place"))

        # Opening hours (Geoapify provides this in opening_hours field)
        opening_hours = None
        hours_data = properties.get("opening_hours")
        if hours_data:
            # TODO: Parse Geoapify hours format properly
            opening_hours = OpeningHours()

        # Website and contact
        website = properties.get("website") or properties.get("contact", {}).get("website")
        phone = properties.get("contact", {}).get("phone")

        return POI(
            id=properties.get("place_id", ""),
            source="geoapify",
            name=name,
            category=category_display,
            tags=categories,
            latitude=latitude,
            longitude=longitude,
            address=address,
            description=None,  # Geoapify doesn't provide descriptions
            opening_hours=opening_hours,
            estimated_visit_duration_minutes=self._estimate_visit_duration(primary_category),
            rating=None,  # Geoapify free tier doesn't include ratings
            popularity_score=0.5,  # Default since no rating available
            admission_fee=None,
            website=website,
            phone=phone,
            image_url=None,  # Geoapify doesn't provide images in free tier
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
        elif any(word in category_lower for word in ["restaurant", "cafe", "coffee", "catering"]):
            return 60
        elif any(word in category_lower for word in ["temple", "shrine", "church", "monument", "tourism"]):
            return 45
        elif any(word in category_lower for word in ["park", "garden", "natural"]):
            return 60
        elif any(word in category_lower for word in ["shop", "store", "commercial"]):
            return 30
        else:
            return 60  # Default

    async def geocode(self, location: str) -> dict[str, Any] | None:
        """
        Geocode a location name to coordinates.

        Args:
            location: Location name (e.g., "Kyoto, Japan", "Paris, France")

        Returns:
            Dictionary with latitude, longitude, and formatted address, or None if not found
        """
        url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            "text": location,
            "limit": 1,
            "apiKey": self.api_key,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        if not features:
            return None

        # Extract first result
        feature = features[0]
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [0, 0])

        return {
            "latitude": coordinates[1],  # Geoapify uses [lon, lat]
            "longitude": coordinates[0],
            "formatted": properties.get("formatted", ""),
            "city": properties.get("city", ""),
            "country": properties.get("country", ""),
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
