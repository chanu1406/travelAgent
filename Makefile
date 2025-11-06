.PHONY: help install install-dev test lint format type-check clean run

help:
	@echo "TravelMind - Development Commands"
	@echo ""
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linter (ruff)"
	@echo "  make format       Format code (black + ruff)"
	@echo "  make type-check   Run type checker (mypy)"
	@echo "  make clean        Clean cache and build files"
	@echo "  make run          Run example query"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=travelmind --cov-report=html

lint:
	ruff check src tests

format:
	black src tests
	ruff check --fix src tests

type-check:
	mypy src

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .cache

run:
	python -m travelmind "Plan 3 days in Kyoto, love temples and coffee"
