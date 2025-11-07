"""
Route Agent

Responsible for calculating travel times and optimal routes between POIs.

Uses routing services to compute:
- Walking, driving, or cycling routes
- Distance and estimated travel time
- Turn-by-turn directions (if needed)

Routing sources (choose based on availability):
- OSRM (Open Source Routing Machine): Free, no key, walking/driving/cycling
- OpenRouteService: Free tier with API key, more features

The Route Agent helps the Calendar Agent:
1. Cluster nearby POIs for efficient daily routes
2. Validate that daily itineraries are feasible (total walking time)
3. Minimize backtracking
4. Respect user's mobility preferences (max walk distance, prefer transit, etc.)

Results are heavily cached since routes don't change frequently.
"""

from typing import Any, Literal

from ..models.poi import POI
from ..services.routing import OSRMClient, RouteProfile
from ..utils.config import settings


TransportMode = Literal["walking", "driving", "cycling", "transit"]


class RouteAgent:
    """
    Computes routes and travel times between locations.

    Supports multiple transport modes:
    - Walking (default for city trips)
    - Driving
    - Cycling
    - Public transit (future)
    """

    def __init__(self, provider: str = "osrm") -> None:
        """
        Initialize route agent with preferred routing provider.

        Args:
            provider: "osrm" or "openrouteservice"
        """
        if provider == "osrm":
            self.client = OSRMClient(base_url=settings.osrm_base_url)
        else:
            raise NotImplementedError(f"Provider '{provider}' not yet supported")

    async def get_route(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        mode: TransportMode = "walking",
    ) -> dict[str, Any]:
        """
        Calculate route between two points.

        Args:
            origin: (latitude, longitude) tuple
            destination: (latitude, longitude) tuple
            mode: Transport mode

        Returns:
            Route data with distance (meters), duration (seconds), and geometry
        """
        profile: RouteProfile = mode  # type: ignore
        return await self.client.get_route(
            coordinates=[origin, destination],
            profile=profile,
        )

    async def get_distance_matrix(
        self,
        locations: list[tuple[float, float]],
        mode: TransportMode = "walking",
    ) -> list[list[float]]:
        """
        Get all-pairs distance/time matrix for a set of locations.

        Useful for optimizing visit order (traveling salesman problem).

        Args:
            locations: List of (lat, lon) tuples
            mode: Transport mode

        Returns:
            NxN matrix of travel times in minutes
        """
        profile: RouteProfile = mode  # type: ignore
        result = await self.client.get_table(
            coordinates=locations,
            profile=profile,
        )

        # Convert seconds to minutes
        durations_minutes = [
            [duration / 60 if duration is not None else float("inf") for duration in row]
            for row in result["durations"]
        ]

        return durations_minutes

    async def optimize_visit_order(
        self,
        pois: list[POI],
        start_location: tuple[float, float],
        mode: TransportMode = "walking",
    ) -> list[POI]:
        """
        Optimize the order to visit POIs (minimize total travel time).

        Uses nearest-neighbor heuristic for TSP (greedy algorithm).

        Args:
            pois: List of POIs to visit
            start_location: Starting point (e.g., hotel)
            mode: Transport mode

        Returns:
            Reordered list of POIs
        """
        if len(pois) <= 1:
            return pois

        # Build locations list: start + all POIs
        locations = [start_location] + [(poi.latitude, poi.longitude) for poi in pois]

        # Get distance matrix
        time_matrix = await self.get_distance_matrix(locations, mode)

        # Nearest neighbor heuristic
        unvisited = set(range(1, len(locations)))  # Skip index 0 (start location)
        current = 0  # Start from start_location
        route = []

        while unvisited:
            # Find nearest unvisited location
            nearest = min(unvisited, key=lambda i: time_matrix[current][i])
            route.append(nearest - 1)  # Convert back to POI index
            unvisited.remove(nearest)
            current = nearest

        # Return POIs in optimized order
        return [pois[i] for i in route]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.close()
