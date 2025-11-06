"""
LangGraph Workflow Orchestration

Defines the multi-agent workflow using LangGraph.

Workflow:
1. User Query → Intent Agent (parse request)
2. Intent → [POI Agent + Weather Agent + Route Agent] (parallel data gathering)
3. All data → Calendar Agent (build itinerary)
4. Calendar → HITL Checkpoint (optional human review)
5. HITL → Calendar Agent (apply edits if needed)
6. Final itinerary → Export Agent (generate outputs)

State management:
- Graph state tracks data flow between agents
- Each agent reads from and writes to shared state
- Conditional edges for HITL and error handling
"""

from typing import Any, TypedDict

from langgraph.graph import StateGraph


class TravelPlanningState(TypedDict, total=False):
    """
    Shared state for the travel planning workflow.

    Each agent reads inputs from and writes outputs to this state.
    """

    # User input
    user_query: str
    raw_input: dict[str, Any]

    # Intent parsing
    travel_request: dict[str, Any]
    constraints: dict[str, Any]
    clarifications_needed: list[str]

    # Data gathering
    pois: list[dict[str, Any]]
    weather_forecast: dict[str, Any]
    distance_matrix: list[list[float]]

    # Itinerary building
    itinerary: dict[str, Any]
    warnings: list[str]

    # Human-in-the-loop
    hitl_approved: bool
    hitl_edits: dict[str, Any]

    # Export
    export_formats: list[str]
    output_files: dict[str, str]

    # Error handling
    errors: list[str]


def create_travel_planning_graph() -> StateGraph:
    """
    Create the LangGraph workflow for travel planning.

    Returns:
        Configured StateGraph ready for compilation
    """
    workflow = StateGraph(TravelPlanningState)

    # Add nodes (agent functions)
    workflow.add_node("intent_agent", intent_node)
    workflow.add_node("poi_agent", poi_node)
    workflow.add_node("weather_agent", weather_node)
    workflow.add_node("route_agent", route_node)
    workflow.add_node("calendar_agent", calendar_node)
    workflow.add_node("hitl_checkpoint", hitl_node)
    workflow.add_node("export_agent", export_node)

    # Define edges (workflow transitions)
    workflow.set_entry_point("intent_agent")

    # After intent, check if clarifications needed
    workflow.add_conditional_edges(
        "intent_agent",
        should_clarify,
        {
            "clarify": "__end__",  # Exit to get user clarification
            "continue": "poi_agent",
        },
    )

    # Parallel data gathering (POI, Weather, Route)
    # In practice, these would fan out and fan in
    workflow.add_edge("poi_agent", "weather_agent")
    workflow.add_edge("weather_agent", "route_agent")
    workflow.add_edge("route_agent", "calendar_agent")

    # After calendar, go to HITL checkpoint
    workflow.add_edge("calendar_agent", "hitl_checkpoint")

    # HITL decision: approve or edit
    workflow.add_conditional_edges(
        "hitl_checkpoint",
        should_finalize,
        {
            "edit": "calendar_agent",  # Loop back for adjustments
            "approve": "export_agent",
        },
    )

    # Export is terminal
    workflow.add_edge("export_agent", "__end__")

    return workflow


# Node functions (placeholders - actual implementations will use agent classes)


async def intent_node(state: TravelPlanningState) -> dict[str, Any]:
    """
    Intent Agent node: Parse user query.

    Reads: user_query
    Writes: travel_request, constraints, clarifications_needed
    """
    raise NotImplementedError("Intent node to be implemented")


async def poi_node(state: TravelPlanningState) -> dict[str, Any]:
    """
    POI Agent node: Search for attractions.

    Reads: travel_request
    Writes: pois
    """
    raise NotImplementedError("POI node to be implemented")


async def weather_node(state: TravelPlanningState) -> dict[str, Any]:
    """
    Weather Agent node: Fetch forecasts.

    Reads: travel_request
    Writes: weather_forecast
    """
    raise NotImplementedError("Weather node to be implemented")


async def route_node(state: TravelPlanningState) -> dict[str, Any]:
    """
    Route Agent node: Calculate travel times.

    Reads: pois
    Writes: distance_matrix
    """
    raise NotImplementedError("Route node to be implemented")


async def calendar_node(state: TravelPlanningState) -> dict[str, Any]:
    """
    Calendar Agent node: Build itinerary.

    Reads: pois, weather_forecast, distance_matrix, constraints
    Writes: itinerary, warnings
    """
    raise NotImplementedError("Calendar node to be implemented")


async def hitl_node(state: TravelPlanningState) -> dict[str, Any]:
    """
    Human-in-the-loop checkpoint.

    Presents itinerary to user for review.
    Reads: itinerary
    Writes: hitl_approved, hitl_edits
    """
    raise NotImplementedError("HITL node to be implemented")


async def export_node(state: TravelPlanningState) -> dict[str, Any]:
    """
    Export Agent node: Generate output files.

    Reads: itinerary, export_formats
    Writes: output_files
    """
    raise NotImplementedError("Export node to be implemented")


# Conditional edge functions


def should_clarify(state: TravelPlanningState) -> str:
    """
    Decide if clarifications are needed before proceeding.

    Returns:
        "clarify" if questions needed, "continue" otherwise
    """
    if state.get("clarifications_needed"):
        return "clarify"
    return "continue"


def should_finalize(state: TravelPlanningState) -> str:
    """
    Decide if itinerary should be finalized or edited.

    Returns:
        "approve" to proceed to export, "edit" to revise itinerary
    """
    if state.get("hitl_approved"):
        return "approve"
    return "edit"


# Main execution function


async def plan_trip(
    user_query: str,
    export_formats: list[str] | None = None,
) -> dict[str, Any]:
    """
    Execute the full travel planning workflow.

    Args:
        user_query: Natural language travel request
        export_formats: Output formats (default: ["markdown"])

    Returns:
        Final state with itinerary and output files
    """
    graph = create_travel_planning_graph()
    app = graph.compile()

    initial_state: TravelPlanningState = {
        "user_query": user_query,
        "export_formats": export_formats or ["markdown"],
        "hitl_approved": False,  # Default: require review
        "errors": [],
    }

    # Run the graph
    final_state = await app.ainvoke(initial_state)
    return final_state
