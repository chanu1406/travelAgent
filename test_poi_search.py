"""
Test POI search with different categories to see what works best.
"""

import asyncio

from src.travelmind.agents.poi import POIAgent


async def test_poi_search():
    """Test different search strategies."""
    agent = POIAgent()

    print("=" * 80)
    print("Testing POI Search for Kyoto Temples")
    print("=" * 80)
    print()

    # Test 1: Search with "temples" interest
    print("Test 1: Search with interest='temples'")
    print("-" * 80)
    pois = await agent.search(
        location="Kyoto",
        interests=["temples"],
        limit=10,
    )

    print(f"Found {len(pois)} POIs:")
    for i, poi in enumerate(pois[:10], 1):
        print(f"  {i}. {poi.name} ({poi.category})")
    print()

    # Test 2: Search with "cultural sites" interest
    print("Test 2: Search with interest='cultural sites'")
    print("-" * 80)
    pois = await agent.search(
        location="Kyoto",
        interests=["cultural sites"],
        limit=10,
    )

    print(f"Found {len(pois)} POIs:")
    for i, poi in enumerate(pois[:10], 1):
        print(f"  {i}. {poi.name} ({poi.category})")
    print()

    # Test 3: Search with both
    print("Test 3: Search with interests=['temples', 'museums']")
    print("-" * 80)
    pois = await agent.search(
        location="Kyoto",
        interests=["temples", "museums"],
        limit=10,
    )

    print(f"Found {len(pois)} POIs:")
    for i, poi in enumerate(pois[:15], 1):
        print(f"  {i}. {poi.name} ({poi.category})")
    print()

    await agent.close()


if __name__ == "__main__":
    asyncio.run(test_poi_search())
