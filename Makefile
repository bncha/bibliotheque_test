.PHONY: help install test lint format run clean

help:
	@echo "Available commands:"
	@echo "  make install  - Install project dependencies with dev tools"
	@echo "  make test     - Run test suite with pytest"
	@echo "  make lint     - Run code quality checks with ruff"
	@echo "  make format   - Format code with ruff"
	@echo "  make run      - Start FastAPI server with live reload"
	@echo "  make clean    - Remove build artifacts and caches"

install:
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff check --fix src tests
	ruff format src tests

run:
	uvicorn library.api.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build dist src/*.egg-info
