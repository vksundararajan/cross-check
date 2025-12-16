.PHONY: help install run adk eval tests coverage clean

# Display available commands
help:
	@echo ""
	@echo "Cross-Check Project Commands"
	@echo "============================"
	@echo ""
	@echo "  make install   - Install project dependencies using uv"
	@echo "  make serve     - Run the main Mesop web application"
	@echo "  make dev       - Start the ADK web interface"
	@echo "  make eval      - Run evaluation tests"
	@echo "  make tests     - Run unit tests"
	@echo "  make coverage  - Run tests with coverage report (HTML output)"
	@echo "  make clean     - Remove cache files and directories"

# Install project dependencies using uv
install:
	uv sync --frozen

# Run the main Mesop web application
serve:
	uv run mesop app/main.py

# Start the ADK web interface
dev:
	uv run adk web

# Run evaluation tests with verbose output
eval:
	uv run pytest eval -s --disable-warnings

# Run unit tests
tests:
	uv run pytest tests --disable-warnings

# Run tests with coverage report (generates HTML report in htmlcov/)
coverage:
	uv run pytest --cov=engine --cov-report=html eval/ tests/

# Remove cache files and directories
clean:
	rm -rf app/__pycache__
	rm -rf engine/__pycache__
	rm -rf eval/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .coverage.xml