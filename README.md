# TravelMind AI Trip Planner

An intelligent multi-agent travel planning system that transforms natural language travel requests into complete, optimized itineraries.

Tell it what you want ("I want to visit Kyoto temples for 3 days starting November 10"), and it automatically discovers POIs, checks weather, optimizes routes, and generates a complete day-by-day itinerary with exports to JSON, Markdown, and ICS calendar formats.

**Status**: ✅ All core features complete and working!

## What It Does

1. **Parses Intent** - Understands your destination, dates, interests using Google Gemini 2.0 Flash
2. **Discovers POIs** - Finds relevant points of interest via Geoapify API
3. **Checks Weather** - Fetches real-time forecasts from Open-Meteo
4. **Optimizes Routes** - Calculates distances and optimal visit order using OSRM
5. **Builds Itinerary** - Creates day-by-day schedules with realistic timings
6. **Exports Multiple Formats** - Generates JSON, Markdown, and ICS calendar files

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file with:
```bash
GOOGLE_API_KEY=your_google_gemini_key
GEOAPIFY_API_KEY=your_geoapify_key
```

**Get free API keys:**
- Google Gemini: https://ai.google.dev/ (1.5M tokens/day free)
- Geoapify: https://www.geoapify.com/ (3,000 requests/day free)
- Open-Meteo: No key needed (open source)
- OSRM: No key needed (open source)

### 3. Run the Demo

```bash
# End-to-end workflow demo
python demo_end_to_end.py

# Interactive intent parser
python interactive_intent.py
```

### 4. Check Generated Outputs

Files created in `output/`:
- `trip.json` - Complete structured itinerary data
- `trip.md` - Human-readable trip summary
- `trip.ics` - Calendar file (import to Google Calendar, Apple Calendar, etc.)

## Example Output

**Query:**
```
I want to visit Kyoto temples and cultural sites for 3 days starting November 10, 2025
```

**Generated Itinerary:**
- 3-day trip with 8 POIs
- Weather-aware scheduling
- Optimized walking routes (3.61 km total)
- Realistic timings (09:00 - 12:03 each day)
- Complete timeline with travel segments

## Testing Individual Components

```bash
python test_intent.py       # Test intent parsing
python test_poi_agent.py    # Test POI discovery
python test_route_agent.py  # Test route optimization
python test_calendar_agent.py # Test itinerary scheduling
python test_export.py       # Test export formats
```

## Architecture

**Multi-Agent System:**
- **Intent Agent** - Natural language parsing (Google Gemini)
- **POI Agent** - Point of interest discovery (Geoapify)
- **Weather Agent** - Weather forecasting (Open-Meteo)
- **Route Agent** - Route optimization (OSRM)
- **Calendar Agent** - Itinerary scheduling
- **Export Agent** - Multi-format output generation

**Tech Stack:**
- Python 3.11+ with async/await
- LangChain for LLM integration
- Pydantic v2 for type-safe models
- httpx for async HTTP requests
- Free APIs only (Google Gemini, Geoapify, Open-Meteo, OSRM)

## Project Structure

```
TravelAgent/
├── src/travelmind/
│   ├── agents/          # Multi-agent system
│   │   ├── intent.py    # Natural language parsing
│   │   ├── poi.py       # POI discovery
│   │   ├── weather.py   # Weather forecasting
│   │   ├── route.py     # Route optimization
│   │   ├── calendar.py  # Itinerary building
│   │   └── export.py    # Output generation
│   ├── models/          # Pydantic data models
│   ├── services/        # API clients
│   └── utils/           # Configuration
├── tests/               # Individual agent tests
├── output/              # Generated itineraries
└── demo_end_to_end.py   # Full workflow demo
```

## Features

✅ Smart geographic clustering to minimize travel
✅ Weather-aware activity selection
✅ Route optimization using TSP heuristics
✅ Realistic time estimates
✅ Multi-format export (JSON, Markdown, ICS)
✅ All core agents implemented and tested

## Next Steps (Optional)

- LangGraph workflow orchestration
- Multi-city trip support
- Budget optimization
- Restaurant recommendations
- Public transit routing
- Interactive web UI

