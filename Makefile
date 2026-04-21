.PHONY: install install-dev run test

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload

test:
	pytest -q
