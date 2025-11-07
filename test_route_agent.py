"""
Test the Route Agent for route optimization and distance calculations.

Run with: python test_route_agent.py
"""

import asyncio

from src.travelmind.agents.route import RouteAgent
from src.travelmind.models.poi import POI


async def test_route_agent():
    """Test the Route Agent's routing and optimization capabilities."""
    print("=== Testing Route Agent ===\n")

    agent = RouteAgent(provider="osrm")

    # Test locations in Kyoto
    hotel = (35.0116, 135.7681)  # Central Kyoto (example hotel location)

    # Create sample POIs
    pois = [
        POI(
            id="1",
            source="test",
            name="Fushimi Inari Shrine",
            category="temple",
            latitude=34.9671,
            longitude=135.7727,
            estimated_visit_duration_minutes=90,
        ),
        POI(
            id="2",
            source="test",
            name="Kinkaku-ji (Golden Pavilion)",
            category="temple",
            latitude=35.0394,
            longitude=135.7292,
            estimated_visit_duration_minutes=60,
        ),
        POI(
            id="3",
            source="test",
            name="Kiyomizu-dera",
            category="temple",
            latitude=34.9949,
            longitude=135.7850,
            estimated_visit_duration_minutes=75,
        ),
    ]

    print("Test 1: Calculate single route")
    print(f"From: Hotel to {pois[0].name}")
    route = await agent.get_route(
        origin=hotel,
        destination=(pois[0].latitude, pois[0].longitude),
        mode="walking",
    )
    print(f"  Distance: {route['distance']/1000:.2f} km")
    print(f"  Duration: {route['duration']/60:.1f} minutes")
    print()

    print("Test 2: Get distance matrix")
    locations = [hotel] + [(poi.latitude, poi.longitude) for poi in pois]
    matrix = await agent.get_distance_matrix(locations, mode="walking")
    print("  Travel times (minutes) from hotel:")
    for i, poi in enumerate(pois):
        print(f"    To {poi.name}: {matrix[0][i+1]:.1f} min")
    print()

    print("Test 3: Optimize visit order")
    print(f"  Original order: {[poi.name for poi in pois]}")
    optimized_pois = await agent.optimize_visit_order(
        pois=pois,
        start_location=hotel,
        mode="walking",
    )
    print(f"  Optimized order: {[poi.name for poi in optimized_pois]}")
    print()

    # Calculate total travel time for optimized route
    locations_optimized = [hotel] + [
        (poi.latitude, poi.longitude) for poi in optimized_pois
    ]
    total_time = 0
    for i in range(len(locations_optimized) - 1):
        route = await agent.get_route(
            locations_optimized[i], locations_optimized[i + 1], "walking"
        )
        total_time += route["duration"] / 60

    print(f"  Total walking time: {total_time:.1f} minutes")
    print(f"  Total visit time: {sum(poi.estimated_visit_duration_minutes for poi in optimized_pois)} minutes")
    print(f"  Total day time: {(total_time + sum(poi.estimated_visit_duration_minutes for poi in optimized_pois))/60:.1f} hours")
    print()

    await agent.close()
    print("✅ Route Agent tests complete!")


if __name__ == "__main__":
    asyncio.run(test_route_agent())
