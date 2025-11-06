# TravelMind

An AI trip planner that builds day-by-day itineraries from natural language requests.

Tell it what you want ("4 days in Kyoto, love temples and coffee"), and it handles the research, route optimization, and scheduling. Uses only free data sources.

**Status**: Early development - core scaffolding complete, agents not yet implemented.

## How it works

1. You describe your trip in plain English
2. AI parses your request and pulls data from free APIs (OpenTripMap, OSM, weather)
3. Agents figure out what to see, when to go, and how to get there
4. You get a day-by-day plan with times, routes, and export options (calendar, map, etc.)

## Setup

```bash
git clone https://github.com/yourusername/travelmind.git
cd travelmind

python -m venv venv
source venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env
```


What's next:
- Implement service clients (OpenTripMap, weather, routing)
- Build agent logic
- Wire up LangGraph workflow
- Add tests




## Tech stack

- LangGraph for multi-agent orchestration
- Pydantic for data validation
- httpx for async API calls
- diskcache for local caching
- pytest, ruff, black, mypy

