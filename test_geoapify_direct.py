"""
Test Geoapify API directly to understand what categories work.
"""

import asyncio

from src.travelmind.services.geoapify import GeoapifyClient
from src.travelmind.utils.config import settings


async def test_geoapify():
    """Test direct Geoapify queries."""
    client = GeoapifyClient(api_key=settings.geoapify_api_key)

    # Geocode Kyoto
    location = await client.geocode("Kyoto")
    print(f"Kyoto center: {location['latitude']}, {location['longitude']}")
    print()

    # Test different category searches
    categories_to_test = [
        "religion",
        "religion.buddhist",
        "religion.shinto",
        "tourism",
        "tourism.attraction",
        "heritage",
        "entertainment.museum",
    ]

    for category in categories_to_test:
        print(f"Category: {category}")
        print("-" * 80)
        try:
            pois = await client.search_nearby(
                latitude=location["latitude"],
                longitude=location["longitude"],
                query=None,
                categories=category,
                radius_meters=15000,
                limit=10,
            )
            print(f"  Found {len(pois)} POIs")
            for poi in pois[:5]:
                print(f"    - {poi.name} ({poi.category})")
        except Exception as e:
            print(f"  Error: {e}")
        print()

    # Test text search
    print("Text search: 'temple'")
    print("-" * 80)
    try:
        pois = await client.search_nearby(
            latitude=location["latitude"],
            longitude=location["longitude"],
            query="temple",
            categories=None,
            radius_meters=15000,
            limit=10,
        )
        print(f"  Found {len(pois)} POIs")
        for poi in pois[:5]:
            print(f"    - {poi.name} ({poi.category})")
    except Exception as e:
        print(f"  Error: {e}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(test_geoapify())
