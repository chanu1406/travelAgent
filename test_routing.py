"""
Test the OSRM routing client.

Run with: python test_routing.py
"""

import asyncio

from src.travelmind.services.routing import OSRMClient


async def test_osrm_client():
    """Test OSRM routing and table services."""
    print("=== Testing OSRM Client ===\n")

    client = OSRMClient()

    # Test coordinates (Kyoto)
    fushimi_inari = (34.9671, 135.7727)  # Fushimi Inari Shrine
    kinkakuji = (35.0394, 135.7292)  # Kinkaku-ji (Golden Pavilion)
    kiyomizudera = (34.9949, 135.7850)  # Kiyomizu-dera

    print("Test 1: Route from Fushimi Inari to Kinkaku-ji (walking)")
    try:
        route = await client.get_route(
            coordinates=[fushimi_inari, kinkakuji],
            profile="walking",
        )
        print(f"  Distance: {route['distance']:.0f} meters")
        print(f"  Duration: {route['duration'] / 60:.1f} minutes")
        print(f"  Geometry type: {route['geometry']['type']}")
        print(f"  Coordinates: {len(route['geometry']['coordinates'])} points")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    print("Test 2: Distance/time matrix for 3 locations")
    try:
        matrix = await client.get_table(
            coordinates=[fushimi_inari, kinkakuji, kiyomizudera],
            profile="walking",
        )
        print("  Durations (minutes):")
        for i, row in enumerate(matrix["durations"]):
            durations_min = [f"{d/60:.1f}" if d is not None else "N/A" for d in row]
            print(f"    From {i}: {durations_min}")

        print("  Distances (km):")
        for i, row in enumerate(matrix["distances"]):
            distances_km = [f"{d/1000:.2f}" if d is not None else "N/A" for d in row]
            print(f"    From {i}: {distances_km}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    await client.close()
    print("\n✅ Tests complete!")


if __name__ == "__main__":
    asyncio.run(test_osrm_client())
