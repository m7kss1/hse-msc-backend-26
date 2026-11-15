# Homework 2

Задачи на asyncio и потоки, Python 3.12 и uv

## Подготовка

```bash
uv sync --locked
```

## Тесты

```bash
uv run pytest -v
```

Одну задачу можно проверить из её папки

```bash
cd hw2/01_async_prices
uv run pytest -v
```

Для остальных задач используются папки `02_find_blocking` и `03_thread_safe_lru`

После активации окружения работает и команда из условия

```bash
source .venv/bin/activate
cd hw2/01_async_prices
pytest -v
```

Все проверки (Ruff, mypy, pytest): `make check`

Покрытие тестами: `make coverage`

GitHub Actions запускает проверки на Python 3.12 и 3.13
