# Agent Reference

This document details each agent's responsibilities, inputs, outputs, and implementation notes.

## Intent Agent

**Purpose**: Parse natural language travel requests into structured parameters.

### Responsibilities
- Extract destinations, dates, interests from user query
- Validate and normalize parameters
- Identify missing critical information
- Generate clarifying questions if needed

### Implementation
- Uses LLM (GPT-4, Claude, or local Llama) for NLU
- Structured output via function calling or JSON mode
- Pydantic validation of extracted parameters

### Input
```python
user_query: str  # e.g., "Plan 4 days in Kyoto, love temples and coffee"
```

### Output
```python
TravelRequest(
    destinations=["Kyoto"],
    duration_days=4,
    interests=["temples", "coffee"],
    mobility="walking",
    pace="moderate",
    raw_query="Plan 4 days in Kyoto, love temples and coffee"
)
```

### Edge Cases
- Ambiguous dates ("next month" → needs clarification)
- Vague interests ("fun stuff" → needs clarification)
- Multiple destinations with unclear routing
- Budget not specified (use defaults)

---

## POI Agent

**Purpose**: Find attractions, restaurants, and activities matching user interests.

### Responsibilities
- Query OpenTripMap for tourist attractions
- Query Overpass API (OSM) for restaurants, cafes, shops
- Deduplicate results from multiple sources
- Rank by relevance and quality
- Enrich with details (hours, descriptions, ratings)

### Data Sources
1. **OpenTripMap**: Museums, monuments, viewpoints, nature
2. **OpenStreetMap (Overpass)**: Restaurants, cafes, parks, shops

### Input
```python
location: str  # "Kyoto"
interests: list[str]  # ["temples", "coffee"]
radius_km: float  # 10.0
```

### Output
```python
[
    POI(
        id="W123456",
        source="osm",
        name="Kinkaku-ji Temple",
        category="temple",
        tags=["religious", "historic", "garden"],
        latitude=35.039444,
        longitude=135.729167,
        rating=4.7,
        estimated_visit_duration_minutes=90,
        ...
    ),
    ...
]
```

### Algorithms
- **Deduplication**: Fuzzy name matching + coordinate proximity
- **Ranking**: Score = (relevance × 0.4) + (rating × 0.3) + (popularity × 0.3)

### Caching
- TTL: 7 days
- Key: `f"poi:{location}:{interests_hash}:{radius}"`

---

## Weather Agent

**Purpose**: Fetch weather forecasts to inform scheduling decisions.

### Responsibilities
- Get 7-day hourly forecasts from Open-Meteo
- Categorize days (excellent/good/fair/indoor/challenging)
- Identify best time windows for outdoor activities
- Provide sunrise/sunset times

### Data Source
- **Open-Meteo**: Free, no key, 7-day forecasts

### Input
```python
latitude: float
longitude: float
start_date: date
end_date: date
```

### Output
```python
WeatherForecast(
    location="Kyoto",
    latitude=35.0,
    longitude=135.73,
    forecasts=[
        DailyForecast(
            date=date(2025, 11, 10),
            temperature_max_celsius=18,
            temperature_min_celsius=10,
            precipitation_probability=0.2,
            weather_code=1,
            weather_description="Mainly clear",
            category="excellent",
            best_activity_window=(9, 16),  # 9 AM - 4 PM
            ...
        ),
        ...
    ]
)
```

### Categorization Logic
- **Excellent**: Clear, temp 15-25°C, no rain
- **Good**: Partly cloudy, temp 10-28°C, <20% rain
- **Fair**: Overcast or cool, 20-40% rain
- **Indoor**: Rain likely (>60%), or extreme temps
- **Challenging**: Heavy rain, storms, or unsafe conditions

### Caching
- TTL: 6 hours (forecasts update regularly)

---

## Route Agent

**Purpose**: Calculate travel times and optimize visit order.

### Responsibilities
- Compute routes between POIs (walking, driving, cycling)
- Generate distance matrices for optimization
- Optimize visit order (TSP heuristic)
- Validate daily itineraries are feasible

