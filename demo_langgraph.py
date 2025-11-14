"""
LangGraph Workflow Demo

Demonstrates the stateful LangGraph workflow for TravelMind.
Shows how the workflow handles:
- Intent parsing
- Conditional routing
- Error handling
- Human-in-the-loop review
- Multi-format export

Run with: python demo_langgraph.py
"""

import asyncio

from src.travelmind.workflow.graph import create_workflow


async def run_workflow_demo(query: str) -> None:
    """
    Run the LangGraph workflow with a travel query.

    Args:
        query: Natural language travel request
    """
    print("=" * 80)
    print("TravelMind LangGraph Workflow Demo")
    print("=" * 80)
    print(f"\nQuery: {query}\n")

    # Create workflow
    app = create_workflow()

    # Initial state
    initial_state = {
        "user_query": query,
        "conversation_history": [],
        "errors": [],
        "retry_count": 0,
        "completed_steps": [],
        "status": "running",
        "needs_clarification": False,
        "clarification_questions": [],
        "user_approved": True,  # Auto-approve for demo
        "mobility": "walking",
    }

    # Run workflow
    print("🚀 Starting workflow...\n")

    try:
        # Execute the graph
        result = await app.ainvoke(initial_state)

        print("\n" + "=" * 80)
        print("WORKFLOW RESULTS")
        print("=" * 80)

        # Show final state
        print(f"\nStatus: {result.get('status', 'unknown')}")
        print(f"Completed steps: {', '.join(result.get('completed_steps', []))}")

        if result.get("errors"):
            print(f"\nErrors encountered:")
            for error in result["errors"]:
                print(f"  - {error}")

        if result.get("export_paths"):
            print(f"\nGenerated files:")
            for format_name, path in result["export_paths"].items():
                print(f"  - {format_name}: {path}")

        if result.get("itinerary"):
            itinerary = result["itinerary"]
            print(f"\nItinerary summary:")
            print(f"  - Duration: {itinerary.get('total_days')} days")
            print(f"  - POIs: {itinerary.get('total_pois')}")
            print(f"  - Dates: {itinerary.get('start_date')} to {itinerary.get('end_date')}")

        print("\n" + "=" * 80)
        print("✅ Workflow completed successfully!")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ Workflow failed: {str(e)}")
        print("=" * 80)
        raise


async def run_multiple_scenarios():
    """Run the workflow with different test scenarios."""

    scenarios = [
        {
            "name": "Complete Query",
            "query": "I want to visit Kyoto temples for 3 days starting November 10, 2025",
        },
        {
            "name": "Query with Interests",
            "query": "Plan 4 days in Tokyo, love coffee shops and museums",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n\n{'=' * 80}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'=' * 80}\n")

        await run_workflow_demo(scenario["query"])

        if i < len(scenarios):
            print("\n\nPress Enter to continue to next scenario...")
            # input()  # Uncomment for interactive mode


async def main():
    """Run the demo."""
    # Run single scenario
    await run_workflow_demo(
        "I want to visit Kyoto temples and cultural sites for 3 days starting November 10, 2025"
    )

    # Optionally run multiple scenarios
    # await run_multiple_scenarios()


if __name__ == "__main__":
    asyncio.run(main())