"""
Tests for Intent Agent

Tests natural language understanding and parameter extraction.
"""

import pytest

from travelmind.agents.intent import IntentAgent


class TestIntentAgent:
    """Tests for the Intent Agent."""

    @pytest.mark.asyncio
    async def test_parse_simple_query(self):
        """Test parsing a straightforward travel query."""
        agent = IntentAgent()
        query = "Plan 4 days in Kyoto, mostly walkable, love coffee shops and temples"

        # To be implemented
        with pytest.raises(NotImplementedError):
            result = await agent.parse(query)

        # Expected behavior (once implemented):
        # assert result["destinations"] == ["Kyoto"]
        # assert result["duration_days"] == 4
        # assert "coffee shops" in result["interests"]
        # assert "temples" in result["interests"]
        # assert result["mobility"] == "walking"

    @pytest.mark.asyncio
    async def test_parse_multi_city_query(self):
        """Test parsing query with multiple destinations."""
        agent = IntentAgent()
        query = "2 weeks in Tokyo and Kyoto"

        with pytest.raises(NotImplementedError):
            result = await agent.parse(query)

        # Expected:
        # assert result["destinations"] == ["Tokyo", "Kyoto"]
        # assert result["duration_days"] == 14

    @pytest.mark.asyncio
    async def test_parse_date_range_query(self):
        """Test parsing query with explicit dates."""
        agent = IntentAgent()
        query = "Visit Paris from November 10 to November 15"

        with pytest.raises(NotImplementedError):
            result = await agent.parse(query)

        # Expected:
        # assert result["start_date"] is not None
        # assert result["end_date"] is not None

    @pytest.mark.asyncio
    async def test_clarification_needed(self):
        """Test that agent requests clarification for vague queries."""
        agent = IntentAgent()
        vague_query = "I want to go somewhere fun"

        with pytest.raises(NotImplementedError):
            result = await agent.parse(vague_query)

        # Expected:
        # clarifications = await agent.clarify(result)
        # assert len(clarifications) > 0
        # assert any("destination" in q.lower() for q in clarifications)

    @pytest.mark.asyncio
    async def test_budget_extraction(self):
        """Test extraction of budget constraints."""
        agent = IntentAgent()
        query = "Budget trip to Bangkok for 5 days"

        with pytest.raises(NotImplementedError):
            result = await agent.parse(query)

        # Expected:
        # assert result["budget_level"] == "budget"

    @pytest.mark.asyncio
    async def test_dietary_restrictions(self):
        """Test extraction of dietary requirements."""
        agent = IntentAgent()
        query = "Week in Rome, vegetarian, love pasta"

        with pytest.raises(NotImplementedError):
            result = await agent.parse(query)

        # Expected:
        # assert "vegetarian" in result["dietary_restrictions"]
        # assert "pasta" in result["interests"]
