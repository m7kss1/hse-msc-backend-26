.PHONY: setup dev test lint format typecheck check

setup:
	uv sync --locked

dev:
	uv run fastapi dev

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

check: lint typecheck test
