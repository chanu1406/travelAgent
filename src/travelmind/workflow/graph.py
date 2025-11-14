"""
LangGraph workflow definition.

This module defines the complete workflow graph with nodes, edges,
and conditional routing logic.
"""

from langgraph.graph import END, StateGraph

from .nodes import (
    ask_clarification_node,
    build_itinerary_node,
    discover_pois_node,
    export_itinerary_node,
    parse_intent_node,
    review_itinerary_node,
)
from .state import TravelPlanState


def should_ask_clarification(state: TravelPlanState) -> str:
    """
    Determine if we need to ask user for clarification.

    Returns:
        "clarify" if clarification needed, "continue" otherwise
    """
    if state.get("needs_clarification", False):
        return "clarify"
    return "continue"


def should_retry_or_continue(state: TravelPlanState) -> str:
    """
    Determine if we should retry a failed operation or fail permanently.

    Returns:
        "retry" if we should retry (< 3 attempts)
        "fail" if we should give up
        "continue" if no errors
    """
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0)

    if errors and retry_count < 3:
        return "retry"
    elif errors:
        return "fail"
    return "continue"


def should_export(state: TravelPlanState) -> str:
    """
    Determine if user approved itinerary for export.

    Returns:
        "export" if approved
        "revise" if user wants changes
    """
    if state.get("user_approved", False):
        return "export"
    return "revise"


def create_workflow() -> StateGraph:
    """
    Create the complete TravelMind workflow graph.

    The workflow follows this structure:
    1. Parse intent
    2. Check if clarification needed → ask or continue
    3. Discover POIs
    4. Build itinerary (includes weather and routing)
    5. Review with user → export or revise
    6. Export to multiple formats

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph
    workflow = StateGraph(TravelPlanState)

    # Add nodes
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("ask_clarification", ask_clarification_node)
    workflow.add_node("discover_pois", discover_pois_node)
    workflow.add_node("build_itinerary", build_itinerary_node)
    workflow.add_node("review_itinerary", review_itinerary_node)
    workflow.add_node("export_itinerary", export_itinerary_node)

    # Set entry point
    workflow.set_entry_point("parse_intent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "parse_intent",
        should_ask_clarification,
        {
            "clarify": "ask_clarification",
            "continue": "discover_pois",
        },
    )

    # After clarification, go back to parse intent with updated info
    # (In real implementation, this would merge user answers into query)
    workflow.add_edge("ask_clarification", END)  # For now, end if clarification needed

    # Linear flow: POIs → Itinerary → Review → Export
    workflow.add_edge("discover_pois", "build_itinerary")
    workflow.add_edge("build_itinerary", "review_itinerary")

    # Conditional: approved → export, not approved → end (would revise in full impl)
    workflow.add_conditional_edges(
        "review_itinerary",
        should_export,
        {
            "export": "export_itinerary",
            "revise": END,  # For now, end if not approved
        },
    )

    # Export is final step
    workflow.add_edge("export_itinerary", END)

    # Compile the graph
    return workflow.compile()


def create_workflow_with_persistence(db_path: str = "travelmind.db") -> StateGraph:
    """
    Create workflow with SQLite persistence for resumable conversations.

    Args:
        db_path: Path to SQLite database for checkpointing

    Returns:
        Compiled StateGraph with persistence
    """
    from langgraph.checkpoint.sqlite import SqliteSaver

    workflow = StateGraph(TravelPlanState)

    # Add all nodes (same as above)
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("ask_clarification", ask_clarification_node)
    workflow.add_node("discover_pois", discover_pois_node)
    workflow.add_node("build_itinerary", build_itinerary_node)
    workflow.add_node("review_itinerary", review_itinerary_node)
    workflow.add_node("export_itinerary", export_itinerary_node)

    workflow.set_entry_point("parse_intent")

    # Add edges
    workflow.add_conditional_edges(
        "parse_intent",
        should_ask_clarification,
        {
            "clarify": "ask_clarification",
            "continue": "discover_pois",
        },
    )

    workflow.add_edge("ask_clarification", END)
    workflow.add_edge("discover_pois", "build_itinerary")
    workflow.add_edge("build_itinerary", "review_itinerary")

    workflow.add_conditional_edges(
        "review_itinerary",
        should_export,
        {
            "export": "export_itinerary",
            "revise": END,
        },
    )

    workflow.add_edge("export_itinerary", END)

    # Add persistence
    memory = SqliteSaver.from_conn_string(db_path)

    return workflow.compile(checkpointer=memory)