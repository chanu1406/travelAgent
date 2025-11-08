"""
Test the Export Agent to generate different output formats.

Run with: python test_export.py
"""

import asyncio
from datetime import date, timedelta
from pathlib import Path

from src.travelmind.agents.calendar import CalendarAgent
from src.travelmind.agents.export import ExportAgent
from src.travelmind.models.poi import POI
from src.travelmind.models.request import TravelConstraints


async def test_export_agent():
    """Test the Export Agent's file generation capabilities."""
    print("=" * 70)
    print("Testing Export Agent - Multiple Output Formats")
    print("=" * 70)
    print()

    # First, create a sample itinerary using the Calendar Agent
    print("Step 1: Generating sample itinerary...")
    calendar_agent = CalendarAgent()

    hotel = (35.0116, 135.7681)  # Central Kyoto
    start_date = date.today() + timedelta(days=1)
    travel_dates = [start_date + timedelta(days=i) for i in range(2)]

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
            name="Nishiki Market",
            category="Market",
            latitude=35.0049,
            longitude=135.7653,
            estimated_visit_duration_minutes=60,
            address="Nishikikoji Street, Nakagyo Ward, Kyoto",
        ),
        POI(
            id="4",
            source="test",
            name="Gion District",
            category="Cultural",
            latitude=35.0037,
            longitude=135.7760,
            estimated_visit_duration_minutes=90,
            address="Gion, Higashiyama Ward, Kyoto",
        ),
    ]

    itinerary = await calendar_agent.build_itinerary(
        pois=pois,
        start_location=hotel,
        travel_dates=travel_dates,
        constraints=TravelConstraints(),
        mobility="walking",
    )

    print(f"✓ Created itinerary: {itinerary['total_days']} days, {itinerary['total_pois']} POIs")
    print()

    # Step 2: Export to different formats
    print("Step 2: Exporting to multiple formats...")
    export_agent = ExportAgent()
    output_dir = Path("output")
    trip_name = "Kyoto Cultural Tour"

    # Export to JSON
    print("  • Exporting to JSON...")
    json_path = export_agent.export(
        itinerary=itinerary,
        format="json",
        output_path=output_dir / "itinerary.json",
        trip_name=trip_name,
    )
    print(f"    ✓ Created: {json_path}")
    print(f"      Size: {json_path.stat().st_size} bytes")

    # Export to Markdown
    print("  • Exporting to Markdown...")
    md_path = export_agent.export(
        itinerary=itinerary,
        format="markdown",
        output_path=output_dir / "itinerary.md",
        trip_name=trip_name,
    )
    print(f"    ✓ Created: {md_path}")
    print(f"      Size: {md_path.stat().st_size} bytes")

    # Export to ICS Calendar
    print("  • Exporting to ICS (Calendar)...")
    ics_path = export_agent.export(
        itinerary=itinerary,
        format="ics",
        output_path=output_dir / "itinerary.ics",
        trip_name=trip_name,
    )
    print(f"    ✓ Created: {ics_path}")
    print(f"      Size: {ics_path.stat().st_size} bytes")

    print()

    # Step 3: Display preview of Markdown export
    print("=" * 70)
    print("MARKDOWN PREVIEW (First 50 lines)")
    print("=" * 70)
    print()

    md_content = md_path.read_text(encoding="utf-8")
    md_lines = md_content.split("\n")
    for line in md_lines[:50]:
        print(line)

    if len(md_lines) > 50:
        print(f"\n... ({len(md_lines) - 50} more lines)")

    print()
    print("=" * 70)
    print("FILES CREATED")
    print("=" * 70)
    print()
    print(f"📁 Output directory: {output_dir.absolute()}")
    print()
    print(f"📄 JSON:     {json_path.name}")
    print(f"   • Machine-readable complete itinerary data")
    print(f"   • Can be used for API integration or data analysis")
    print()
    print(f"📝 Markdown: {md_path.name}")
    print(f"   • Human-readable trip summary")
    print(f"   • Can be viewed in any text editor or converted to PDF")
    print()
    print(f"📅 Calendar: {ics_path.name}")
    print(f"   • Import into Google Calendar, Apple Calendar, Outlook")
    print(f"   • Each POI becomes a calendar event with location and time")
    print()

    await calendar_agent.close()
    print("✅ Export Agent test complete!")


if __name__ == "__main__":
    asyncio.run(test_export_agent())
