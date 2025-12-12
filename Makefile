.PHONY: install run adk eval tests clean

install:
	uv sync --frozen

run:
	uv run mesop app/main.py

adk:
	uv run adk web

eval:
	uv run pytest eval

tests:
	uv run pytest tests

clean:
	rm -rf app/__pycache__
	rm -rf engine/__pycache__
	rm -rf eval/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache