"""
Export Agent

Responsible for converting finalized itineraries into various output formats.

Supported formats:
1. JSON (.json): Machine-readable complete itinerary data
2. Markdown (.md): Human-readable trip summary with day-by-day breakdown
3. ICS Calendar (.ics): Import into Google Calendar, Apple Calendar, etc.

Each export format includes:
- All POI details (name, address, coords, times)
- Route information (walking directions, distances)
- Weather notes
- User notes/preferences

The agent uses templates and standard libraries (no external dependencies)
to ensure exports are clean and compatible with common tools.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal


ExportFormat = Literal["json", "markdown", "ics"]


class ExportAgent:
    """
    Exports itineraries to multiple file formats.

    Supports:
    - JSON: Complete structured data
    - Markdown: Human-readable trip plans
    - ICS: Calendar events for each POI
    """

    def __init__(self) -> None:
        """Initialize export agent."""
        pass

    def export(
        self,
        itinerary: dict[str, Any],
        format: ExportFormat,
        output_path: str | Path,
        trip_name: str = "My Trip",
    ) -> Path:
        """
        Export itinerary to specified format.

        Args:
            itinerary: Complete itinerary data structure
            format: Output format (json, markdown, ics)
            output_path: Where to save the file
            trip_name: Name of the trip for headers

        Returns:
            Path to the created file
        """
        output_path = Path(output_path)

        # Generate content based on format
        if format == "json":
            content = self.to_json(itinerary)
        elif format == "markdown":
            content = self.to_markdown(itinerary, trip_name)
        elif format == "ics":
            content = self.to_ics(itinerary, trip_name)
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def to_json(self, itinerary: dict[str, Any]) -> str:
        """
        Generate JSON export of complete itinerary.

        Args:
            itinerary: Itinerary data

        Returns:
            JSON string
        """
        return json.dumps(itinerary, indent=2, ensure_ascii=False)

    def to_markdown(self, itinerary: dict[str, Any], trip_name: str = "My Trip") -> str:
        """
        Generate markdown-formatted itinerary.

        Args:
            itinerary: Itinerary data
            trip_name: Name of the trip

        Returns:
            Markdown formatted string
        """
        lines = []

        # Header
        lines.append(f"# {trip_name}")
        lines.append("")
        lines.append(f"**Dates:** {itinerary['trip_dates'][0]} to {itinerary['trip_dates'][-1]}")
        lines.append(f"**Duration:** {itinerary['total_days']} days")
        lines.append(f"**Total POIs:** {itinerary['total_pois']}")
        lines.append("")

        # Calculate total walking
        total_walking = sum(day["total_walking_km"] for day in itinerary["days"])
        lines.append(f"**Total Walking Distance:** {total_walking:.2f} km")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Day-by-day breakdown
        for day_idx, day in enumerate(itinerary["days"], 1):
            lines.append(f"## Day {day_idx}: {day['date']}")
            lines.append("")

            # Weather and stats
            lines.append(f"**Weather:** {day['weather']['description']} ({day['weather']['category']})")
            lines.append(f"**POIs:** {day['pois_count']}")
            lines.append(f"**Walking:** {day['total_walking_km']} km")
            lines.append(f"**Time:** {day['start_time']} - {day['end_time']}")
            lines.append("")

            # Timeline
            lines.append("### Timeline")
            lines.append("")

            for event in day["timeline"]:
                time = event["time"]
                event_type = event["type"]

                if event_type == "start":
                    lines.append(f"**{time}** - 🏨 {event['location']}")
                elif event_type == "travel":
                    mode_emoji = {"walking": "🚶", "driving": "🚗", "cycling": "🚴"}.get(
                        event["mode"], "🚶"
                    )
                    lines.append(
                        f"**{time}** - {mode_emoji} Travel {event['distance_km']} km "
                        f"({event['duration_minutes']} min)"
                    )
                elif event_type == "poi":
                    lines.append(f"**{time}** - 📍 **{event['name']}**")
                    lines.append(f"  - Category: {event['category']}")
                    lines.append(f"  - Duration: {event['duration_minutes']} minutes")
                    if event.get("address"):
                        lines.append(f"  - Address: {event['address']}")
                    if event.get("coordinates"):
                        coords = event["coordinates"]
                        lines.append(f"  - Coordinates: {coords['lat']:.4f}, {coords['lon']:.4f}")
                elif event_type == "end":
                    lines.append(f"**{time}** - 🏨 {event['location']}")

                lines.append("")

            lines.append("---")
            lines.append("")

        # Footer
        lines.append("## Trip Summary")
        lines.append("")
        lines.append(f"- **Total Days:** {itinerary['total_days']}")
        lines.append(f"- **Total POIs:** {itinerary['total_pois']}")
        lines.append(f"- **Total Walking:** {total_walking:.2f} km")
        lines.append(f"- **Average per Day:** {total_walking/itinerary['total_days']:.2f} km")
        lines.append("")
        lines.append("*Generated by TravelMind AI Trip Planner*")

        return "\n".join(lines)

    def to_ics(self, itinerary: dict[str, Any], trip_name: str = "My Trip") -> str:
        """
        Generate ICS calendar file.

        Args:
            itinerary: Itinerary data
            trip_name: Name of the trip

        Returns:
            ICS formatted string
        """
        lines = []

        # ICS header
        lines.append("BEGIN:VCALENDAR")
        lines.append("VERSION:2.0")
        lines.append("PRODID:-//TravelMind//Trip Planner//EN")
        lines.append(f"X-WR-CALNAME:{trip_name}")
        lines.append("X-WR-TIMEZONE:UTC")
        lines.append("CALSCALE:GREGORIAN")
        lines.append("METHOD:PUBLISH")

        # Create events for each POI
        for day in itinerary["days"]:
            date_str = day["date"]

            for event in day["timeline"]:
                if event["type"] == "poi":
                    # Parse date and time
                    date_parts = date_str.split("-")
                    time_parts = event["time"].split(":")

                    # Create datetime for start
                    start_dt = datetime(
                        int(date_parts[0]),
                        int(date_parts[1]),
                        int(date_parts[2]),
                        int(time_parts[0]),
                        int(time_parts[1]),
                    )

                    # Calculate end time
                    from datetime import timedelta

                    end_dt = start_dt + timedelta(minutes=event["duration_minutes"])

                    # Format for ICS (YYYYMMDDTHHMMSS)
                    dtstart = start_dt.strftime("%Y%m%dT%H%M%S")
                    dtend = end_dt.strftime("%Y%m%dT%H%M%S")

                    # Create unique ID
                    uid = f"{dtstart}-{event['name'].replace(' ', '-')}@travelmind"

                    # Build event
                    lines.append("BEGIN:VEVENT")
                    lines.append(f"UID:{uid}")
                    lines.append(f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}")
                    lines.append(f"DTSTART:{dtstart}")
                    lines.append(f"DTEND:{dtend}")
                    lines.append(f"SUMMARY:{event['name']}")

                    # Add location if available
                    if event.get("address"):
                        # Escape commas and newlines in ICS format
                        address = event["address"].replace(",", "\\,").replace("\n", "\\n")
                        lines.append(f"LOCATION:{address}")

                    # Add description
                    description_parts = [
                        f"Category: {event['category']}",
                        f"Duration: {event['duration_minutes']} minutes",
                    ]
                    if event.get("coordinates"):
                        coords = event["coordinates"]
                        description_parts.append(
                            f"Coordinates: {coords['lat']:.4f}, {coords['lon']:.4f}"
                        )

                    description = "\\n".join(description_parts)
                    lines.append(f"DESCRIPTION:{description}")

                    lines.append("STATUS:CONFIRMED")
                    lines.append("SEQUENCE:0")
                    lines.append("END:VEVENT")

        # ICS footer
        lines.append("END:VCALENDAR")

        return "\n".join(lines)
