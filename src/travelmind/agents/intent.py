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
from datetime import date, datetime
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ..exceptions import (
    IntentParsingError,
    InvalidDateError,
    InvalidDurationError,
    MissingDestinationError,
)
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
            IntentParsingError: If LLM fails to parse the query
            InvalidDateError: If dates are invalid (past dates, end before start)
            InvalidDurationError: If duration is invalid (too short, too long)
            MissingDestinationError: If no destination is specified
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
            raise IntentParsingError(
                f"Failed to parse LLM response as JSON. This might be due to an unexpected "
                f"response format. Response: {response.content[:200]}..."
            )

        # Add the raw query
        parsed_data["raw_query"] = user_query

        # Validate the parsed data
        validated_data = self._validate_parsed_data(parsed_data)

        return validated_data

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

    def _validate_parsed_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate parsed data and apply constraints.

        Args:
            data: Parsed data from LLM

        Returns:
            Validated data with corrections applied

        Raises:
            MissingDestinationError: If no destination is provided
            InvalidDateError: If dates are invalid
            InvalidDurationError: If duration is invalid
        """
        # 1. Validate destinations
        if not data.get("destinations") or len(data.get("destinations", [])) == 0:
            raise MissingDestinationError(
                "No destination specified. Please specify where you want to travel."
            )

        # 2. Validate and parse dates
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        duration_days = data.get("duration_days")

        today = date.today()

        # Parse start_date if provided
        if start_date:
            try:
                if isinstance(start_date, str):
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                elif isinstance(start_date, date):
                    start_date_obj = start_date
                else:
                    raise ValueError("Invalid date type")

                # Check if start date is in the past
                if start_date_obj < today:
                    raise InvalidDateError(
                        f"Start date ({start_date}) is in the past. Please provide a future date."
                    )

                data["start_date"] = start_date_obj.strftime("%Y-%m-%d")
            except ValueError:
                raise InvalidDateError(
                    f"Invalid start date format: {start_date}. Expected YYYY-MM-DD."
                )

        # Parse end_date if provided
        if end_date:
            try:
                if isinstance(end_date, str):
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                elif isinstance(end_date, date):
                    end_date_obj = end_date
                else:
                    raise ValueError("Invalid date type")

                # Check if end date is in the past
                if end_date_obj < today:
                    raise InvalidDateError(
                        f"End date ({end_date}) is in the past. Please provide a future date."
                    )

                data["end_date"] = end_date_obj.strftime("%Y-%m-%d")
            except ValueError:
                raise InvalidDateError(
                    f"Invalid end date format: {end_date}. Expected YYYY-MM-DD."
                )

        # Validate start_date < end_date
        if start_date and end_date:
            start_obj = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end_obj = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

            if end_obj <= start_obj:
                raise InvalidDateError(
                    f"End date ({end_date}) must be after start date ({start_date})."
                )

            # Calculate duration from dates if not provided
            if not duration_days:
                duration_days = (end_obj - start_obj).days
                data["duration_days"] = duration_days

        # 3. Validate duration
        if duration_days:
            if not isinstance(duration_days, int):
                try:
                    duration_days = int(duration_days)
                    data["duration_days"] = duration_days
                except (ValueError, TypeError):
                    raise InvalidDurationError(
                        f"Invalid duration: {duration_days}. Must be a positive integer."
                    )

            # Check duration constraints
            if duration_days < 1:
                raise InvalidDurationError(
                    "Trip duration must be at least 1 day."
                )

            if duration_days > 14:
                raise InvalidDurationError(
                    f"Trip duration ({duration_days} days) exceeds maximum of 14 days. "
                    f"Weather forecast data is only available for up to 14 days in advance."
                )

        # 4. Validate mobility preference
        valid_mobility = ["walking", "driving", "cycling", "transit"]
        if data.get("mobility") and data["mobility"] not in valid_mobility:
            # Try to map to valid values
            mobility_lower = data["mobility"].lower()
            if mobility_lower in ["walk", "walkable"]:
                data["mobility"] = "walking"
            elif mobility_lower in ["drive", "car"]:
                data["mobility"] = "driving"
            elif mobility_lower in ["bike", "bicycle"]:
                data["mobility"] = "cycling"
            elif mobility_lower in ["public transport", "public_transport", "bus", "train"]:
                data["mobility"] = "transit"
            else:
                # Default to walking if unclear
                data["mobility"] = "walking"

        # 5. Validate pace
        valid_pace = ["relaxed", "moderate", "packed"]
        if data.get("pace") and data["pace"] not in valid_pace:
            # Default to moderate
            data["pace"] = "moderate"

        # 6. Validate budget_level
        valid_budget = ["budget", "moderate", "luxury"]
        if data.get("budget_level") and data["budget_level"] not in valid_budget:
            # Default to moderate
            data["budget_level"] = "moderate"

        return data