### Data Sources
- **OSRM**: Free, no key, walking/driving/cycling
- **OpenRouteService**: Free tier with key, more features

### Input
```python
origin: tuple[float, float]  # (lat, lon)
destination: tuple[float, float]
mode: "walking" | "driving" | "cycling"
```

### Output
```python
{
    "distance_km": 2.3,
    "duration_minutes": 28,
    "geometry": [...],  # List of coordinates
}
```

### Optimization
- **Nearest Neighbor**: For small sets (<10 POIs)
- **2-opt**: For larger sets (10-20 POIs)
- **Constraint**: Respect max walking distance per day

### Caching
- TTL: 30 days (routes rarely change)

---

## Calendar Agent

**Purpose**: Build day-by-day itineraries from collected data.

### Responsibilities
- Cluster POIs geographically (k-means or similar)
- Assign POI clusters to days
- Optimize visit order within each day
- Schedule with time buffers and meal breaks
- Adjust for weather (outdoor activities on nice days)
- Validate feasibility (walking distance, open hours)

### Inputs
```python
pois: list[POI]
weather_forecast: WeatherForecast
distance_matrix: list[list[float]]
constraints: TravelConstraints
```

### Output
```python
Itinerary(
    title="4 Days in Kyoto",
    days=[
        DayItinerary(
            date=date(2025, 11, 10),
            day_number=1,
            items=[
                ItineraryItem(
                    type="poi",
                    start_time=time(9, 0),
                    end_time=time(10, 30),
                    poi=kinkakuji_temple,
                    title="Kinkaku-ji Temple",
                ),
                ItineraryItem(
                    type="travel",
                    start_time=time(10, 30),
                    end_time=time(10, 50),
                    travel_mode="walking",
                    distance_km=1.2,
                ),
                ...
            ],
            total_walking_km=8.5,
            weather_summary="Mainly clear, 10-18°C",
        ),
        ...
    ]
)
```

### Algorithms
1. **Clustering**: K-means on (lat, lon) coordinates
2. **Day Assignment**: Balance POIs across days
3. **Ordering**: TSP heuristic for each day
4. **Scheduling**: Start at 9 AM, add visit durations + travel + buffers
5. **Weather Matching**: Outdoor POIs on good weather days

### Constraints
- Max walking distance: 10 km/day (default)
- Max POIs per day: 6 (default)
- Meal breaks: 60 min for lunch
- Buffer time: 15% of total time for unexpected delays

---

## Export Agent

**Purpose**: Convert finalized itineraries to multiple output formats.

### Responsibilities
- Generate Markdown summaries
- Create ICS calendar files
- Export CSV for spreadsheets
- Generate GeoJSON for maps

### Inputs
```python
itinerary: Itinerary
format: "markdown" | "ics" | "csv" | "geojson"
output_path: Path
```

### Output Formats

#### 1. Markdown
```markdown
# 4 Days in Kyoto

## Day 1 - November 10, 2025
Weather: Mainly clear, 10-18°C

### 9:00 AM - Kinkaku-ji Temple
📍 35.039444, 135.729167
⏱️ 1.5 hours
...
```

#### 2. ICS Calendar
- Each POI as a calendar event
- Location set to coordinates
- Description includes notes and travel time

#### 3. CSV
| Date | Time | Type | Name | Duration | Notes |
|------|------|------|------|----------|-------|
| 2025-11-10 | 09:00 | POI | Kinkaku-ji | 90 min | Temple, historic |

#### 4. GeoJSON
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [135.729167, 35.039444]},
      "properties": {"name": "Kinkaku-ji", "day": 1, "time": "09:00"}
    },
    ...
  ]
}
```

### No External Dependencies
Uses Python standard library:
- Markdown: String templates
- ICS: `ics` library or manual generation
- CSV: `csv` module
- GeoJSON: `json` module

---

## Agent Communication

Agents don't communicate directly—all state flows through **LangGraph**:

```
State → Agent reads → Agent writes → State updated → Next agent reads
```

This ensures:
- Clear data flow
- Easy debugging (inspect state at any point)
- Testability (mock state, test agents in isolation)
- Parallelization (multiple agents can read same state simultaneously)
