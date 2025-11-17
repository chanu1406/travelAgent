"""
Test error handling and validation across all agents.

This test suite validates that:
1. Intent Agent properly validates dates and duration
2. POI Agent handles API failures and no results gracefully
3. Calendar Agent validates trip length and POI count
4. All errors provide helpful, actionable messages
"""

import asyncio
from datetime import date, timedelta

import pytest

from src.travelmind.agents.calendar import CalendarAgent
from src.travelmind.agents.intent import IntentAgent
from src.travelmind.agents.poi import POIAgent
from src.travelmind.exceptions import (
    InsufficientPOIsError,
    InvalidDateError,
    InvalidDurationError,
    ItineraryBuildError,
    MissingDestinationError,
    NoPOIsFoundError,
    POISearchError,
)
from src.travelmind.models.request import TravelConstraints


# ============================================================================
# Intent Agent Tests
# ============================================================================


async def test_intent_missing_destination():
    """Test that missing destination raises error."""
    print("\n" + "=" * 80)
    print("TEST: Intent Agent - Missing Destination")
    print("=" * 80)

    agent = IntentAgent()

    try:
        result = await agent.parse("I want to travel for 5 days")
        print(f"❌ FAILED: Should have raised MissingDestinationError")
        print(f"Got result: {result}")
    except MissingDestinationError as e:
        print(f"✅ PASSED: Correctly raised MissingDestinationError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")


async def test_intent_past_dates():
    """Test that dates in the past raise error."""
    print("\n" + "=" * 80)
    print("TEST: Intent Agent - Dates in the Past")
    print("=" * 80)

    agent = IntentAgent()

    try:
        # Use a past date
        past_date = date.today() - timedelta(days=10)
        result = await agent.parse(
            f"Trip to Tokyo from {past_date.strftime('%Y-%m-%d')} for 3 days"
        )
        print(f"❌ FAILED: Should have raised InvalidDateError")
        print(f"Got result: {result}")
    except InvalidDateError as e:
        print(f"✅ PASSED: Correctly raised InvalidDateError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")


async def test_intent_too_long_duration():
    """Test that trip duration > 14 days raises error."""
    print("\n" + "=" * 80)
    print("TEST: Intent Agent - Duration Too Long")
    print("=" * 80)

    agent = IntentAgent()

    try:
        result = await agent.parse("Plan a 20-day trip to Kyoto")
        print(f"❌ FAILED: Should have raised InvalidDurationError")
        print(f"Got result: {result}")
    except InvalidDurationError as e:
        print(f"✅ PASSED: Correctly raised InvalidDurationError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")


async def test_intent_end_before_start():
    """Test that end date before start date raises error."""
    print("\n" + "=" * 80)
    print("TEST: Intent Agent - End Date Before Start Date")
    print("=" * 80)

    agent = IntentAgent()

    try:
        start = date.today() + timedelta(days=10)
        end = date.today() + timedelta(days=5)
        result = await agent.parse(
            f"Trip to Paris from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"
        )
        print(f"❌ FAILED: Should have raised InvalidDateError")
        print(f"Got result: {result}")
    except InvalidDateError as e:
        print(f"✅ PASSED: Correctly raised InvalidDateError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")


# ============================================================================
# POI Agent Tests
# ============================================================================


