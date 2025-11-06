"""
Pytest configuration and shared fixtures.

Provides common test fixtures for mocking API responses,
creating test data, and configuring the test environment.
"""

import pytest
from httpx_mock import HTTPXMock


@pytest.fixture
def sample_travel_request() -> dict:
    """Sample travel request for testing."""
    return {
        "destinations": ["Kyoto"],
        "start_date": "2025-11-10",
        "end_date": "2025-11-13",
        "duration_days": 4,
        "interests": ["temples", "coffee shops", "gardens"],
        "mobility": "walking",
        "pace": "moderate",
        "max_walk_km_per_day": 10.0,
        "raw_query": "Plan 4 days in Kyoto, mostly walkable, love coffee shops and temples",
    }


@pytest.fixture
def sample_pois() -> list[dict]:
    """Sample POI data for testing."""
    return [
        {
            "id": "W123456",
            "source": "opentripmap",
            "name": "Kinkaku-ji Temple",
            "category": "temple",
            "tags": ["buddhist", "historic", "garden"],
            "latitude": 35.039444,
            "longitude": 135.729167,
            "rating": 4.7,
            "estimated_visit_duration_minutes": 90,
        },
        {
            "id": "N789012",
            "source": "osm",
            "name": "Vermillion Coffee",
            "category": "cafe",
            "tags": ["coffee", "specialty"],
            "latitude": 35.011,
            "longitude": 135.768,
            "rating": 4.5,
            "estimated_visit_duration_minutes": 45,
        },
    ]


@pytest.fixture
def sample_weather_forecast() -> dict:
    """Sample weather forecast for testing."""
    return {
        "location": "Kyoto",
        "latitude": 35.0,
        "longitude": 135.73,
        "timezone": "Asia/Tokyo",
        "forecasts": [
            {
                "date": "2025-11-10",
                "temperature_max_celsius": 18.0,
                "temperature_min_celsius": 10.0,
                "precipitation_probability": 0.2,
                "weather_code": 1,
                "weather_description": "Mainly clear",
                "category": "excellent",
            }
        ],
    }


@pytest.fixture
def mock_opentripmap_response() -> dict:
    """Mock response from OpenTripMap API."""
    return {
        "features": [
            {
                "xid": "W123456",
                "name": "Kinkaku-ji",
                "kinds": "buddhist_temples,cultural,interesting_places",
                "osm": "way/123456",
                "point": {"lon": 135.729167, "lat": 35.039444},
            }
        ]
    }


@pytest.fixture
def mock_openmeteo_response() -> dict:
    """Mock response from Open-Meteo API."""
    return {
        "latitude": 35.0,
        "longitude": 135.73,
        "timezone": "Asia/Tokyo",
        "daily": {
            "time": ["2025-11-10"],
            "temperature_2m_max": [18.0],
            "temperature_2m_min": [10.0],
            "precipitation_sum": [0.0],
            "weathercode": [1],
        },
    }


@pytest.fixture
def mock_osrm_response() -> dict:
    """Mock response from OSRM API."""
    return {
        "routes": [
            {
                "distance": 1234.5,
                "duration": 987.6,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[135.729167, 35.039444], [135.740, 35.045]],
                },
            }
        ]
    }


@pytest.fixture
def httpx_mock_with_apis(httpx_mock: HTTPXMock) -> HTTPXMock:
    """
    HTTPXMock with common API responses pre-configured.

    Usage in tests:
        def test_something(httpx_mock_with_apis):
            # API mocks already set up
            result = await agent.fetch_data()
    """
    # OpenTripMap
    httpx_mock.add_response(
        url__regex=r"https://api\.opentripmap\.com/.*",
        json={
            "features": [
                {
                    "xid": "W123456",
                    "name": "Test POI",
                    "point": {"lon": 135.0, "lat": 35.0},
                }
            ]
        },
    )

    # Open-Meteo
    httpx_mock.add_response(
        url__regex=r"https://api\.open-meteo\.com/.*",
        json={
            "latitude": 35.0,
            "longitude": 135.0,
            "daily": {"time": [], "temperature_2m_max": []},
        },
    )

    # OSRM
    httpx_mock.add_response(
        url__regex=r"http://router\.project-osrm\.org/.*",
        json={"routes": [{"distance": 1000, "duration": 600}]},
    )

    return httpx_mock
