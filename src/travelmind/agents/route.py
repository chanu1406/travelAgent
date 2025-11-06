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
        pass

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
            Route data with distance, duration, and geometry
        """
        raise NotImplementedError("Route calculation to be implemented")

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
        raise NotImplementedError("Distance matrix calculation to be implemented")

    def optimize_visit_order(
        self,
        pois: list[dict[str, Any]],
        start_location: tuple[float, float],
        mode: TransportMode = "walking",
    ) -> list[dict[str, Any]]:
        """
        Optimize the order to visit POIs (minimize total travel time).

        Uses nearest-neighbor or 2-opt heuristic for TSP.

        Args:
            pois: List of POIs to visit
            start_location: Starting point (e.g., hotel)
            mode: Transport mode

        Returns:
            Reordered list of POIs
        """
        raise NotImplementedError("Route optimization to be implemented")
