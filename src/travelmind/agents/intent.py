"""
Intent Agent

Responsible for parsing natural language travel requests into structured parameters.

This agent uses an LLM to understand user intent and extract:
- Destination cities/regions
- Travel dates (or duration)
- Budget constraints
- Interests and preferences (e.g., "coffee shops", "temples", "hiking")
- Mobility preferences (walkable, driving, public transit)
- Accommodation type (if specified)
- Dietary restrictions
- Any specific must-see locations

The agent validates extracted parameters and requests clarification if needed.

Example transformations:
    Input: "Plan 4 days in Kyoto, mostly walkable, love coffee shops and temples"
    Output: TravelRequest(
        destinations=["Kyoto"],
        duration_days=4,
        interests=["coffee shops", "temples"],
        mobility="walking",
        ...
    )
"""

from typing import Any


class IntentAgent:
    """
    Parses user natural language queries into structured travel requests.

    Uses LLM-based natural language understanding to extract:
    - Destinations
    - Dates/duration
    - Interests
    - Budget
    - Mobility preferences
    """

    def __init__(self) -> None:
        """Initialize the intent agent with LLM configuration."""
        pass

    async def parse(self, user_query: str) -> dict[str, Any]:
        """
        Parse a natural language travel request.

        Args:
            user_query: Raw user input describing their trip

        Returns:
            Structured travel request parameters

        Raises:
            ValueError: If query is ambiguous or missing critical info
        """
        raise NotImplementedError("Intent parsing logic to be implemented")

    async def clarify(self, request: dict[str, Any]) -> list[str]:
        """
        Generate clarifying questions for incomplete requests.

        Args:
            request: Partially parsed travel request

        Returns:
            List of questions to ask the user
        """
        raise NotImplementedError("Clarification logic to be implemented")
