"""
Visualize the LangGraph workflow structure.

This script generates a visual representation of the TravelMind workflow graph.

Run with: python visualize_graph.py
"""

from src.travelmind.workflow.graph import create_workflow


def print_graph_structure():
    """Print a text-based representation of the graph structure."""
    print("=" * 80)
    print("TravelMind LangGraph Workflow Structure")
    print("=" * 80)
    print()

    print("Nodes:")
    print("  1. parse_intent        - Parse natural language query")
    print("  2. ask_clarification   - Ask user for missing information (HITL)")
    print("  3. discover_pois       - Find relevant points of interest")
    print("  4. build_itinerary     - Create optimized schedule with weather & routes")
    print("  5. review_itinerary    - Present to user for approval (HITL)")
    print("  6. export_itinerary    - Export to JSON, Markdown, ICS")
    print()

    print("Flow:")
    print()
    print("  START")
    print("    ↓")
    print("  parse_intent")
    print("    ↓")
    print("  [needs_clarification?]")
    print("    ├─ YES → ask_clarification → END (wait for user input)")
    print("    └─ NO  → discover_pois")
    print("              ↓")
    print("            build_itinerary")
    print("              ↓")
    print("            review_itinerary")
    print("              ↓")
    print("            [user_approved?]")
    print("              ├─ YES → export_itinerary → END")
    print("              └─ NO  → END (would revise in full impl)")
    print()

    print("Human-in-the-Loop Points:")
    print("  • ask_clarification  - Collects missing info from user")
    print("  • review_itinerary   - Gets user approval before export")
    print()

    print("State Management:")
    print("  • Stateful workflow with TypedDict state schema")
    print("  • Optional SQLite persistence for resumable conversations")
    print("  • Error tracking with retry logic")
    print("  • Completed steps tracking for debugging")
    print()

    print("Key Features:")
    print("  ✅ Conditional routing based on data completeness")
    print("  ✅ Error handling with configurable retries")
    print("  ✅ Human-in-the-loop for clarification & approval")
    print("  ✅ Conversation persistence across sessions")
    print("  ✅ Streaming execution with progress updates")
    print()


def export_graph_image():
    """
    Export graph visualization to PNG (requires graphviz).

    Note: This requires graphviz to be installed:
        pip install pygraphviz  (or)
        brew install graphviz && pip install pygraphviz
    """
    try:
        from langchain_core.runnables.graph import MermaidDrawMethod

        app = create_workflow()

        # Get mermaid representation
        mermaid = app.get_graph().draw_mermaid()

        print("Mermaid Diagram:")
        print("=" * 80)
        print(mermaid)
        print("=" * 80)
        print()
        print("Copy the above Mermaid code to https://mermaid.live/ to visualize")
        print()

        # Try to render PNG
        try:
            png_data = app.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API,
            )

            output_path = "workflow_graph.png"
            with open(output_path, "wb") as f:
                f.write(png_data)

            print(f"✅ Graph exported to: {output_path}")

        except Exception as e:
            print(f"ℹ️  Could not export PNG: {e}")
            print("   (Mermaid diagram printed above - use https://mermaid.live/)")

    except ImportError:
        print("ℹ️  Install pygraphviz for graph visualization:")
        print("   brew install graphviz && pip install pygraphviz")


def main():
    """Main entry point."""
    print_graph_structure()

    print("=" * 80)
    print("Generating visual diagram...")
    print("=" * 80)
    print()

    export_graph_image()


if __name__ == "__main__":
    main()