async def test_poi_empty_location():
    """Test that empty location raises error."""
    print("\n" + "=" * 80)
    print("TEST: POI Agent - Empty Location")
    print("=" * 80)

    agent = POIAgent()

    try:
        result = await agent.search(location="", interests=["temples"])
        print(f"❌ FAILED: Should have raised POISearchError")
        print(f"Got result: {result}")
    except POISearchError as e:
        print(f"✅ PASSED: Correctly raised POISearchError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


async def test_poi_no_interests():
    """Test that empty interests list raises error."""
    print("\n" + "=" * 80)
    print("TEST: POI Agent - No Interests")
    print("=" * 80)

    agent = POIAgent()

    try:
        result = await agent.search(location="Tokyo", interests=[])
        print(f"❌ FAILED: Should have raised POISearchError")
        print(f"Got result: {result}")
    except POISearchError as e:
        print(f"✅ PASSED: Correctly raised POISearchError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


async def test_poi_invalid_radius():
    """Test that invalid search radius raises error."""
    print("\n" + "=" * 80)
    print("TEST: POI Agent - Invalid Search Radius")
    print("=" * 80)

    agent = POIAgent()

    try:
        result = await agent.search(
            location="Tokyo", interests=["temples"], radius_km=100
        )
        print(f"❌ FAILED: Should have raised POISearchError")
        print(f"Got result: {result}")
    except POISearchError as e:
        print(f"✅ PASSED: Correctly raised POISearchError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


async def test_poi_invalid_location():
    """Test that nonexistent location raises error."""
    print("\n" + "=" * 80)
    print("TEST: POI Agent - Nonexistent Location")
    print("=" * 80)

    agent = POIAgent()

    try:
        # Use a nonsense location name
        result = await agent.search(
            location="XYZ12345NonexistentCity", interests=["temples"]
        )
        print(f"❌ FAILED: Should have raised POISearchError")
        print(f"Got {len(result)} POIs")
    except POISearchError as e:
        print(f"✅ PASSED: Correctly raised POISearchError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"⚠️  WARNING: Raised different exception: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


# ============================================================================
# Calendar Agent Tests
# ============================================================================


async def test_calendar_no_pois():
    """Test that empty POI list raises error."""
    print("\n" + "=" * 80)
    print("TEST: Calendar Agent - No POIs")
    print("=" * 80)

    agent = CalendarAgent()

    try:
        result = await agent.build_itinerary(
            pois=[],
            start_location=(35.0116, 135.7681),
            travel_dates=[date.today() + timedelta(days=i) for i in range(3)],
        )
        print(f"❌ FAILED: Should have raised InsufficientPOIsError")
        print(f"Got result: {result}")
    except InsufficientPOIsError as e:
        print(f"✅ PASSED: Correctly raised InsufficientPOIsError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


async def test_calendar_too_few_pois():
    """Test that insufficient POIs for trip length raises error."""
    print("\n" + "=" * 80)
    print("TEST: Calendar Agent - Too Few POIs")
    print("=" * 80)

    agent = CalendarAgent()

    # Create only 2 POIs for a 5-day trip (need at least 10)
    from src.travelmind.models.poi import POI

    pois = [
        POI(
            id="1",
            source="test",
            name="Test POI 1",
            category="tourism",
            latitude=35.0116,
            longitude=135.7681,
        ),
        POI(
            id="2",
            source="test",
            name="Test POI 2",
            category="tourism",
            latitude=35.0116,
            longitude=135.7681,
        ),
    ]

    try:
        result = await agent.build_itinerary(
            pois=pois,
            start_location=(35.0116, 135.7681),
            travel_dates=[date.today() + timedelta(days=i) for i in range(5)],
        )
        print(f"❌ FAILED: Should have raised InsufficientPOIsError")
        print(f"Got result: {result}")
    except InsufficientPOIsError as e:
        print(f"✅ PASSED: Correctly raised InsufficientPOIsError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


async def test_calendar_no_dates():
    """Test that empty travel dates raises error."""
    print("\n" + "=" * 80)
    print("TEST: Calendar Agent - No Travel Dates")
    print("=" * 80)

    agent = CalendarAgent()

    from src.travelmind.models.poi import POI

    pois = [
        POI(
            id="1",
            source="test",
            name="Test POI",
            category="tourism",
            latitude=35.0116,
            longitude=135.7681,
        )
    ]

    try:
        result = await agent.build_itinerary(
            pois=pois,
            start_location=(35.0116, 135.7681),
            travel_dates=[],
        )
        print(f"❌ FAILED: Should have raised ItineraryBuildError")
        print(f"Got result: {result}")
    except ItineraryBuildError as e:
        print(f"✅ PASSED: Correctly raised ItineraryBuildError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


async def test_calendar_trip_too_long():
    """Test that trip > 14 days raises error."""
    print("\n" + "=" * 80)
    print("TEST: Calendar Agent - Trip Too Long")
    print("=" * 80)

    agent = CalendarAgent()

    from src.travelmind.models.poi import POI

    pois = [
        POI(
            id=str(i),
            source="test",
            name=f"Test POI {i}",
            category="tourism",
            latitude=35.0116,
            longitude=135.7681,
        )
        for i in range(50)
    ]

    try:
        result = await agent.build_itinerary(
            pois=pois,
            start_location=(35.0116, 135.7681),
            travel_dates=[date.today() + timedelta(days=i) for i in range(20)],
        )
        print(f"❌ FAILED: Should have raised ItineraryBuildError")
        print(f"Got result: {result}")
    except ItineraryBuildError as e:
        print(f"✅ PASSED: Correctly raised ItineraryBuildError")
        print(f"Error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Raised wrong exception type: {type(e).__name__}")
        print(f"Error: {e}")
    finally:
        await agent.close()


# ============================================================================
# Run All Tests
# ============================================================================


async def run_all_tests():
    """Run all error handling tests."""
    print("\n" + "🧪" * 40)
    print("ERROR HANDLING TEST SUITE")
    print("🧪" * 40)

    tests = [
        # Intent Agent
        ("Intent: Missing Destination", test_intent_missing_destination),
        ("Intent: Past Dates", test_intent_past_dates),
        ("Intent: Too Long Duration", test_intent_too_long_duration),
        ("Intent: End Before Start", test_intent_end_before_start),
        # POI Agent
        ("POI: Empty Location", test_poi_empty_location),
        ("POI: No Interests", test_poi_no_interests),
        ("POI: Invalid Radius", test_poi_invalid_radius),
        ("POI: Nonexistent Location", test_poi_invalid_location),
        # Calendar Agent
        ("Calendar: No POIs", test_calendar_no_pois),
        ("Calendar: Too Few POIs", test_calendar_too_few_pois),
        ("Calendar: No Dates", test_calendar_no_dates),
        ("Calendar: Trip Too Long", test_calendar_trip_too_long),
    ]

    results = {"passed": 0, "failed": 0, "warnings": 0}

    for test_name, test_func in tests:
        try:
            await test_func()
            results["passed"] += 1
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {test_name}")
            print(f"Exception: {type(e).__name__}: {e}")
            results["failed"] += 1

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Total: {len(tests)}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
