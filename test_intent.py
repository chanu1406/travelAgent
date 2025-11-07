"""
Test the Intent Agent to see if it can parse natural language travel requests.

Run with: python test_intent.py
"""

import asyncio

from src.travelmind.agents.intent import IntentAgent


async def test_intent_agent():
    """Test the Intent Agent with various queries."""
    print("=== Testing Intent Agent ===\n")

    agent = IntentAgent()

    # Test queries
    queries = [
        "4 days in Kyoto, love temples and coffee shops, prefer walking",
        "Plan a week in Tokyo and Osaka, I'm into street food and museums",
        "3 days in Paris, moderate budget, interested in art galleries",
    ]

    for query in queries:
        print(f"Query: {query}")
        try:
            result = await agent.parse(query)
            print("Parsed:")
            for key, value in result.items():
                if value is not None:
                    print(f"  {key}: {value}")

            # Check if clarification is needed
            questions = await agent.clarify(result)
            if questions:
                print("Clarifications needed:")
                for q in questions:
                    print(f"  - {q}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print()


if __name__ == "__main__":
    asyncio.run(test_intent_agent())
