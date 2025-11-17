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
    # Each interest can map to multiple categories for better coverage
    INTEREST_TO_CATEGORIES = {
        # Religious/Cultural Sites
        # Note: Geoapify free tier only supports broad categories like "religion", not subcategories
        "temples": ["religion", "heritage", "tourism"],
        "temple": ["religion", "heritage", "tourism"],
        "shrines": ["religion", "heritage", "tourism"],
        "shrine": ["religion", "heritage", "tourism"],
        "churches": ["religion", "heritage", "tourism"],
        "church": ["religion", "heritage", "tourism"],
        "mosques": ["religion", "heritage", "tourism"],
        "mosque": ["religion", "heritage", "tourism"],
        "synagogues": ["religion", "heritage", "tourism"],
        "synagogue": ["religion", "heritage", "tourism"],

        # Cultural & Tourist Attractions
        "cultural sites": ["heritage", "tourism", "entertainment.museum"],
        "culture": ["heritage", "tourism", "entertainment.museum"],
        "tourist attractions": ["tourism", "heritage"],
        "attractions": ["tourism", "heritage"],
        "landmarks": ["tourism", "heritage"],
        "landmark": ["tourism", "heritage"],
        "monuments": ["heritage", "tourism"],
        "monument": ["heritage", "tourism"],
        "heritage": ["heritage", "tourism"],
        "historic": ["heritage", "tourism"],
        "historical": ["heritage", "tourism"],

        # Food & Drink
        "coffee": ["catering.cafe"],
        "coffee shops": ["catering.cafe"],
        "cafe": ["catering.cafe"],
        "cafes": ["catering.cafe"],
        "restaurants": ["catering.restaurant"],
        "restaurant": ["catering.restaurant"],
        "food": ["catering.restaurant", "catering.cafe", "catering.fast_food"],
        "dining": ["catering.restaurant"],
        "bars": ["catering.bar", "catering.pub"],
        "bar": ["catering.bar", "catering.pub"],
        "pubs": ["catering.pub"],
        "pub": ["catering.pub"],
        "street food": ["catering.fast_food", "catering.restaurant"],

        # Culture & Entertainment
        "museums": ["entertainment.museum"],
        "museum": ["entertainment.museum"],
        "art": ["entertainment.culture", "entertainment.museum"],
        "art galleries": ["entertainment.culture"],
        "gallery": ["entertainment.culture"],
        "galleries": ["entertainment.culture"],
        "theater": ["entertainment.culture"],
        "theatre": ["entertainment.culture"],
        "cinema": ["entertainment.cinema"],
        "movies": ["entertainment.cinema"],

        # Nature & Outdoors
        "parks": ["leisure.park", "natural"],
        "park": ["leisure.park", "natural"],
        "hiking": ["sport.climbing", "leisure.park", "natural"],
        "nature": ["natural", "leisure.park"],
        "gardens": ["leisure.park"],
        "garden": ["leisure.park"],
        "botanical": ["leisure.park"],
        "beach": ["natural.beach", "leisure"],
        "beaches": ["natural.beach", "leisure"],
        "mountains": ["natural.mountain", "natural"],
        "mountain": ["natural.mountain", "natural"],
        "viewpoint": ["tourism.viewpoint"],
        "viewpoints": ["tourism.viewpoint"],

        # Shopping
        "shopping": ["commercial.shopping_mall", "commercial.department_store"],
        "shops": ["commercial"],
        "markets": ["commercial.marketplace"],
        "market": ["commercial.marketplace"],
        "mall": ["commercial.shopping_mall"],
        "malls": ["commercial.shopping_mall"],

        # Activities & Sports
        "sports": ["sport", "leisure"],
        "fitness": ["sport.fitness"],
        "gym": ["sport.fitness"],
        "swimming": ["sport.swimming", "leisure"],
        "spa": ["leisure.spa"],
        "wellness": ["leisure.spa"],

        # Accommodation (for reference, not typically searched)
        "hotels": ["accommodation.hotel"],
        "hotel": ["accommodation.hotel"],
    }

    # Fallback categories for broad interests
    FALLBACK_CATEGORIES = {
        "tourism": ["tourism.attraction", "tourism.sights"],
        "culture": ["tourism.attraction", "entertainment.museum"],
        "general": ["tourism.attraction"],
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
        radius_km: float = 15.0,  # Increased from 10 to 15km for better coverage
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

        # Step 2: Search for POIs for each interest
        all_pois: list[POI] = []
        seen_ids: set[str] = set()

        for interest in interests:
            interest_lower = interest.lower().strip()

            # Get category mapping (list of categories)
            categories = self.INTEREST_TO_CATEGORIES.get(interest_lower)

            pois_found_for_interest = 0

            if categories:
                # Try each category until we get good results
                for category in categories:
                    try:
                        pois = await self.client.search_nearby(
                            latitude=latitude,
                            longitude=longitude,
                            query=None,  # Use category filtering, not text search
                            categories=category,
                            radius_meters=int(radius_km * 1000),
                            limit=limit,
                        )

                        # Deduplicate by id
                        for poi in pois:
                            if poi.id not in seen_ids:
                                seen_ids.add(poi.id)
                                all_pois.append(poi)
                                pois_found_for_interest += 1

                        # If we got enough results (at least 5), break
                        if pois_found_for_interest >= 5:
                            break

                    except Exception as e:
                        # Try next category for this interest
                        continue

                # Note: Text search with query parameter not supported on free tier
                # If we didn't find enough, that's okay - scoring will prioritize what we found

            else:
                # No category mapping - use general tourism category
                try:
                    pois = await self.client.search_nearby(
                        latitude=latitude,
                        longitude=longitude,
                        query=None,
                        categories="tourism",
                        radius_meters=int(radius_km * 1000),
                        limit=limit,
                    )

                    for poi in pois:
                        if poi.id not in seen_ids:
                            seen_ids.add(poi.id)
                            all_pois.append(poi)

                except Exception as e:
                    print(f"Warning: Failed to search for '{interest}': {e}")
                    continue

        # Step 3: Filter out low-quality POIs
        filtered_pois = self._filter_pois(all_pois)

        # Step 4: Score and rank POIs
        scored_pois = self._score_pois(filtered_pois, latitude, longitude, interests)

        # Step 5: Sort by score (highest first)
        scored_pois.sort(key=lambda x: x[1], reverse=True)

        # Return just the POI objects (without scores)
        return [poi for poi, score in scored_pois]

    def _filter_pois(self, pois: list[POI]) -> list[POI]:
        """
        Filter out low-quality or irrelevant POIs.

        Args:
            pois: List of POIs to filter

        Returns:
            Filtered list of POIs
        """
        # Categories to exclude (too generic or not useful for tourists)
        EXCLUDE_CATEGORIES = {
            "building",  # Generic buildings
            "commercial.supermarket",  # Supermarkets
            "service.vehicle",  # Car services
            "service.banking.atm",  # ATMs
            "office",  # Generic offices
        }

        # Keywords that indicate low-quality POIs for tourism
        EXCLUDE_KEYWORDS = [
            "parking",
            "atm",
            "toilet",
            "unnamed",
            "no name",
            "storage",
            "warehouse",
        ]

        filtered = []
        for poi in pois:
            # Skip if category is in exclude list
            if poi.category.lower() in EXCLUDE_CATEGORIES:
                continue

            # Skip if name contains exclude keywords
            name_lower = poi.name.lower()
            if any(keyword in name_lower for keyword in EXCLUDE_KEYWORDS):
                continue

            # Skip POIs with very short names (likely incomplete data)
            if len(poi.name) < 2:
                continue

            filtered.append(poi)

        return filtered

    def _score_pois(
        self, pois: list[POI], center_lat: float, center_lon: float, interests: list[str]
    ) -> list[tuple[POI, float]]:
        """
        Score POIs based on relevance, distance, and category.

        Higher scores = better POIs

        Args:
            pois: List of POIs to score
            center_lat: Center latitude for distance calculation
            center_lon: Center longitude for distance calculation
            interests: User interests for relevance scoring

        Returns:
            List of (POI, score) tuples
        """
        scored = []

        for poi in pois:
            score = 0.0

            # 1. Category bonus (prefer certain types)
            category_lower = poi.category.lower()

            if any(x in category_lower for x in ["religion", "temple", "shrine", "church"]):
                score += 15.0  # Religious sites
            elif "museum" in category_lower:
                score += 12.0  # Museums
            elif "tourism" in category_lower:
                score += 10.0  # Tourist attractions
            elif "heritage" in category_lower:
                score += 13.0  # Heritage sites
            elif "park" in category_lower or "garden" in category_lower:
                score += 8.0  # Parks and gardens
            elif "cafe" in category_lower or "restaurant" in category_lower:
                score += 6.0  # Food and drink
            else:
                score += 3.0  # Everything else

            # 2. Distance penalty (prefer closer POIs, but not too harsh)
            distance_km = self._haversine_distance(
                center_lat, center_lon, poi.latitude, poi.longitude
            )

            if distance_km < 2.0:
                score += 5.0  # Very close
            elif distance_km < 5.0:
                score += 3.0  # Close
            elif distance_km < 10.0:
                score += 1.0  # Moderate distance
            else:
                score -= (distance_km - 10.0) * 0.5  # Penalty for far POIs

            # 3. Name quality bonus
            # POIs with longer names often have better metadata
            if len(poi.name) > 10:
                score += 2.0
            elif len(poi.name) > 20:
                score += 3.0

            # 4. Interest matching bonus
            # Check if POI name or category matches user interests
            name_lower = poi.name.lower()
            for interest in interests:
                interest_lower = interest.lower()
                if interest_lower in name_lower or interest_lower in category_lower:
                    score += 8.0  # Strong match bonus
                    break

            scored.append((poi, score))

        return scored

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
