"""
Interactive LangGraph Workflow

An interactive CLI for the TravelMind LangGraph workflow.
Features:
- Real human-in-the-loop for clarifications
- Itinerary review and approval
- Conversation persistence
- Streaming progress updates

Run with: python interactive_langgraph.py
"""

import asyncio
from pathlib import Path

from src.travelmind.workflow.graph import create_workflow_with_persistence


async def get_user_input(prompt: str) -> str:
    """Get user input asynchronously."""
    return input(prompt)


async def run_interactive_workflow():
    """Run an interactive workflow session."""
    print("=" * 80)
    print("TravelMind Interactive Workflow")
    print("=" * 80)
    print()
    print("I'll help you plan your trip! Just tell me what you're looking for.")
    print("Type 'quit' to exit at any time.")
    print()

    # Create workflow with persistence
    db_path = "travelmind_sessions.db"
    app = create_workflow_with_persistence(db_path)

    # Generate a session ID (in real app, this would be user-specific)
    import uuid

    session_id = str(uuid.uuid4())[:8]
    config = {"configurable": {"thread_id": f"session-{session_id}"}}

    print(f"Session ID: {session_id}")
    print(f"Persistence: {db_path}")
    print()

    # Get user query
    query = await get_user_input("What trip would you like to plan? ")

    if query.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        return

    print()
    print("🚀 Starting workflow...")
    print()

    # Initial state
    initial_state = {
        "user_query": query,
        "conversation_history": [{"role": "user", "content": query}],
        "errors": [],
        "retry_count": 0,
        "completed_steps": [],
        "status": "running",
        "needs_clarification": False,
        "clarification_questions": [],
        "user_approved": False,  # Will ask user for real approval
        "mobility": "walking",
    }

    try:
        # Stream the workflow execution
        async for event in app.astream(initial_state, config):
            node_name = list(event.keys())[0]
            node_state = event[node_name]

            # Handle human-in-the-loop checkpoints
            if node_name == "ask_clarification":
                print("\n❓ I need some clarification:")
                questions = node_state.get("clarification_questions", [])

                for question in questions:
                    answer = await get_user_input(f"  {question}\n  > ")
                    # In a full implementation, we'd merge this answer back into the state
                    # and re-run parse_intent

                print("\nℹ️  Clarification collected. Workflow paused.")
                print("   (In full implementation, workflow would continue with updated info)")
                break

            elif node_name == "review_itinerary":
                print("\n" + "=" * 80)
                print("📋 ITINERARY PREVIEW")
                print("=" * 80)

                itinerary = node_state.get("itinerary", {})

                if itinerary:
                    print(f"\n📅 Trip Duration: {itinerary.get('total_days')} days")
                    print(f"📍 Total POIs: {itinerary.get('total_pois')}")
                    print(f"🗓️  Dates: {itinerary.get('start_date')} to {itinerary.get('end_date')}")

                    # Show day-by-day summary
                    days = itinerary.get("days", [])
                    for day in days:
                        print(f"\n  Day {day['date']}:")
                        print(f"    Weather: {day['weather']['description']} ({day['weather']['category']})")
                        print(f"    POIs: {day['pois_count']}")
                        print(f"    Walking: {day['total_walking_km']} km")

                print("\n" + "=" * 80)

                # Ask for approval
                approval = await get_user_input("\nDo you approve this itinerary? (yes/no): ")

                if approval.lower() in ["yes", "y"]:
                    # Update state to approve
                    node_state["user_approved"] = True
                    print("\n✅ Itinerary approved! Proceeding to export...")
                else:
                    print("\n❌ Itinerary not approved. Workflow will end.")
                    print("   (In full implementation, you could request changes)")
                    break

        # Get final state
        final_state = await app.aget_state(config)
        result = final_state.values if final_state else {}

        # Show final results
        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETE")
        print("=" * 80)

        print(f"\nStatus: {result.get('status', 'unknown')}")
        print(f"Completed steps: {', '.join(result.get('completed_steps', []))}")

        if result.get("export_paths"):
            print(f"\n📁 Generated files:")
            for format_name, path in result["export_paths"].items():
                print(f"  ✓ {format_name}: {path}")

            # Show preview of markdown
            md_path = result["export_paths"].get("markdown")
            if md_path and Path(md_path).exists():
                print(f"\n📄 Preview of {Path(md_path).name}:")
                print("-" * 80)
                content = Path(md_path).read_text(encoding="utf-8")
                lines = content.split("\n")[:30]
                for line in lines:
                    print(line)
                if len(content.split("\n")) > 30:
                    print(f"\n... ({len(content.split('\n')) - 30} more lines)")

        print("\n" + "=" * 80)
        print(f"Session saved! You can resume with session ID: {session_id}")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Workflow error: {str(e)}")
        import traceback

        traceback.print_exc()


async def main():
    """Main entry point."""
    try:
        await run_interactive_workflow()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\nError: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())