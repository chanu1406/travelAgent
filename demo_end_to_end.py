"""
Comprehensive End-to-End TravelMind Demo

This demo shows the complete workflow:
1. Parse natural language travel query
2. Discover POIs matching interests
3. Fetch weather forecasts
4. Optimize routes and build itinerary
5. Export to multiple formats

Run with: python demo_end_to_end.py
"""

import asyncio
from datetime import date, timedelta
from pathlib import Path

from src.travelmind.agents.calendar import CalendarAgent
from src.travelmind.agents.export import ExportAgent
from src.travelmind.agents.intent import IntentAgent
from src.travelmind.agents.poi import POIAgent
from src.travelmind.models.request import TravelConstraints


async def run_complete_workflow(query: str) -> None:
    """
    Run the complete TravelMind workflow from query to exported itinerary.

    Args:
        query: Natural language travel request
    """
    print("=" * 80)
    print("TravelMind AI Trip Planner - End-to-End Demo")
    print("=" * 80)
    print()
    print(f"Query: {query}")
    print()

    # Step 1: Parse Intent
    print("STEP 1: Parsing travel request...")
    print("-" * 80)
    intent_agent = IntentAgent()

    parsed_intent = await intent_agent.parse(query)

    # Extract and display parsed information
    destinations = parsed_intent.get("destinations", [])
    destination = destinations[0] if destinations else "Unknown"
    start_date = parsed_intent.get("start_date", "Not specified")
    end_date = parsed_intent.get("end_date", "Not specified")
    interests = parsed_intent.get("interests", [])
    mobility = parsed_intent.get("mobility", "walking")

    print(f"  Destination: {destination}")
    print(f"  Dates: {start_date} to {end_date}")
    print(f"  Interests: {', '.join(interests) if interests else 'General'}")
    print(f"  Mobility: {mobility}")
    print()

    # Step 2: Discover POIs
    print("STEP 2: Discovering points of interest...")
    print("-" * 80)
    poi_agent = POIAgent()

    pois = await poi_agent.search(
        location=destination,
        interests=interests if interests else ["tourism", "culture"],
        limit=12,
    )

    print(f"  Found {len(pois)} POIs:")
    for i, poi in enumerate(pois[:6], 1):  # Show first 6
        print(f"    {i}. {poi.name} ({poi.category})")
    if len(pois) > 6:
        print(f"    ... and {len(pois) - 6} more")
    print()

    # Step 3: Build Itinerary
    print("STEP 3: Building optimized itinerary...")
    print("-" * 80)
    calendar_agent = CalendarAgent()

    # Use first POI location as approximate hotel location
    hotel_location = (pois[0].latitude, pois[0].longitude) if pois else (0, 0)

    # Generate travel dates
    if parsed_intent.get("start_date") and parsed_intent.get("end_date"):
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        travel_dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    elif parsed_intent.get("duration_days"):
        # Use dates from query if available, otherwise use future dates
        start = date.fromisoformat(start_date) if start_date != "Not specified" else date.today() + timedelta(days=1)
        travel_dates = [start + timedelta(days=i) for i in range(parsed_intent["duration_days"])]
    else:
        # Default to 3 days starting tomorrow
        travel_dates = [date.today() + timedelta(days=i) for i in range(1, 4)]

    itinerary = await calendar_agent.build_itinerary(
        pois=pois[:8],  # Use first 8 POIs
        start_location=hotel_location,
        travel_dates=travel_dates,
        constraints=TravelConstraints(
            max_walk_km_per_day=15.0,
            preferred_start_time="09:00",
        ),
        mobility=mobility,
    )

    print(f"  Total Days: {itinerary['total_days']}")
    print(f"  Total POIs: {itinerary['total_pois']}")
    print()

    for day in itinerary["days"]:
        print(f"  Day {day['date']}:")
        print(f"    Weather: {day['weather']['description']} ({day['weather']['category']})")
        print(f"    POIs: {day['pois_count']}")
        print(f"    Walking: {day['total_walking_km']} km")
        print(f"    Time: {day['start_time']} - {day['end_time']}")
        print()

    # Step 4: Export to Multiple Formats
    print("STEP 4: Exporting itinerary...")
    print("-" * 80)
    export_agent = ExportAgent()
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    trip_name = f"Trip to {destination}"

    # Export to JSON
    json_path = export_agent.export(
        itinerary=itinerary,
        format="json",
        output_path=output_dir / "trip.json",
        trip_name=trip_name,
    )
    print(f"  JSON: {json_path.name} ({json_path.stat().st_size:,} bytes)")

    # Export to Markdown
    md_path = export_agent.export(
        itinerary=itinerary,
        format="markdown",
        output_path=output_dir / "trip.md",
        trip_name=trip_name,
    )
    print(f"  Markdown: {md_path.name} ({md_path.stat().st_size:,} bytes)")

    # Export to ICS Calendar
    ics_path = export_agent.export(
        itinerary=itinerary,
        format="ics",
        output_path=output_dir / "trip.ics",
        trip_name=trip_name,
    )
    print(f"  Calendar: {ics_path.name} ({ics_path.stat().st_size:,} bytes)")
    print()

    # Step 5: Show Preview
    print("=" * 80)
    print("MARKDOWN PREVIEW")
    print("=" * 80)
    print()

    md_content = md_path.read_text(encoding="utf-8")
    md_lines = md_content.split("\n")
    for line in md_lines[:40]:  # Show first 40 lines
        print(line)

    if len(md_lines) > 40:
        print(f"\n... ({len(md_lines) - 40} more lines)")

    print()
    print("=" * 80)
    print("WORKFLOW COMPLETE!")
    print("=" * 80)
    print()
    print(f"All files saved to: {output_dir.absolute()}")
    print()
    print("What was accomplished:")
    print("  1. Parsed natural language query using Google Gemini 2.0 Flash")
    print("  2. Discovered POIs using Geoapify API")
    print("  3. Fetched weather forecasts from Open-Meteo")
    print("  4. Optimized routes using OSRM")
    print("  5. Built day-by-day itinerary with realistic timings")
    print("  6. Exported to JSON, Markdown, and ICS calendar formats")
    print()

    # Cleanup
    await poi_agent.close()
    await calendar_agent.close()


async def main():
    """Run demo with sample queries."""

    # Demo Query 1: Kyoto temples
    await run_complete_workflow(
        "I want to visit Kyoto temples and cultural sites for 3 days starting November 10, 2025"
    )

    print("\n" + "=" * 80)
    print("Try your own query by running: python interactive_intent.py")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
