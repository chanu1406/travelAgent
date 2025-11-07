"""
Quick test script to verify API clients are working.

Run with: python test_apis.py
"""

import asyncio
from datetime import date, timedelta

from src.travelmind.services.geoapify import GeoapifyClient
from src.travelmind.services.openmeteo import OpenMeteoClient
from src.travelmind.utils.config import settings


async def test_geoapify():
    """Test Geoapify API client."""
    print("\n=== Testing Geoapify API ===")

    if not settings.geoapify_api_key:
        print("❌ GEOAPIFY_API_KEY not set in .env")
        return

    print(f"API Key starts with: {settings.geoapify_api_key[:10]}...")

    client = GeoapifyClient(settings.geoapify_api_key)

    try:
        # Search for coffee shops in Tokyo
        print("Searching for coffee shops in Tokyo...")
        results = await client.search_nearby(
            latitude=35.6762,  # Tokyo
            longitude=139.6503,
            categories=["catering.cafe"],
            radius_meters=2000,
            limit=5,
        )

        print(f"✅ Found {len(results)} places in Tokyo")

        if results:
            # Convert first result to POI
            poi = client.convert_to_poi(results[0])
            print(f"\nExample POI:")
            print(f"  Name: {poi.name}")
            print(f"  Category: {poi.category}")
            print(f"  Address: {poi.address}")
            print(f"  Tags: {', '.join(poi.tags[:3])}")

    except Exception as e:
        print(f"❌ Geoapify test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def test_openmeteo():
    """Test Open-Meteo API client."""
    print("\n=== Testing Open-Meteo API ===")

    client = OpenMeteoClient()

    try:
        # Get weather forecast for Tokyo
        today = date.today()
        end_date = today + timedelta(days=3)

        forecast = await client.get_forecast(
            latitude=35.6762,  # Tokyo
            longitude=139.6503,
            start_date=today,
            end_date=end_date,
            timezone="Asia/Tokyo",
        )

        print(f"✅ Got {len(forecast['daily'])} days of weather data for Tokyo")

        if forecast["daily"]:
            day = forecast["daily"][0]
            print(f"\nToday's forecast:")
            print(f"  Temperature: {day['temperature_min_celsius']}°C - {day['temperature_max_celsius']}°C")
            print(f"  Conditions: {day['weather_description']}")
            print(f"  Precipitation: {day['precipitation_probability']*100:.0f}% chance")

    except Exception as e:
        print(f"❌ Open-Meteo test failed: {e}")
    finally:
        await client.close()


async def main():
    """Run all tests."""
    print("Testing API clients...")
    await test_geoapify()
    await test_openmeteo()
    print("\n✅ All tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
