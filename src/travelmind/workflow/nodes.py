"""
LangGraph node functions.

Each node function takes the current state and returns an updated state.
Nodes wrap our existing agents to fit into the LangGraph workflow.
"""

from datetime import date, timedelta

from ..agents.calendar import CalendarAgent
from ..agents.export import ExportAgent
from ..agents.intent import IntentAgent
from ..agents.poi import POIAgent
from ..models.request import TravelConstraints
from .state import TravelPlanState


async def parse_intent_node(state: TravelPlanState) -> dict:
    """
    Parse user intent from natural language query.

    Extracts destination, dates, interests, and other parameters.
    Checks if additional clarification is needed.
    """
    print("\n🔍 Parsing travel request...")

    intent_agent = IntentAgent()

    try:
        parsed = await intent_agent.parse(state["user_query"])

        # Check if we need clarification
        questions = await intent_agent.clarify(parsed)

        # Extract parsed fields
        destinations = parsed.get("destinations", [])
        destination = destinations[0] if destinations else None

        # Generate travel dates if we have date info
        travel_dates = None
        start_date = parsed.get("start_date")
        end_date = parsed.get("end_date")
        duration_days = parsed.get("duration_days")

        if start_date and end_date:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            travel_dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        elif start_date and duration_days:
            start = date.fromisoformat(start_date)
            travel_dates = [start + timedelta(days=i) for i in range(duration_days)]
        elif duration_days:
            # Default to starting tomorrow
            start = date.today() + timedelta(days=1)
            travel_dates = [start + timedelta(days=i) for i in range(duration_days)]

        print(f"  ✓ Destination: {destination or 'Not specified'}")
        print(f"  ✓ Dates: {start_date or 'Not specified'} to {end_date or 'Not specified'}")
        print(f"  ✓ Interests: {', '.join(parsed.get('interests', [])) or 'None specified'}")

        completed_steps = state.get("completed_steps", [])
        completed_steps.append("parse_intent")

        return {
            "destination": destination,
            "destinations": destinations,
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration_days,
            "travel_dates": travel_dates,
            "interests": parsed.get("interests"),
            "mobility": parsed.get("mobility", "walking"),
            "pace": parsed.get("pace"),
            "budget_level": parsed.get("budget_level"),
            "must_see": parsed.get("must_see"),
            "needs_clarification": len(questions) > 0,
            "clarification_questions": questions,
            "errors": [],
            "current_node": "parse_intent",
            "completed_steps": completed_steps,
            "status": "running",
        }

    except Exception as e:
        print(f"  ✗ Error parsing intent: {str(e)}")
        return {
            "errors": [f"Intent parsing failed: {str(e)}"],
            "retry_count": state.get("retry_count", 0) + 1,
            "current_node": "parse_intent",
            "status": "failed",
        }


async def ask_clarification_node(state: TravelPlanState) -> dict:
    """
    Ask user for clarification on missing information.

    This is a human-in-the-loop node that pauses execution.
    """
    print("\n❓ Need clarification from user...")

    questions = state.get("clarification_questions", [])

    for i, question in enumerate(questions, 1):
        print(f"  {i}. {question}")

    # In a real application, this would wait for user input
    # For now, we'll just mark that we need clarification
    return {
        "status": "waiting_for_input",
        "current_node": "ask_clarification",
    }


async def discover_pois_node(state: TravelPlanState) -> dict:
    """
    Discover points of interest based on user preferences.

    Uses POI Agent to search for relevant attractions.
    """
    print("\n📍 Discovering points of interest...")

    poi_agent = POIAgent()

    try:
        destination = state.get("destination")
        interests = state.get("interests") or ["tourism", "culture"]

        if not destination:
            raise ValueError("No destination specified")

        pois = await poi_agent.search(
            location=destination,
            interests=interests,
            limit=12,
        )

        await poi_agent.close()

        print(f"  ✓ Found {len(pois)} POIs")
        for i, poi in enumerate(pois[:3], 1):
            print(f"    {i}. {poi.name} ({poi.category})")
        if len(pois) > 3:
            print(f"    ... and {len(pois) - 3} more")

        completed_steps = state.get("completed_steps", [])
        completed_steps.append("discover_pois")

        return {
            "pois": pois,
            "errors": [],
            "current_node": "discover_pois",
            "completed_steps": completed_steps,
        }

    except Exception as e:
        print(f"  ✗ Error discovering POIs: {str(e)}")
        await poi_agent.close()

        return {
            "errors": state.get("errors", []) + [f"POI discovery failed: {str(e)}"],
            "retry_count": state.get("retry_count", 0) + 1,
            "current_node": "discover_pois",
        }


