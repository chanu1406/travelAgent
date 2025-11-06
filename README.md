# TravelMind

**AI-powered trip planner with multi-agent architecture**

Plan your perfect trip using natural language. TravelMind uses LangGraph to coordinate specialized AI agents that research destinations, check weather, optimize routes, and build personalized day-by-day itineraries—all using free and open data sources.

## Features

- **Conversational Planning**: Describe your trip in plain English
- **Multi-Agent Architecture**: Specialized agents for different planning tasks
- **100% Free Data**: No paid APIs—uses OpenTripMap, OpenStreetMap, Open-Meteo
- **Smart Scheduling**: Balances interests, weather, walking distances, and opening hours
- **Human-in-the-Loop**: Review and adjust plans before finalizing
- **Multiple Export Formats**: Markdown, ICS calendar, CSV, GeoJSON

## Architecture

TravelMind uses **LangGraph** to orchestrate six specialized agents:

| Agent | Purpose | Data Sources |
|-------|---------|--------------|
| **Intent Agent** | Parses user requests into structured parameters | LLM-based NLU |
| **POI Agent** | Finds attractions matching user interests | OpenTripMap, Overpass (OSM) |
| **Weather Agent** | Fetches forecasts to inform scheduling | Open-Meteo |
| **Route Agent** | Calculates travel times and optimal routes | OSRM / OpenRouteService |
| **Calendar Agent** | Builds day-by-day itineraries | Internal logic + agent data |
| **Export Agent** | Generates output files (Markdown, ICS, etc.) | Template-based |

### Workflow

```
User Query → Intent Agent → [POI, Weather, Route Agents] → Calendar Agent → HITL Review → Export Agent → Final Itinerary
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- (Optional) API keys for:
  - OpenTripMap (free tier)
  - OpenRouteService (free tier)
  - LLM provider (OpenAI, Anthropic, or local Ollama)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/travelmind.git
cd travelmind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"

# Copy environment template and configure
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your settings:

```bash
# Required for LLM-based intent parsing
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# Free API keys (sign up links in .env.example)
OPENTRIPMAP_API_KEY=your_key
OPENROUTESERVICE_API_KEY=your_key
```

### Usage

*Application logic coming soon. This is the initial scaffolding.*

```python
# Example usage (to be implemented)
from travelmind import TravelPlanner

planner = TravelPlanner()
itinerary = planner.plan(
    "Plan 4 days in Kyoto, mostly walkable, love coffee shops and temples"
)
print(itinerary.to_markdown())
```

## Project Structure

```
travelmind/
├── src/travelmind/
│   ├── agents/           # Individual agent implementations
│   │   ├── intent.py
│   │   ├── poi.py
│   │   ├── weather.py
│   │   ├── route.py
│   │   ├── calendar.py
│   │   └── export.py
│   ├── models/           # Pydantic data models
│   │   ├── request.py
│   │   ├── poi.py
│   │   ├── weather.py
│   │   └── itinerary.py
│   ├── orchestration/    # LangGraph workflow definitions
│   │   └── graph.py
│   ├── services/         # External API clients
│   │   ├── opentripmap.py
│   │   ├── openmeteo.py
│   │   ├── osm.py
│   │   └── routing.py
│   ├── utils/            # Helpers (caching, rate limiting, etc.)
│   │   ├── cache.py
│   │   ├── rate_limit.py
│   │   └── config.py
│   └── api/              # FastAPI endpoints (future)
│       └── routes.py
├── tests/
│   ├── agents/           # Agent unit tests
│   ├── integration/      # End-to-end tests
│   └── unit/             # Service/util tests
├── docs/                 # Documentation
│   ├── architecture.md
│   ├── agents.md
│   └── api_integrations.md
├── pyproject.toml        # Project metadata and dependencies
├── .env.example          # Environment template
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
# Check code style
ruff check src tests

# Format code
black src tests

# Type checking
mypy src
```

### Code Quality

This project uses:
- **ruff** for fast Python linting
- **black** for code formatting
- **mypy** for type checking
- **pytest** for testing

## Design Principles

1. **Zero-Cost Operations**: Only free-tier APIs and open data
2. **Modular Agents**: Each agent is independent and testable
3. **Responsible Usage**: Caching and rate limiting for public APIs
4. **Type Safety**: Pydantic models throughout
5. **Testability**: Unit and integration tests for all components

## Roadmap

- [x] Project scaffolding
- [ ] Implement Pydantic models for all data structures
- [ ] Build service clients (OpenTripMap, Open-Meteo, OSRM)
- [ ] Implement individual agents
- [ ] Create LangGraph orchestration workflow
- [ ] Add caching and rate limiting
- [ ] Build export functionality (Markdown, ICS, CSV, GeoJSON)
- [ ] Add human-in-the-loop review step
- [ ] Create FastAPI endpoints
- [ ] Write comprehensive tests
- [ ] Add example notebooks and documentation

## Contributing

Contributions welcome! Please read the contributing guidelines (coming soon).

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - AI agent orchestration
- [OpenTripMap](https://opentripmap.io/) - POI data
- [OpenStreetMap](https://www.openstreetmap.org/) - Map data
- [Open-Meteo](https://open-meteo.com/) - Weather forecasts
- [OSRM](http://project-osrm.org/) / [OpenRouteService](https://openrouteservice.org/) - Routing
