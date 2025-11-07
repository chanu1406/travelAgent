"""
Routing Service Client

Unified client for routing services (OSRM or OpenRouteService).

Supports:
- OSRM (Open Source Routing Machine): Free, no key, self-hosted or public demo
- OpenRouteService: Free tier with API key, more features

Both provide:
- Walking, driving, cycling routes
- Distance and duration
- Turn-by-turn directions
- Route geometry (coordinates)

This module abstracts the differences between providers.
"""

from typing import Any, Literal

import httpx


RouteProfile = Literal["walking", "driving", "cycling"]


class OSRMClient:
    """
    Client for OSRM (Open Source Routing Machine).

    No API key required. Can use public demo or self-hosted instance.
    """

    BASE_URL = "http://router.project-osrm.org"

    def __init__(self, base_url: str | None = None) -> None:
        """
        Initialize OSRM client.

        Args:
            base_url: OSRM server URL (defaults to public demo)
        """
        self.base_url = base_url or self.BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_route(
        self,
        coordinates: list[tuple[float, float]],
        profile: RouteProfile = "walking",
    ) -> dict[str, Any]:
        """
        Calculate route between coordinates.

        Args:
            coordinates: List of (lat, lon) tuples
            profile: "walking", "driving", or "cycling"

        Returns:
            Route data with distance, duration, and geometry

        Raises:
            httpx.HTTPError: If the request fails
        """
        # Convert profile to OSRM profile name
        profile_map = {
            "walking": "foot",
            "driving": "car",
            "cycling": "bike",
        }
        osrm_profile = profile_map.get(profile, "foot")

        # Convert coordinates from (lat, lon) to "lon,lat;lon,lat" format
        coord_string = ";".join(f"{lon},{lat}" for lat, lon in coordinates)

        # Build URL
        url = f"{self.base_url}/route/v1/{osrm_profile}/{coord_string}"

        # Request with geometry in GeoJSON format for easier parsing
        params = {
            "overview": "full",
            "geometries": "geojson",
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data["code"] != "Ok":
            raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")

        # Extract the first route
        route = data["routes"][0]

        return {
            "distance": route["distance"],  # meters
            "duration": route["duration"],  # seconds
            "geometry": route["geometry"],  # GeoJSON LineString
        }

    async def get_table(
        self,
        coordinates: list[tuple[float, float]],
        profile: RouteProfile = "walking",
    ) -> dict[str, Any]:
        """
        Get distance/time matrix for multiple points.

        Args:
            coordinates: List of (lat, lon) tuples
            profile: "walking", "driving", or "cycling"

        Returns:
            Matrix of distances (meters) and durations (seconds)
            Format: {"durations": [[float]], "distances": [[float]]}

        Raises:
            httpx.HTTPError: If the request fails
        """
        # Convert profile to OSRM profile name
        profile_map = {
            "walking": "foot",
            "driving": "car",
            "cycling": "bike",
        }
        osrm_profile = profile_map.get(profile, "foot")

        # Convert coordinates from (lat, lon) to "lon,lat;lon,lat" format
        coord_string = ";".join(f"{lon},{lat}" for lat, lon in coordinates)

        # Build URL
        url = f"{self.base_url}/table/v1/{osrm_profile}/{coord_string}"

        # Request both distances and durations
        params = {
            "annotations": "distance,duration",
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data["code"] != "Ok":
            raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")

        return {
            "durations": data["durations"],  # seconds, row-major matrix
            "distances": data["distances"],  # meters, row-major matrix
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


class OpenRouteServiceClient:
    """
    Client for OpenRouteService API.

    Requires free API key from https://openrouteservice.org/
    """

    BASE_URL = "https://api.openrouteservice.org"

    def __init__(self, api_key: str) -> None:
        """
        Initialize OpenRouteService client.

        Args:
            api_key: OpenRouteService API key
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": api_key},
        )

    async def get_route(
        self,
        coordinates: list[tuple[float, float]],
        profile: RouteProfile = "walking",
    ) -> dict[str, Any]:
        """
        Calculate route between coordinates.

        Args:
            coordinates: List of (lat, lon) tuples
            profile: "walking", "driving", or "cycling"

        Returns:
            Route data with distance, duration, and geometry
        """
        raise NotImplementedError("OpenRouteService routing to be implemented")

    async def get_matrix(
        self,
        coordinates: list[tuple[float, float]],
        profile: RouteProfile = "walking",
    ) -> dict[str, Any]:
        """
        Get distance/time matrix for multiple points.

        Args:
            coordinates: List of (lat, lon) tuples
            profile: "walking", "driving", or "cycling"

        Returns:
            Matrix of distances and durations
        """
        raise NotImplementedError("OpenRouteService matrix to be implemented")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


class RoutingService:
    """
    Unified routing service that abstracts provider differences.

    Automatically selects between OSRM and OpenRouteService based on configuration.
    """

    def __init__(
        self,
        provider: Literal["osrm", "openrouteservice"] = "osrm",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """
        Initialize routing service.

        Args:
            provider: "osrm" or "openrouteservice"
            api_key: Required for OpenRouteService
            base_url: Optional custom OSRM server URL
        """
        if provider == "osrm":
            self.client: OSRMClient | OpenRouteServiceClient = OSRMClient(base_url)
        elif provider == "openrouteservice":
            if not api_key:
                raise ValueError("OpenRouteService requires an API key")
            self.client = OpenRouteServiceClient(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def get_route(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profile: RouteProfile = "walking",
    ) -> dict[str, Any]:
        """Get route between two points."""
        return await self.client.get_route([origin, destination], profile)

    async def get_distance_matrix(
        self,
        coordinates: list[tuple[float, float]],
        profile: RouteProfile = "walking",
    ) -> list[list[float]]:
        """Get all-pairs distance matrix."""
        raise NotImplementedError("Distance matrix wrapper to be implemented")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.close()
