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

import json
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ..models.request import TravelRequest
from ..utils.config import settings


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

    def __init__(self, llm: BaseChatModel | None = None) -> None:
        """
        Initialize the intent agent with LLM configuration.

        Args:
            llm: Optional language model. If not provided, uses Anthropic Claude from config.
        """
        if llm is None:
            # Try Google Gemini first (free tier), then Anthropic, then OpenAI
            if settings.google_api_key:
                from langchain_google_genai import ChatGoogleGenerativeAI

                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=settings.google_api_key,
                    temperature=0,
                )
            elif settings.anthropic_api_key:
                from langchain_anthropic import ChatAnthropic

                self.llm = ChatAnthropic(
                    model="claude-3-5-haiku-20241022",
                    api_key=settings.anthropic_api_key,
                    temperature=0,
                )
            elif settings.openai_api_key:
                from langchain_openai import ChatOpenAI

                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.openai_api_key,
                    temperature=0,
                )
            else:
                raise ValueError(
                    "One of GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY must be set in .env"
                )
        else:
            self.llm = llm

    async def parse(self, user_query: str) -> dict[str, Any]:
        """
        Parse a natural language travel request.

        Args:
            user_query: Raw user input describing their trip

        Returns:
            Structured travel request parameters as a dictionary

        Raises:
            ValueError: If query is ambiguous or missing critical info
        """
        system_prompt = """You are a travel planning assistant that extracts structured information from natural language queries.

Extract the following information from the user's travel request:
- destinations: List of cities or regions (e.g., ["Tokyo", "Kyoto"])
- duration_days: Number of days for the trip (if mentioned)
- start_date: Trip start date in YYYY-MM-DD format (if mentioned)
- end_date: Trip end date in YYYY-MM-DD format (if mentioned)
- interests: List of user interests (e.g., ["temples", "coffee shops", "hiking"])
- mobility: Preferred mode of transportation ("walking", "driving", "cycling", "transit")
- pace: Trip pace ("relaxed", "moderate", "packed")
- budget_level: Budget constraint ("budget", "moderate", "luxury")
- must_see: Specific POIs that must be included
- avoid: Things to avoid
- dietary_restrictions: Any dietary restrictions

Return a JSON object with these fields. Only include fields that are explicitly mentioned or can be reasonably inferred.
If destinations are not mentioned, return null for destinations.
If neither duration_days nor dates are mentioned, return null for all date fields.

Example:
User: "4 days in Kyoto, love temples and coffee shops, prefer walking"
Response: {
    "destinations": ["Kyoto"],
    "duration_days": 4,
    "interests": ["temples", "coffee shops"],
    "mobility": "walking",
    "pace": "moderate"
}"""

        # Gemini doesn't support system messages, so we combine system prompt with user query
        combined_prompt = f"{system_prompt}\n\nUser query: {user_query}"
        messages = [
            HumanMessage(content=combined_prompt),
        ]

        response = await self.llm.ainvoke(messages)

        # Parse the JSON response
        try:
            # Extract JSON from response (handle markdown code blocks if present)
            content = response.content
            if "```json" in content:
                # Extract JSON from markdown code block
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                # Extract from generic code block
                content = content.split("```")[1].split("```")[0].strip()

            parsed_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response: {e}\nResponse content: {response.content}")

        # Add the raw query
        parsed_data["raw_query"] = user_query

        return parsed_data

    async def clarify(self, request: dict[str, Any]) -> list[str]:
        """
        Generate clarifying questions for incomplete requests.

        Args:
            request: Partially parsed travel request

        Returns:
            List of questions to ask the user
        """
        questions = []

        # Check for missing critical information
        if not request.get("destinations"):
            questions.append("Where would you like to go? (destination city or region)")

        if not request.get("duration_days") and not (
            request.get("start_date") and request.get("end_date")
        ):
            questions.append(
                "How long is your trip? (number of days or specific dates)"
            )

        return questions