async def build_itinerary_node(state: TravelPlanState) -> dict:
    """
    Build complete itinerary with weather, routes, and scheduling.

    This node combines Weather Agent, Route Agent, and Calendar Agent.
    """
    print("\n📅 Building optimized itinerary...")

    calendar_agent = CalendarAgent()

    try:
        pois = state.get("pois", [])
        travel_dates = state.get("travel_dates", [])
        mobility = state.get("mobility", "walking")

        if not pois:
            raise ValueError("No POIs available")

        if not travel_dates:
            # Default to 3 days starting tomorrow
            travel_dates = [date.today() + timedelta(days=i) for i in range(1, 4)]

        # Use first POI location as start location
        start_location = (pois[0].latitude, pois[0].longitude)

        # Build itinerary (this internally uses weather and route agents)
        itinerary = await calendar_agent.build_itinerary(
            pois=pois[:8],  # Limit to 8 POIs for reasonable daily schedules
            start_location=start_location,
            travel_dates=travel_dates,
            constraints=TravelConstraints(
                max_walk_km_per_day=15.0,
                preferred_start_time="09:00",
            ),
            mobility=mobility,
        )

        await calendar_agent.close()

        print(f"  ✓ Created {itinerary['total_days']}-day itinerary")
        print(f"  ✓ Total POIs: {itinerary['total_pois']}")

        completed_steps = state.get("completed_steps", [])
        completed_steps.append("build_itinerary")

        return {
            "itinerary": itinerary,
            "errors": [],
            "current_node": "build_itinerary",
            "completed_steps": completed_steps,
        }

    except Exception as e:
        print(f"  ✗ Error building itinerary: {str(e)}")
        await calendar_agent.close()

        return {
            "errors": state.get("errors", []) + [f"Itinerary building failed: {str(e)}"],
            "retry_count": state.get("retry_count", 0) + 1,
            "current_node": "build_itinerary",
        }


async def review_itinerary_node(state: TravelPlanState) -> dict:
    """
    Present itinerary to user for review and approval.

    This is a human-in-the-loop node that waits for user feedback.
    """
    print("\n👀 Review itinerary...")

    itinerary = state.get("itinerary", {})

    # Show summary
    print(f"\n  Trip Summary:")
    print(f"  - Duration: {itinerary.get('total_days')} days")
    print(f"  - POIs: {itinerary.get('total_pois')}")
    print(f"  - Dates: {itinerary.get('start_date')} to {itinerary.get('end_date')}")

    print("\n  Do you approve this itinerary? (yes/no/modify)")

    # In a real application, wait for user input
    # For demo purposes, auto-approve
    return {
        "user_approved": True,  # Would come from user input
        "status": "waiting_for_input",
        "current_node": "review_itinerary",
    }


async def export_itinerary_node(state: TravelPlanState) -> dict:
    """
    Export itinerary to multiple formats (JSON, Markdown, ICS).

    Saves files to output directory.
    """
    print("\n💾 Exporting itinerary...")

    export_agent = ExportAgent()

    try:
        itinerary = state.get("itinerary")
        destination = state.get("destination", "Unknown")

        if not itinerary:
            raise ValueError("No itinerary to export")

        from pathlib import Path

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        trip_name = f"Trip to {destination}"

        # Export to all formats
        json_path = export_agent.export(
            itinerary=itinerary,
            format="json",
            output_path=output_dir / "trip.json",
            trip_name=trip_name,
        )

        md_path = export_agent.export(
            itinerary=itinerary,
            format="markdown",
            output_path=output_dir / "trip.md",
            trip_name=trip_name,
        )

        ics_path = export_agent.export(
            itinerary=itinerary,
            format="ics",
            output_path=output_dir / "trip.ics",
            trip_name=trip_name,
        )

        print(f"  ✓ JSON: {json_path.name}")
        print(f"  ✓ Markdown: {md_path.name}")
        print(f"  ✓ Calendar: {ics_path.name}")

        completed_steps = state.get("completed_steps", [])
        completed_steps.append("export_itinerary")

        return {
            "export_paths": {
                "json": str(json_path),
                "markdown": str(md_path),
                "ics": str(ics_path),
            },
            "errors": [],
            "current_node": "export_itinerary",
            "completed_steps": completed_steps,
            "status": "completed",
        }

    except Exception as e:
        print(f"  ✗ Error exporting itinerary: {str(e)}")

        return {
            "errors": state.get("errors", []) + [f"Export failed: {str(e)}"],
            "retry_count": state.get("retry_count", 0) + 1,
            "current_node": "export_itinerary",
            "status": "failed",
        }