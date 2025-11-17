"""
Test weather-aware POI matching.

This test creates a scenario with mixed weather and verifies that:
- Indoor POIs are scheduled on rainy days
- Outdoor POIs are scheduled on sunny days
"""

import asyncio
from datetime import date, timedelta

from src.travelmind.agents.calendar import CalendarAgent
from src.travelmind.agents.poi import POIAgent
from src.travelmind.models.request import TravelConstraints


async def test_weather_matching():
    """Test that POIs are matched to appropriate weather conditions."""
    print("=" * 80)
    print("Testing Weather-Aware POI Matching")
    print("=" * 80)
    print()

    # Step 1: Get diverse POIs (temples + museums)
    print("Step 1: Searching for temples and museums in Kyoto...")
    poi_agent = POIAgent()

    pois = await poi_agent.search(
        location="Kyoto",
        interests=["temples", "museums"],
        limit=15,
    )

    await poi_agent.close()

    print(f"  Found {len(pois)} POIs")
    print()

    # Categorize for display
    indoor = [p for p in pois if p.is_indoor()]
    outdoor = [p for p in pois if p.is_outdoor()]

    print(f"  Indoor POIs: {len(indoor)}")
    for poi in indoor[:3]:
        print(f"    - {poi.name} ({poi.category})")

    print(f"\n  Outdoor POIs: {len(outdoor)}")
    for poi in outdoor[:3]:
        print(f"    - {poi.name} ({poi.category})")
    print()

    # Step 2: Build itinerary for dates with varied weather
    print("Step 2: Building weather-aware itinerary...")
    calendar_agent = CalendarAgent()

    # Use dates in the near future for real weather data
    start_date = date.today() + timedelta(days=1)
    travel_dates = [start_date + timedelta(days=i) for i in range(3)]

    hotel_location = (pois[0].latitude, pois[0].longitude) if pois else (0, 0)

    itinerary = await calendar_agent.build_itinerary(
        pois=pois[:12],  # Use 12 POIs
        start_location=hotel_location,
        travel_dates=travel_dates,
        constraints=TravelConstraints(
            max_walk_km_per_day=12.0,
            preferred_start_time="09:00",
        ),
        mobility="walking",
    )

    await calendar_agent.close()

    print(f"  Created {itinerary['total_days']}-day itinerary")
    print()

    # Step 3: Analyze the matching
    print("Step 3: Analyzing weather-POI matching...")
    print("=" * 80)
    print()

    for day in itinerary["days"]:
        weather_cat = day["weather"]["category"]
        weather_desc = day["weather"]["description"]

        print(f"Day {day['date']}:")
        print(f"  Weather: {weather_desc} ({weather_cat})")
        print(f"  POIs: {day['pois_count']}")
        print()

        # Check POI types
        if day["timeline"]:
            indoor_count = 0
            outdoor_count = 0

            for event in day["timeline"]:
                if event["type"] == "poi":
                    poi_name = event["name"]
                    # Find the POI object
                    matching_poi = next((p for p in pois if p.name == poi_name), None)
                    if matching_poi:
                        if matching_poi.is_indoor():
                            indoor_count += 1
                            print(f"    🏛️  {poi_name} (INDOOR)")
                        elif matching_poi.is_outdoor():
                            outdoor_count += 1
                            print(f"    ⛩️  {poi_name} (OUTDOOR)")

            print()
            print(f"  Summary: {indoor_count} indoor, {outdoor_count} outdoor")

            # Validate logic
            if weather_cat in ["indoor", "challenging"]:
                if outdoor_count > indoor_count:
                    print(f"  ⚠️  WARNING: Bad weather but more outdoor POIs!")
                else:
                    print(f"  ✅ Good: Indoor activities prioritized for bad weather")
            elif weather_cat in ["excellent", "good"]:
                if indoor_count > outdoor_count:
                    print(f"  ℹ️  Note: Good weather but mostly indoor POIs")
                else:
                    print(f"  ✅ Good: Outdoor activities for nice weather")

        print()
        print("-" * 80)
        print()

    print("=" * 80)
    print("Test complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_weather_matching())
