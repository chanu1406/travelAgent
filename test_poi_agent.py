"""
Test the POI Agent to see if it can find points of interest based on user preferences.

Run with: python test_poi_agent.py
"""

import asyncio

from src.travelmind.agents.poi import POIAgent


async def test_poi_agent():
    """Test the POI Agent with various location and interest combinations."""
    print("=== Testing POI Agent ===\n")

    agent = POIAgent()

    # Test 1: Kyoto with temples and coffee shops
    print("Test 1: Kyoto - temples and coffee shops")
    try:
        pois = await agent.search(
            location="Kyoto, Japan",
            interests=["temples", "coffee shops"],
            radius_km=5.0,
            limit=10,
        )
        print(f"  Found {len(pois)} POIs")
        print("  Top 5 results:")
        for poi in pois[:5]:
            print(f"    - {poi.name} ({poi.category})")
            print(f"      {poi.latitude:.4f}, {poi.longitude:.4f}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    # Test 2: Paris with art galleries and restaurants
    print("Test 2: Paris - art galleries and restaurants")
    try:
        pois = await agent.search(
            location="Paris, France",
            interests=["art galleries", "restaurants"],
            radius_km=3.0,
            limit=10,
        )
        print(f"  Found {len(pois)} POIs")
        print("  Top 5 results:")
        for poi in pois[:5]:
            print(f"    - {poi.name} ({poi.category})")
            if poi.address:
                print(f"      {poi.address}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    # Test 3: Tokyo with museums
    print("Test 3: Tokyo - museums")
    try:
        pois = await agent.search(
            location="Tokyo, Japan",
            interests=["museums"],
            radius_km=10.0,
            limit=10,
        )
        print(f"  Found {len(pois)} POIs")
        print("  Top 5 results:")
        for poi in pois[:5]:
            print(f"    - {poi.name}")
            if poi.opening_hours:
                print(f"      Hours: {poi.opening_hours}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    await agent.close()
    print("\n✅ Tests complete!")


if __name__ == "__main__":
    asyncio.run(test_poi_agent())
