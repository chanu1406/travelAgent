# Getting Started with TravelMind

Quick start guide for setting up and developing TravelMind.

## Prerequisites

- Python 3.11 or higher
- pip and venv
- (Optional) API keys for external services

## Installation

### 1. Clone and Setup Environment

```bash
cd TravelAgent  # You're already here!

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# At minimum, you need an LLM API key (OpenAI or Anthropic)
```

Required keys:
- **LLM**: Either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (for intent parsing)
- **OpenTripMap**: `OPENTRIPMAP_API_KEY` (free, get at https://opentripmap.io/)
- **OpenRouteService** (optional): `OPENROUTESERVICE_API_KEY` (free, get at https://openrouteservice.org/)

Optional (no keys needed):
- Open-Meteo: Free, no key
- OSRM: Free, no key
- Overpass (OSM): Free, no key

### 3. Verify Installation

```bash
# Run tests (they should pass but many are NotImplementedError stubs)
make test

# Try the example command (will show stub message)
make run
```

## Project Structure

```
TravelAgent/
├── src/travelmind/          # Main package
│   ├── agents/              # Agent implementations
│   ├── models/              # Pydantic data models
│   ├── services/            # External API clients
│   ├── utils/               # Utilities (cache, rate limit)
│   ├── orchestration/       # LangGraph workflow
│   └── api/                 # FastAPI routes (stub)
├── tests/                   # Test suite
│   ├── agents/             # Agent tests
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                    # Documentation
├── .env.example            # Environment template
├── pyproject.toml          # Project config
└── README.md
```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/agents/test_intent.py

# Run specific test
pytest tests/agents/test_intent.py::TestIntentAgent::test_parse_simple_query
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Type check
make type-check

# Run all checks
make lint && make format && make type-check && make test
```

### Adding New Features

1. **Create models first** ([src/travelmind/models/](../src/travelmind/models/))
   - Define Pydantic models for your data structures
   - Ensures type safety throughout

2. **Implement service clients** ([src/travelmind/services/](../src/travelmind/services/))
   - Add API client for external data source
   - Use caching and rate limiting decorators
   - Write unit tests with mocked responses

3. **Build agents** ([src/travelmind/agents/](../src/travelmind/agents/))
   - Implement agent logic using services
   - Each agent reads/writes specific state fields
   - Test in isolation

4. **Wire into LangGraph** ([src/travelmind/orchestration/graph.py](../src/travelmind/orchestration/graph.py))
   - Add node function for your agent
   - Connect edges in workflow
   - Test end-to-end

5. **Add tests**
   - Unit tests for services and utils
   - Agent tests with mocked services
   - Integration tests for full workflow

## Next Steps

### Immediate (Core Functionality)

1. **Implement Pydantic models** (already scaffolded)
   - Validate field constraints
   - Add computed properties

2. **Build service clients**
   - Start with OpenTripMap
   - Then Open-Meteo
   - Then routing services
   - Test with real APIs

3. **Implement Intent Agent**
   - Choose LLM (GPT-4, Claude, or local Llama)
   - Use structured output (function calling or JSON mode)
   - Handle clarifications

4. **Build POI Agent**
   - Query OpenTripMap and OSM
   - Deduplicate results
   - Rank by relevance

5. **Implement Weather Agent**
   - Fetch Open-Meteo forecasts
   - Categorize days
   - Find best activity windows

6. **Build Route Agent**
   - Integrate OSRM or OpenRouteService
   - Compute distance matrices
   - Optimize visit order

7. **Implement Calendar Agent**
   - Cluster POIs by day
   - Schedule with time buffers
   - Match weather to activities

8. **Build Export Agent**
   - Markdown templates
   - ICS calendar generation
   - CSV and GeoJSON export

9. **Wire LangGraph workflow**
   - Connect all agents
   - Add HITL checkpoint
   - Handle errors gracefully

### Future Enhancements

- FastAPI web service
- Real-time transit data
- Accommodation suggestions
- Cost estimation
- Multi-user collaboration
- Mobile app

## Development Tips

### Caching
Use caching to speed up development and avoid hitting rate limits:

```python
from travelmind.utils.cache import async_cached

@async_cached(ttl=3600)  # Cache for 1 hour
async def fetch_pois(location: str) -> list:
    # Expensive API call
    ...
```

### Rate Limiting
Protect external APIs:

```python
from travelmind.utils.rate_limit import rate_limited

@rate_limited("opentripmap")  # Respects 1 req/s limit
async def search_opentripmap(query: str):
    ...
```

### Testing with Mocks
Use `httpx-mock` for testing without real API calls:

```python
def test_poi_search(httpx_mock):
    httpx_mock.add_response(
        url="https://api.opentripmap.com/...",
        json={"features": [...]}
    )
    result = await poi_agent.search("Kyoto")
```

### Configuration
All settings in [src/travelmind/utils/config.py](../src/travelmind/utils/config.py):

```python
from travelmind.utils.config import settings

# Access configuration
cache_dir = settings.cache_dir
api_key = settings.opentripmap_api_key
```

## Getting Help

- **Documentation**: See [docs/](../docs/) for detailed guides
- **Architecture**: [docs/architecture.md](architecture.md)
- **Agent Details**: [docs/agents.md](agents.md)
- **API Integration**: [docs/api_integrations.md](api_integrations.md)

## Contributing

1. Create a feature branch
2. Write tests first (TDD)
3. Implement feature
4. Ensure all tests pass
5. Run linting and type checking
6. Submit PR with clear description

## Common Issues

### Import Errors
Make sure you installed in editable mode:
```bash
pip install -e ".[dev]"
```

### API Key Errors
Check your `.env` file:
```bash
cat .env | grep API_KEY
```

### Rate Limit Errors
- Check cache is working
- Reduce request frequency
- Use longer cache TTLs during development

### Type Errors
Run mypy to catch issues:
```bash
make type-check
```

Happy coding! Let's make travel planning effortless.
