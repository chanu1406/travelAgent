# TravelMind Architecture

## Overview

TravelMind uses a **multi-agent architecture** orchestrated by **LangGraph** to break down the complex task of trip planning into specialized, manageable components.

## Design Philosophy

1. **Separation of Concerns**: Each agent handles one specific aspect of planning
2. **Composability**: Agents can be tested, optimized, and swapped independently
3. **Zero Cost**: Only free APIs and open data sources
4. **Type Safety**: Pydantic models throughout for validation
5. **Cacheability**: Heavy caching to minimize API calls and improve speed

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                   (CLI / API / Future: Web UI)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                       │
│                  (Workflow State Management)                    │
└─────┬───────────┬───────────┬───────────┬───────────┬──────────┘
      │           │           │           │           │
      ▼           ▼           ▼           ▼           ▼
┌──────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  Intent  │ │   POI   │ │ Weather │ │  Route  │ │Calendar │
│  Agent   │ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │
└────┬─────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │            │           │           │           │
     │            ▼           ▼           ▼           │
     │       ┌─────────────────────────────────┐     │
     │       │    External Data Sources        │     │
     │       ├─────────────────────────────────┤     │
     │       │ • OpenTripMap (attractions)     │     │
     │       │ • OpenStreetMap (restaurants)   │     │
     │       │ • Open-Meteo (weather)          │     │
     │       │ • OSRM/ORS (routing)            │     │
     │       └─────────────────────────────────┘     │
     │                                               │
     └──────────────────┬────────────────────────────┘
                        ▼
              ┌──────────────────┐
              │  HITL Checkpoint │
              │  (Human Review)  │
              └────────┬─────────┘
                       ▼
                 ┌───────────┐
                 │  Export   │
                 │  Agent    │
                 └─────┬─────┘
                       ▼
         ┌──────────────────────────────┐
         │ Output Files                 │
         │ • Markdown                   │
         │ • ICS Calendar               │
         │ • CSV                        │
         │ • GeoJSON                    │
         └──────────────────────────────┘
```

## Workflow Stages

### 1. Intent Parsing
- **Agent**: Intent Agent
- **Input**: Natural language query
- **Output**: Structured `TravelRequest` object
- **LLM**: Required (GPT/Claude/local model)
- **Example**: "4 days in Kyoto" → `{destinations: ["Kyoto"], duration_days: 4, ...}`

### 2. Data Gathering (Parallel)
Three agents work in parallel to collect data:

#### a) POI Discovery
- **Agent**: POI Agent
- **Sources**: OpenTripMap, Overpass (OSM)
- **Output**: List of attractions, restaurants, activities
- **Filters**: By interest categories, ratings, location

#### b) Weather Forecast
- **Agent**: Weather Agent
- **Source**: Open-Meteo
- **Output**: Daily and hourly forecasts
- **Purpose**: Inform indoor/outdoor scheduling

#### c) Route Calculation
- **Agent**: Route Agent
- **Source**: OSRM or OpenRouteService
- **Output**: Distance matrix between POIs
- **Purpose**: Enable clustering and travel time estimation

### 3. Itinerary Building
- **Agent**: Calendar Agent
- **Input**: POIs, weather, routes, constraints
- **Logic**:
  1. Cluster POIs by geographic proximity
  2. Assign clusters to days
  3. Optimize visit order (TSP heuristic)
  4. Schedule with time buffers and meal breaks
  5. Adjust for weather (outdoor activities on nice days)
- **Output**: Day-by-day itinerary with time slots

### 4. Human Review (HITL)
- **Checkpoint**: Human-in-the-Loop
- **Purpose**: User can review and request changes
- **Actions**:
  - Approve and proceed to export
  - Lock specific items (e.g., "must visit X at noon")
  - Request re-planning with adjustments
- **Loop**: Can return to Calendar Agent for revisions

### 5. Export
- **Agent**: Export Agent
- **Input**: Finalized itinerary
- **Output**: Multiple file formats
  - **Markdown**: Human-readable trip summary
  - **ICS**: Import to calendar apps
  - **CSV**: Spreadsheet for custom analysis
  - **GeoJSON**: Map visualization

## Data Models

All data flows through type-safe Pydantic models:

- **Request Models**: `TravelRequest`, `TravelConstraints`
- **POI Models**: `POI`, `OpeningHours`, `POISearchResult`
- **Weather Models**: `WeatherForecast`, `DailyForecast`, `HourlyForecast`
- **Itinerary Models**: `Itinerary`, `DayItinerary`, `ItineraryItem`

## State Management

LangGraph maintains a shared `TravelPlanningState` that flows through the workflow:

```python
class TravelPlanningState(TypedDict):
    user_query: str
    travel_request: dict
    pois: list[POI]
    weather_forecast: WeatherForecast
    distance_matrix: list[list[float]]
    itinerary: Itinerary
    hitl_approved: bool
    output_files: dict[str, str]
```

Each agent reads its inputs from the state and writes its outputs back.

## Caching Strategy

To minimize API calls and improve performance:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| POI data | 7 days | Tourist attractions rarely change |
| Weather forecasts | 6 hours | Updates throughout the day |
| Routes | 30 days | Road networks change slowly |
| LLM responses | None | Query-dependent, no cache |

Cache is implemented with `diskcache` for persistence across runs.

## Rate Limiting

Each external service has rate limits:

| Service | Limit | Implementation |
|---------|-------|----------------|
| OpenTripMap | 1 req/s, 500/day | Token bucket |
| Open-Meteo | 10k/day | Generous, minimal limiting |
| OSRM | ~2 req/s | Token bucket |
| OpenRouteService | 40/min | Token bucket |
| Overpass (OSM) | ~2 req/s | Token bucket |

## Error Handling

- **API failures**: Retry with exponential backoff (3 attempts)
- **Missing data**: Graceful degradation (e.g., skip weather if unavailable)
- **User clarification**: Exit workflow and prompt for missing info
- **Validation errors**: Caught by Pydantic, returned to user

## Future Enhancements

1. **Real-time transit**: Integrate GTFS data for public transport
2. **Accommodation booking**: Suggest hotels based on itinerary
3. **Cost estimation**: Track admission fees and meal budgets
4. **Multi-city trips**: Support complex itineraries across regions
5. **Collaborative planning**: Multiple users editing same trip
6. **Mobile app**: Native iOS/Android interface
7. **Real-time updates**: Push notifications for weather changes

## Technology Stack

- **Orchestration**: LangGraph
- **Models**: Pydantic v2
- **HTTP**: httpx (async)
- **Caching**: diskcache
- **API**: FastAPI (future)
- **Testing**: pytest, httpx-mock
- **Linting**: ruff, black, mypy
