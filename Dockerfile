FROM python:3.13-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (--no-dev excludes pytest, debugpy, etc.)
RUN uv sync --frozen --no-dev

# Create non-root user with home directory (required by HF Spaces)
RUN groupadd -g 900 mesop && \
    useradd -u 900 -s /bin/bash -g mesop -m mesop
USER mesop

# Copy application
COPY --chown=mesop:mesop . /srv/app
WORKDIR /srv/app

# Run with gunicorn on port 9200
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:9200", "app.main:me"]
