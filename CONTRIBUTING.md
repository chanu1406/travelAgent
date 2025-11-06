# Contributing to TravelMind

Thanks for your interest in contributing!

## Getting Started

1. Fork the repo
2. Create a branch for your feature
3. Make your changes
4. Run tests and linting
5. Submit a PR

## Development Setup

```bash
git clone https://github.com/yourusername/travelmind.git
cd travelmind

python -m venv venv
source venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env
```

## Before Submitting

```bash
make test          # all tests pass
make format        # code is formatted
make lint          # no linting errors
make type-check    # no type errors
```

## Commit Messages

Keep them simple and descriptive:

```
feat: add weather categorization logic
fix: handle missing POI coordinates
docs: update API integration guide
test: add route optimization tests
```

No need for fancy formatting or co-author tags - just clear, concise descriptions.

## Code Style

- Follow existing patterns
- Add type hints
- Write docstrings for public functions
- Keep functions focused and small

## Questions?

Open an issue or discussion on GitHub.
