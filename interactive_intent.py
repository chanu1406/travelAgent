"""
Interactive Intent Parser

Allows you to test the Intent Agent with your own queries in real-time.

Run with: python interactive_intent.py
"""

import asyncio

from src.travelmind.agents.intent import IntentAgent


async def interactive_mode():
    """Run an interactive session for testing the Intent Agent."""
    print("=" * 70)
    print("Interactive Intent Parser")
    print("=" * 70)
    print()
    print("Enter travel queries to see how the Intent Agent parses them.")
    print("Type 'quit' or 'exit' to stop.")
    print()

    # Initialize the Intent Agent
    print("Initializing Intent Agent...")
    agent = IntentAgent()
    print("Ready!\n")

    while True:
        # Get user input
        print("-" * 70)
        query = input("Enter your travel query: ").strip()
        print()

        # Check for exit commands
        if query.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Skip empty queries
        if not query:
            print("Please enter a query.\n")
            continue

        # Parse the query
        try:
            print("Parsing...")
            result = await agent.parse(query)

            print("\n✅ Parsed Successfully!")
            print("-" * 70)

            # Display results in a formatted way
            for key, value in result.items():
                if value is not None and key != "raw_query":
                    # Format the key nicely
                    formatted_key = key.replace("_", " ").title()

                    # Format the value
                    if isinstance(value, list):
                        if value:  # Only show non-empty lists
                            print(f"{formatted_key}:")
                            for item in value:
                                print(f"  • {item}")
                        else:
                            print(f"{formatted_key}: (none)")
                    else:
                        print(f"{formatted_key}: {value}")

            # Check for clarifications needed
            questions = await agent.clarify(result)
            if questions:
                print("\n⚠️  Clarifications Needed:")
                for q in questions:
                    print(f"  ? {q}")

            print()

        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    try:
        asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
