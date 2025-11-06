# API Integrations Reference

Complete guide to all external data sources used by TravelMind.

## Overview

All APIs used are **free tier or open data**. No paid subscriptions required.

| Service | Cost | API Key Required | Rate Limit | Purpose |
|---------|------|-----------------|------------|---------|
| OpenTripMap | Free | Yes (free) | 500/day | Tourist attractions |
| Open-Meteo | Free | No | 10k/day | Weather forecasts |
| Overpass (OSM) | Free | No | ~2 req/s | Restaurants, cafes |
| OSRM | Free | No | ~2 req/s | Routing (walking/driving) |
| OpenRouteService | Free tier | Yes (free) | 40/min | Routing (alternative) |

---

## OpenTripMap

**Purpose**: Tourist attractions (museums, monuments, viewpoints, nature)

### Getting Started
1. Sign up at: https://opentripmap.io/
2. Get free API key (no credit card required)
3. Add to `.env`: `OPENTRIPMAP_API_KEY=your_key`

### API Documentation
https://opentripmap.io/docs

### Endpoints Used

#### 1. Radius Search
```http
GET /0.1/en/places/radius
  ?radius=5000
  &lon=135.729167
  &lat=35.039444
  &kinds=museums,monuments
  &limit=50
  &apikey=YOUR_KEY
```

**Response**:
```json
[
  {
    "xid": "W123456",
    "name": "Kinkaku-ji",
    "kinds": "buddhist_temples,cultural,interesting_places",
    "osm": "way/123456",
    "point": {"lon": 135.729167, "lat": 35.039444}
  }
]
```

#### 2. Place Details
```http
GET /0.1/en/places/xid/{xid}?apikey=YOUR_KEY
```

**Response**:
```json
{
  "xid": "W123456",
  "name": "Kinkaku-ji",
  "address": {"city": "Kyoto", "road": "Kinkakujicho"},
  "rate": 7,
  "osm": "way/123456",
  "wikidata": "Q429572",
  "wikipedia": "en:Kinkaku-ji",
  "image": "https://...",
  "preview": {"source": "...", "height": 300, "width": 400},
  "wikipedia_extracts": {"text": "...", "html": "..."},
  "point": {"lon": 135.729167, "lat": 35.039444}
}
```

### Categories (kinds)
```
accomodations, adult, amusements, banks, beaches, bridges,
buddhist_temples, burial_places, castles, churches,
entertainment, ferries, fortifications, gardens, glaciers,
historic, industrial_facilities, interesting_places,
monuments, mosques, museums, natural, other, palaces,
parks, religion, restaurants, roads, sport, temples,
theatres_and_entertainments, towers, tourist_facilities,
urban_environment, viewpoints, water, wineries
```

### Rate Limits
- 500 requests per day
- 1 request per second
- Exceeding limits returns 429 status

### Caching Strategy
- Cache POI lists: 7 days
- Cache detailed info: 30 days

---

## Open-Meteo

**Purpose**: Weather forecasts

### Getting Started
1. No sign-up needed
2. No API key required
3. Just start making requests!

### API Documentation
https://open-meteo.com/en/docs

### Endpoint Used

```http
GET /v1/forecast
  ?latitude=35.039444
  &longitude=135.729167
  &start_date=2025-11-10
  &end_date=2025-11-13
  &daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode,sunrise,sunset
  &hourly=temperature_2m,precipitation_probability,precipitation,weathercode,windspeed_10m
  &timezone=Asia/Tokyo
```

**Response**:
```json
{
  "latitude": 35.0,
  "longitude": 135.73,
  "timezone": "Asia/Tokyo",
  "daily": {
    "time": ["2025-11-10", "2025-11-11", ...],
    "temperature_2m_max": [18.0, 19.5, ...],
    "temperature_2m_min": [10.0, 11.2, ...],
    "precipitation_sum": [0.0, 2.3, ...],
    "weathercode": [1, 61, ...]
  },
  "hourly": {
    "time": ["2025-11-10T00:00", "2025-11-10T01:00", ...],
    "temperature_2m": [12.0, 11.5, ...],
    ...
  }
}
```

### Weather Codes (WMO)
```
0 = Clear sky
1 = Mainly clear
2 = Partly cloudy
3 = Overcast
45 = Fog
51-55 = Drizzle
61-65 = Rain
71-77 = Snow
80-82 = Rain showers
95-99 = Thunderstorm
```

### Rate Limits
- 10,000 requests per day per IP
- Very generous for personal use

### Caching Strategy
- Cache forecasts: 6 hours (updates throughout day)

---

## OpenStreetMap (Overpass API)

**Purpose**: Restaurants, cafes, parks, shops

### Getting Started
1. No sign-up needed
2. No API key required
3. Public Overpass instances available

### API Documentation
https://wiki.openstreetmap.org/wiki/Overpass_API

