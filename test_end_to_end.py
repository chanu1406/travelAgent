"""
End-to-end test of the TravelAgent system.

This test demonstrates the full workflow:
1. User provides natural language query
2. Intent Agent parses the query
3. POI Agent finds relevant attractions
4. Routing service calculates distances
5. Weather service fetches forecasts

Run with: python test_end_to_end.py
"""

import asyncio
from datetime import date, timedelta

from src.travelmind.agents.intent import IntentAgent
from src.travelmind.agents.poi import POIAgent
from src.travelmind.services.openmeteo import OpenMeteoClient
from src.travelmind.services.routing import OSRMClient


async def test_full_workflow():
    """Test the complete travel planning workflow."""
    print("=" * 70)
    print("TravelAgent End-to-End Test")
    print("=" * 70)
    print()

    # Step 1: Parse user query
    print("STEP 1: Parse Natural Language Query")
    print("-" * 70)

    user_query = "Plan 4 days in Kyoto, love temples and coffee shops, prefer walking"
    print(f"User Query: '{user_query}'")
    print()

    intent_agent = IntentAgent()
    parsed_request = await intent_agent.parse(user_query)

    print("Parsed Request:")
    print(f"  Destinations: {parsed_request.get('destinations')}")
    print(f"  Duration: {parsed_request.get('duration_days')} days")
    print(f"  Interests: {parsed_request.get('interests')}")
    print(f"  Mobility: {parsed_request.get('mobility')}")
    print(f"  Pace: {parsed_request.get('pace')}")
    print()

    # Step 2: Find POIs
    print("STEP 2: Discover Points of Interest")
    print("-" * 70)

    poi_agent = POIAgent()
    destination = parsed_request['destinations'][0]
    interests = parsed_request.get('interests', [])

    print(f"Searching for POIs in {destination}...")
    print(f"Interests: {interests}")
    print()

    pois = await poi_agent.search(
        location=destination,
        interests=interests,
        radius_km=5.0,
        limit=10,
    )

    print(f"Found {len(pois)} POIs:")
    for i, poi in enumerate(pois[:10], 1):
        print(f"  {i}. {poi.name}")
        print(f"     Category: {poi.category}")
        print(f"     Location: {poi.latitude:.4f}, {poi.longitude:.4f}")
        print(f"     Visit time: ~{poi.estimated_visit_duration_minutes} minutes")
        if poi.address:
            print(f"     Address: {poi.address}")
        print()

    # Step 3: Calculate routes between top POIs
    print("STEP 3: Calculate Routes Between POIs")
    print("-" * 70)

    if len(pois) >= 3:
        top_pois = pois[:3]
        print(f"Calculating distances between top 3 POIs...")
        print()

        osrm_client = OSRMClient()
        coordinates = [(poi.latitude, poi.longitude) for poi in top_pois]

        # Get distance matrix
        matrix = await osrm_client.get_table(
            coordinates=coordinates,
            profile="walking",
        )

        print("Walking distances and times:")
        for i, poi_from in enumerate(top_pois):
            for j, poi_to in enumerate(top_pois):
                if i != j:
                    distance_km = matrix['distances'][i][j] / 1000
                    duration_min = matrix['durations'][i][j] / 60
                    print(f"  {poi_from.name} → {poi_to.name}")
                    print(f"    {distance_km:.2f} km, {duration_min:.0f} minutes walk")
        print()

        # Get detailed route for first pair
        if len(top_pois) >= 2:
            route = await osrm_client.get_route(
                coordinates=[
                    (top_pois[0].latitude, top_pois[0].longitude),
                    (top_pois[1].latitude, top_pois[1].longitude),
                ],
                profile="walking",
            )
            print(f"Detailed route: {top_pois[0].name} → {top_pois[1].name}")
            print(f"  Distance: {route['distance']/1000:.2f} km")
            print(f"  Duration: {route['duration']/60:.1f} minutes")
            print(f"  Route geometry: {len(route['geometry']['coordinates'])} waypoints")
            print()

        await osrm_client.close()

    # Step 4: Get weather forecast
    print("STEP 4: Fetch Weather Forecast")
    print("-" * 70)

    if pois:
        # Use first POI's coordinates for weather
        lat, lon = pois[0].latitude, pois[0].longitude

        # Get forecast for next 4 days
        start = date.today()
        end = start + timedelta(days=3)

        print(f"Getting weather forecast for {destination}...")
        print(f"Dates: {start} to {end}")
        print()

        weather_client = OpenMeteoClient()
        forecast = await weather_client.get_forecast(
            latitude=lat,
            longitude=lon,
            start_date=start,
            end_date=end,
            timezone="auto",
        )

        print("Daily forecast:")
        for day in forecast['daily'][:4]:
            print(f"  {day['date']}")
            print(f"    {day['weather_description']}")
            print(f"    Temperature: {day['temperature_min_celsius']}°C - {day['temperature_max_celsius']}°C")
            print(f"    Precipitation: {day['precipitation_sum_mm']} mm")
        print()

        await weather_client.close()

    # Step 5: Summary
    print("STEP 5: Trip Summary")
    print("-" * 70)
    print(f"Destination: {destination}")
    print(f"Duration: {parsed_request.get('duration_days')} days")
    print(f"Travel mode: {parsed_request.get('mobility', 'walking')}")
    print(f"Total POIs found: {len(pois)}")
    if pois:
        print(f"Sample itinerary for Day 1:")
        for i, poi in enumerate(pois[:4], 1):
            print(f"  {i}. Visit {poi.name} (~{poi.estimated_visit_duration_minutes} min)")
    print()

    await poi_agent.close()

    print("=" * 70)
    print("✅ End-to-End Test Complete!")
    print("=" * 70)
    print()
    print("Next steps to complete the platform:")
    print("  • Implement Weather Agent wrapper")
    print("  • Implement Route Agent wrapper")
    print("  • Implement Calendar Agent for intelligent itinerary building")
    print("  • Implement Export Agent for PDF/JSON/iCal output")
    print("  • Wire up LangGraph workflow for multi-agent orchestration")


if __name__ == "__main__":
    asyncio.run(test_full_workflow())
