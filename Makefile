.PHONY: help install dev-install lint format test docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev-install   - Install dev dependencies"
	@echo "  make lint          - Run linting (ruff + mypy)"
	@echo "  make format        - Format code with ruff"
	@echo "  make test          - Run tests"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start containers"
	@echo "  make docker-down   - Stop containers"
	@echo "  make clean         - Clean build artifacts"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

lint:
	ruff check app
	mypy app

format:
	ruff format app
	ruff check --fix app

test:
	pytest -v

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

lock:
	pip install pip-tools
	pip-compile pyproject.toml -o requirements.txt --strip-extras

clean:
	rm -rf build dist .egg-info __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
