"""
Calendar Agent

Responsible for building day-by-day itineraries from POI, weather, and route data.

The Calendar Agent is the "brain" that combines all inputs:
- POIs from POI Agent
- Weather forecasts from Weather Agent
- Travel times from Route Agent
- User constraints (mobility, pace, interests)

Scheduling logic:
1. Assign POIs to days based on:
   - Geographic clustering (minimize daily travel)
   - Weather appropriateness (outdoor vs indoor)
   - Opening hours
   - User energy levels (heavy activities early, light later)
2. Optimize visit order within each day
3. Add buffer time for meals, rest, unexpected delays
4. Respect constraints:
   - Max walking distance per day
   - Preferred pace (relaxed, moderate, packed)
   - Must-see items get priority

Output: A structured itinerary with:
- Day-by-day breakdown
- Time slots for each POI
- Walking/transport between locations
- Meal suggestions
- Free time blocks
"""

from datetime import date, datetime, timedelta
from typing import Any

from ..exceptions import InsufficientPOIsError, ItineraryBuildError
from ..models.poi import POI
from ..models.request import TravelConstraints
from .route import RouteAgent
from .weather import WeatherAgent


class CalendarAgent:
    """
    Builds optimized day-by-day itineraries.

    Coordinates data from other agents to create realistic,
    enjoyable daily plans that respect user preferences and constraints.
    """

    def __init__(self) -> None:
        """Initialize calendar agent with other agents."""
        self.route_agent = RouteAgent()
        self.weather_agent = WeatherAgent()

    async def build_itinerary(
        self,
        pois: list[POI],
        start_location: tuple[float, float],
        travel_dates: list[date],
        constraints: TravelConstraints | None = None,
        mobility: str = "walking",
    ) -> dict[str, Any]:
        """
        Create a complete itinerary from available data.

        Args:
            pois: List of POIs to schedule
            start_location: Hotel/accommodation coordinates (lat, lon)
            travel_dates: List of dates in the trip
            constraints: User preferences (max_walk_km, pace, etc.)
            mobility: Transport mode (walking, driving, cycling)

        Returns:
            Complete itinerary with day-by-day schedules

        Raises:
            ItineraryBuildError: If itinerary building fails due to invalid inputs
            InsufficientPOIsError: If there are not enough POIs for the trip length
        """
        # Validate inputs
        if not travel_dates or len(travel_dates) == 0:
            raise ItineraryBuildError("No travel dates provided")

        if len(travel_dates) > 14:
            raise ItineraryBuildError(
                f"Trip length ({len(travel_dates)} days) exceeds maximum of 14 days"
            )

        if not pois or len(pois) == 0:
            raise InsufficientPOIsError(
                "No POIs provided. Cannot build itinerary without destinations."
            )

        if constraints is None:
            constraints = TravelConstraints()

        n_days = len(travel_dates)

        # Validate POI count vs trip length
        # Rule of thumb: need at least 2-3 POIs per day for a good itinerary
        min_pois_needed = max(n_days * 2, 3)  # At least 3 POIs total
        if len(pois) < min_pois_needed:
            raise InsufficientPOIsError(
                f"Not enough POIs for a {n_days}-day trip. Found {len(pois)} POIs, "
                f"but need at least {min_pois_needed} for a quality itinerary. "
                f"Try expanding your interests or search radius."
            )

        # Step 1: Get weather forecast FIRST (needed for smart POI assignment)
        if pois:
            lat, lon = pois[0].latitude, pois[0].longitude
            weather_data = await self.weather_agent.get_forecast(
                latitude=lat,
                longitude=lon,
                start_date=travel_dates[0],
                end_date=travel_dates[-1],
            )
        else:
            weather_data = {"daily": [], "hourly": []}

        # Step 2: Cluster POIs by day WITH weather awareness
        poi_clusters = self._cluster_pois_by_weather(
            pois=pois,
            n_days=n_days,
            weather_data=weather_data.get("daily", []),
        )

        # Step 3: Build daily schedules
        daily_schedules = []
        for day_idx, day_date in enumerate(travel_dates):
            day_pois = poi_clusters[day_idx] if day_idx < len(poi_clusters) else []

            # Get weather for this day
            day_weather = None
            if day_idx < len(weather_data.get("daily", [])):
                day_weather = weather_data["daily"][day_idx]

            # Optimize POI order for this day
            if day_pois:
                optimized_pois = await self.route_agent.optimize_visit_order(
                    pois=day_pois,
                    start_location=start_location,
                    mode=mobility,  # type: ignore
                )
            else:
                optimized_pois = []

            # Schedule the day
            day_schedule = await self._schedule_day(
                day_date=day_date,
                pois=optimized_pois,
                start_location=start_location,
                day_weather=day_weather,
                constraints=constraints,
                mobility=mobility,
            )

            daily_schedules.append(day_schedule)

        return {
            "trip_dates": [str(d) for d in travel_dates],
            "days": daily_schedules,
            "total_days": n_days,
            "total_pois": len(pois),
        }

    def _cluster_by_day(
        self,
        pois: list[POI],
        n_days: int,
    ) -> list[list[POI]]:
        """
        Assign POIs to days using simple round-robin distribution.

        Future: Could use k-means clustering based on coordinates.

        Args:
            pois: List of POIs to distribute
            n_days: Number of days in the trip

        Returns:
            List of POI lists, one per day
        """
        if not pois or n_days <= 0:
            return []

        # Simple distribution: divide POIs evenly across days
        pois_per_day = len(pois) // n_days
        remainder = len(pois) % n_days

        clusters = []
        start_idx = 0

        for day in range(n_days):
            # Give extra POI to early days if there's a remainder
            day_size = pois_per_day + (1 if day < remainder else 0)
            end_idx = start_idx + day_size

            clusters.append(pois[start_idx:end_idx])
            start_idx = end_idx

        return clusters

    def _cluster_pois_by_weather(
        self,
        pois: list[POI],
        n_days: int,
        weather_data: list[dict[str, Any]],
    ) -> list[list[POI]]:
        """
        Assign POIs to days based on weather appropriateness.

        Strategy:
        - Bad weather days → indoor POIs (museums, cafes)
        - Good weather days → outdoor POIs (temples, parks)
        - Mix when possible to balance the itinerary

        Args:
            pois: List of POIs to distribute
            n_days: Number of days in the trip
            weather_data: Daily weather forecasts

        Returns:
            List of POI lists, one per day, matched to weather
        """
        if not pois or n_days <= 0:
            return []

        # Categorize POIs by weather suitability
        indoor_pois = [poi for poi in pois if poi.is_indoor()]
        outdoor_pois = [poi for poi in pois if poi.is_outdoor()]
        flexible_pois = [poi for poi in pois if not poi.is_indoor() and not poi.is_outdoor()]

        # Categorize days by weather quality
        good_weather_days = []
        bad_weather_days = []
        moderate_weather_days = []

        for day_idx in range(n_days):
            if day_idx < len(weather_data):
                day_weather = weather_data[day_idx]
                category = day_weather.get("category", "good")

                if category in ["excellent", "good"]:
                    good_weather_days.append(day_idx)
                elif category in ["indoor", "challenging"]:
                    bad_weather_days.append(day_idx)
                else:
                    moderate_weather_days.append(day_idx)
            else:
                # No weather data, assume moderate
                moderate_weather_days.append(day_idx)

        # Initialize clusters
        clusters: list[list[POI]] = [[] for _ in range(n_days)]

        # Distribute indoor POIs to bad weather days
        for i, poi in enumerate(indoor_pois):
            if bad_weather_days:
                day_idx = bad_weather_days[i % len(bad_weather_days)]
            else:
                # No bad weather days, distribute evenly
                day_idx = i % n_days
            clusters[day_idx].append(poi)

        # Distribute outdoor POIs to good weather days
        for i, poi in enumerate(outdoor_pois):
            if good_weather_days:
                day_idx = good_weather_days[i % len(good_weather_days)]
            else:
                # No specifically good days, use moderate or any available
                day_idx = (moderate_weather_days + list(range(n_days)))[i % n_days]
            clusters[day_idx].append(poi)

        # Distribute flexible POIs to balance days
        for i, poi in enumerate(flexible_pois):
            # Find the day with fewest POIs
            min_day = min(range(n_days), key=lambda d: len(clusters[d]))
            clusters[min_day].append(poi)

        # Balance pass: ensure no day has 0 POIs if others have many
        max_pois_per_day = max(len(cluster) for cluster in clusters) if clusters else 0
        if max_pois_per_day > 3:
            # Move POIs from overloaded days to empty days
            for day_idx in range(n_days):
                if len(clusters[day_idx]) == 0:
                    # Find a day with extra POIs
                    donor_day = max(range(n_days), key=lambda d: len(clusters[d]))
                    if len(clusters[donor_day]) > 1:
                        # Move one POI
                        poi = clusters[donor_day].pop()
                        clusters[day_idx].append(poi)

        return clusters

    async def _schedule_day(
        self,
        day_date: date,
        pois: list[POI],
        start_location: tuple[float, float],
        day_weather: dict[str, Any] | None,
        constraints: TravelConstraints,
        mobility: str,
    ) -> dict[str, Any]:
        """
        Create a timed schedule for a single day.

        Args:
            day_date: Date for this day
            pois: POIs to visit this day (already optimized order)
            start_location: Starting coordinates
            day_weather: Weather forecast for the day
            constraints: User constraints
            mobility: Transport mode

        Returns:
            Day schedule with timeline
        """
        # Parse start time
        start_hour, start_minute = map(int, constraints.preferred_start_time.split(":"))
        current_time = datetime.combine(day_date, datetime.min.time()).replace(
            hour=start_hour, minute=start_minute
        )

        timeline = []
        current_location = start_location

        # Add starting point
        timeline.append({
            "time": current_time.strftime("%H:%M"),
            "type": "start",
            "location": "Accommodation",
            "notes": "Start of day",
        })

        total_walking_km = 0.0

        # Schedule each POI
        for poi in pois:
            poi_location = (poi.latitude, poi.longitude)

            # Calculate travel time to this POI
            route = await self.route_agent.get_route(
                origin=current_location,
                destination=poi_location,
                mode=mobility,  # type: ignore
            )

            travel_minutes = route["duration"] / 60
            travel_km = route["distance"] / 1000
            total_walking_km += travel_km

            # Add travel segment
            current_time += timedelta(minutes=travel_minutes)
            timeline.append({
                "time": current_time.strftime("%H:%M"),
                "type": "travel",
                "mode": mobility,
                "duration_minutes": int(travel_minutes),
                "distance_km": round(travel_km, 2),
            })

            # Add POI visit
            current_time += timedelta(minutes=poi.estimated_visit_duration_minutes)
            timeline.append({
                "time": current_time.strftime("%H:%M"),
                "type": "poi",
                "name": poi.name,
                "category": poi.category,
                "duration_minutes": poi.estimated_visit_duration_minutes,
                "address": poi.address,
                "coordinates": {"lat": poi.latitude, "lon": poi.longitude},
            })

            current_location = poi_location

        # Return to accommodation
        if pois:
            route = await self.route_agent.get_route(
                origin=current_location,
                destination=start_location,
                mode=mobility,  # type: ignore
            )
            travel_minutes = route["duration"] / 60
            travel_km = route["distance"] / 1000
            total_walking_km += travel_km

            current_time += timedelta(minutes=travel_minutes)
            timeline.append({
                "time": current_time.strftime("%H:%M"),
                "type": "travel",
                "mode": mobility,
                "duration_minutes": int(travel_minutes),
                "distance_km": round(travel_km, 2),
            })

        timeline.append({
            "time": current_time.strftime("%H:%M"),
            "type": "end",
            "location": "Accommodation",
            "notes": "End of day",
        })

        # Build day summary
        weather_summary = "Unknown"
        weather_category = "unknown"
        if day_weather:
            weather_summary = day_weather.get("weather_description", "Unknown")
            weather_category = self.weather_agent.categorize_day(day_weather)

        return {
            "date": str(day_date),
            "weather": {
                "description": weather_summary,
                "category": weather_category,
            },
            "pois_count": len(pois),
            "total_walking_km": round(total_walking_km, 2),
            "start_time": timeline[0]["time"],
            "end_time": timeline[-1]["time"],
            "timeline": timeline,
        }

    async def close(self) -> None:
        """Close all sub-agents."""
        await self.route_agent.close()
        await self.weather_agent.close()