### Query Language: Overpass QL

Example: Find cafes near Kyoto
```overpass
[out:json];
node["amenity"="cafe"](around:2000,35.0,135.73);
out body;
```

### Endpoint
```http
POST https://overpass-api.de/api/interpreter
Content-Type: application/x-www-form-urlencoded

data=[out:json];node["amenity"="cafe"](around:2000,35.0,135.73);out body;
```

**Response**:
```json
{
  "elements": [
    {
      "type": "node",
      "id": 123456,
      "lat": 35.0,
      "lon": 135.73,
      "tags": {
        "amenity": "cafe",
        "name": "Coffee House",
        "opening_hours": "Mo-Su 08:00-20:00",
        "cuisine": "coffee_shop"
      }
    }
  ]
}
```

### Common Tags
```
amenity=restaurant,cafe,bar,fast_food
tourism=museum,attraction,viewpoint,hotel
leisure=park,playground,garden
shop=*
historic=monument,castle,temple
```

### Rate Limits
- ~2 requests per second (be respectful)
- Queries timing out? Reduce radius or add limits

### Caching Strategy
- Cache POI lists: 7 days

---

## OSRM (Open Source Routing Machine)

**Purpose**: Routing and distance calculations

### Getting Started
1. No sign-up needed
2. No API key required
3. Public demo: http://router.project-osrm.org
4. Or self-host: https://github.com/Project-OSRM/osrm-backend

### API Documentation
https://project-osrm.org/docs/v5.24.0/api/

### Endpoints Used

#### 1. Route Service
```http
GET /route/v1/foot/135.729167,35.039444;135.740,35.045
  ?overview=full
  &geometries=geojson
```

**Response**:
```json
{
  "routes": [
    {
      "distance": 1234.5,  // meters
      "duration": 987.6,   // seconds
      "geometry": {
        "type": "LineString",
        "coordinates": [[135.729167, 35.039444], ...]
      }
    }
  ]
}
```

#### 2. Table Service (Distance Matrix)
```http
GET /table/v1/foot/135.729167,35.039444;135.740,35.045;135.750,35.050
```

**Response**:
```json
{
  "durations": [
    [0, 987.6, 1234.5],
    [987.6, 0, 456.7],
    [1234.5, 456.7, 0]
  ],
  "distances": [
    [0, 1234, 2345],
    [1234, 0, 678],
    [2345, 678, 0]
  ]
}
```

### Profiles
- `foot`: Walking
- `car`: Driving
- `bike`: Cycling

### Rate Limits
- Public demo: ~2 requests per second
- Self-hosted: No limits

### Caching Strategy
- Cache routes: 30 days (rarely change)

---

## OpenRouteService

**Purpose**: Routing (alternative to OSRM, more features)

### Getting Started
1. Sign up at: https://openrouteservice.org/dev/#/signup
2. Get free API key (no credit card)
3. Add to `.env`: `OPENROUTESERVICE_API_KEY=your_key`

### API Documentation
https://openrouteservice.org/dev/#/api-docs

### Endpoints Used

#### 1. Directions
```http
POST /v2/directions/foot-walking
Authorization: YOUR_KEY
Content-Type: application/json

{
  "coordinates": [[135.729167, 35.039444], [135.740, 35.045]]
}
```

**Response**:
```json
{
  "routes": [
    {
      "summary": {"distance": 1234.5, "duration": 987.6},
      "geometry": {...}
    }
  ]
}
```

#### 2. Matrix
```http
POST /v2/matrix/foot-walking
Authorization: YOUR_KEY
Content-Type: application/json

{
  "locations": [
    [135.729167, 35.039444],
    [135.740, 35.045]
  ]
}
```

### Profiles
- `foot-walking`
- `driving-car`
- `cycling-regular`

### Rate Limits (Free Tier)
- 40 requests per minute
- 2,000 requests per day

### Caching Strategy
- Cache routes: 30 days

---

## Error Handling

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| 429 Too Many Requests | Rate limit exceeded | Wait and retry, check cache |
| 401 Unauthorized | Invalid/missing API key | Check `.env` configuration |
| 503 Service Unavailable | API temporarily down | Retry with exponential backoff |
| Timeout | Slow response | Increase timeout, reduce query size |

### Retry Strategy
```python
# Implemented in utils/rate_limit.py
async def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except (httpx.HTTPError, TimeoutError):
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
            else:
                raise
```

---

## Testing Without API Keys

For development/testing without real API keys:

1. **Use cached data**: Run once with keys, then work offline
2. **Mock responses**: Use `httpx-mock` in tests
3. **Local services**: Self-host OSRM for unlimited routing

Example test setup:
```python
import pytest
from httpx_mock import HTTPXMock

@pytest.mark.asyncio
async def test_poi_search(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.opentripmap.com/...",
        json={"features": [...]}
    )
    # Test POI agent
```
