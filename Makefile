.PHONY: setup test coverage lint format typecheck check

setup:
	uv sync --locked

test:
	uv run pytest -v

coverage:
	uv run pytest --cov --cov-report=term-missing

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

check: lint typecheck test
