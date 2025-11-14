"""
State definitions for LangGraph workflow.

This module defines the state schema that flows through the graph nodes.
"""

from datetime import date
from typing import Any, TypedDict

from ..models.poi import POI


class TravelPlanState(TypedDict, total=False):
    """
    State that flows through the LangGraph workflow.

    This state is passed between nodes and accumulates information
    as the workflow progresses.
    """

    # ===== User Input =====
    user_query: str
    """Original user travel query"""

    conversation_history: list[dict[str, str]]
    """History of user interactions for context"""

    # ===== Parsed Intent =====
    destination: str | None
    """Primary destination city/region"""

    destinations: list[str] | None
    """All destinations if multi-city trip"""

    start_date: str | None
    """Trip start date in YYYY-MM-DD format"""

    end_date: str | None
    """Trip end date in YYYY-MM-DD format"""

    travel_dates: list[date] | None
    """List of date objects for each day of trip"""

    duration_days: int | None
    """Trip duration in days"""

    interests: list[str] | None
    """User interests (temples, coffee, hiking, etc.)"""

    mobility: str
    """Preferred transportation mode (walking, driving, cycling, transit)"""

    pace: str | None
    """Trip pace (relaxed, moderate, packed)"""

    budget_level: str | None
    """Budget constraint (budget, moderate, luxury)"""

    must_see: list[str] | None
    """Specific POIs that must be included"""

    # ===== Agent Outputs =====
    pois: list[POI] | None
    """Discovered points of interest"""

    weather_data: dict[str, Any] | None
    """Weather forecast data"""

    itinerary: dict[str, Any] | None
    """Complete generated itinerary"""

    export_paths: dict[str, str] | None
    """Paths to exported files (json, markdown, ics)"""

    # ===== Control Flow =====
    needs_clarification: bool
    """Whether user input needs clarification"""

    clarification_questions: list[str]
    """Questions to ask user for missing information"""

    user_approved: bool
    """Whether user approved the generated itinerary"""

    user_feedback: str | None
    """User feedback on itinerary for adjustments"""

    # ===== Error Handling =====
    errors: list[str]
    """List of errors encountered during workflow"""

    retry_count: int
    """Number of retries for failed operations"""

    current_node: str | None
    """Current node being executed (for debugging)"""

    # ===== Workflow Status =====
    status: str
    """Overall workflow status (running, waiting_for_input, completed, failed)"""

    completed_steps: list[str]
    """List of successfully completed steps"""