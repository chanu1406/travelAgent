"""
Test the Calendar Agent for complete itinerary generation.

Run with: python test_calendar_agent.py
"""

import asyncio
from datetime import date, timedelta

from src.travelmind.agents.calendar import CalendarAgent
from src.travelmind.models.poi import POI
from src.travelmind.models.request import TravelConstraints


async def test_calendar_agent():
    """Test the Calendar Agent's itinerary building capabilities."""
    print("=" * 70)
    print("Testing Calendar Agent - Complete Itinerary Generation")
    print("=" * 70)
    print()

    # Create a Calendar Agent
    agent = CalendarAgent()

    # Hotel location in central Kyoto
    hotel = (35.0116, 135.7681)

    # Travel dates (starting tomorrow for next 3 days)
    start_date = date.today() + timedelta(days=1)
    travel_dates = [start_date + timedelta(days=i) for i in range(3)]

    print(f"Trip: {travel_dates[0]} to {travel_dates[-1]}")
    print(f"Hotel: {hotel}")
    print()

    # Sample POIs in Kyoto
    pois = [
        POI(
            id="1",
            source="test",
            name="Fushimi Inari Shrine",
            category="Temple",
            latitude=34.9671,
            longitude=135.7727,
            estimated_visit_duration_minutes=90,
            address="Fushimi Inari Taisha, Kyoto",
        ),
        POI(
            id="2",
            source="test",
            name="Kinkaku-ji (Golden Pavilion)",
            category="Temple",
            latitude=35.0394,
            longitude=135.7292,
            estimated_visit_duration_minutes=60,
            address="1 Kinkakujicho, Kita Ward, Kyoto",
        ),
        POI(
            id="3",
            source="test",
            name="Kiyomizu-dera",
            category="Temple",
            latitude=34.9949,
            longitude=135.7850,
            estimated_visit_duration_minutes=75,
            address="1-294 Kiyomizu, Higashiyama Ward, Kyoto",
        ),
        POI(
            id="4",
            source="test",
            name="Arashiyama Bamboo Grove",
            category="Nature",
            latitude=35.0172,
            longitude=135.6719,
            estimated_visit_duration_minutes=45,
            address="Arashiyama, Ukyo Ward, Kyoto",
        ),
        POI(
            id="5",
            source="test",
            name="Nishiki Market",
            category="Market",
            latitude=35.0049,
            longitude=135.7653,
            estimated_visit_duration_minutes=60,
            address="Nishikikoji Street, Nakagyo Ward, Kyoto",
        ),
        POI(
            id="6",
            source="test",
            name="Gion District",
            category="Cultural",
            latitude=35.0037,
            longitude=135.7760,
            estimated_visit_duration_minutes=90,
            address="Gion, Higashiyama Ward, Kyoto",
        ),
    ]

    print(f"POIs to schedule: {len(pois)}")
    for poi in pois:
        print(f"  • {poi.name} ({poi.estimated_visit_duration_minutes} min)")
    print()

    # User constraints
    constraints = TravelConstraints(
        max_walk_km_per_day=15.0,
        max_pois_per_day=3,
        preferred_start_time="09:00",
        preferred_end_time="18:00",
    )

    print("Building itinerary...")
    print()

    # Build the itinerary
    itinerary = await agent.build_itinerary(
        pois=pois,
        start_location=hotel,
        travel_dates=travel_dates,
        constraints=constraints,
        mobility="walking",
    )

    # Display the itinerary
    print("=" * 70)
    print(f"ITINERARY: {itinerary['total_days']} Days, {itinerary['total_pois']} POIs")
    print("=" * 70)
    print()

    for day_idx, day in enumerate(itinerary["days"], 1):
        print(f"DAY {day_idx}: {day['date']}")
        print("-" * 70)
        print(f"Weather: {day['weather']['description']} ({day['weather']['category']})")
        print(f"POIs: {day['pois_count']}")
        print(f"Walking: {day['total_walking_km']} km")
        print(f"Time: {day['start_time']} - {day['end_time']}")
        print()

        print("Timeline:")
        for event in day["timeline"]:
            time = event["time"]
            event_type = event["type"]

            if event_type == "start":
                print(f"  {time} - 🏨 {event['location']}")
            elif event_type == "travel":
                mode_emoji = {"walking": "🚶", "driving": "🚗", "cycling": "🚴"}.get(
                    event["mode"], "🚶"
                )
                print(
                    f"  {time} - {mode_emoji} Travel: {event['distance_km']} km ({event['duration_minutes']} min)"
                )
            elif event_type == "poi":
                print(f"  {time} - 📍 {event['name']}")
                print(f"         {event['category']} - {event['duration_minutes']} min")
                if event.get("address"):
                    print(f"         {event['address']}")
            elif event_type == "end":
                print(f"  {time} - 🏨 {event['location']}")

        print()

    # Summary statistics
    total_walking = sum(day["total_walking_km"] for day in itinerary["days"])
    total_pois = sum(day["pois_count"] for day in itinerary["days"])

    print("=" * 70)
    print("TRIP SUMMARY")
    print("=" * 70)
    print(f"Total Days: {itinerary['total_days']}")
    print(f"Total POIs Visited: {total_pois}/{len(pois)}")
    print(f"Total Walking Distance: {total_walking:.2f} km")
    print(f"Average Walking per Day: {total_walking/itinerary['total_days']:.2f} km")
    print()

    await agent.close()
    print("✅ Calendar Agent test complete!")


if __name__ == "__main__":
    asyncio.run(test_calendar_agent())
