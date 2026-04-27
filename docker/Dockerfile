# syntax=docker/dockerfile:1.7
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    PIP_NO_CACHE_DIR=1

# Install uv
RUN pip install --no-cache-dir uv==0.5.11

WORKDIR /app

# Copy lock + project metadata first for better layer caching
COPY pyproject.toml ./
COPY uv.lock* ./

RUN uv sync --frozen --no-install-project || uv sync --no-install-project

# Copy source
COPY . .

# Final install of the project itself
RUN uv sync --all-groups

# Create non-root user (Playwright base image already has pwuser)
USER pwuser

ENV APP_ENV=dev
CMD ["uv", "run", "pytest", "-m", "smoke", "-n", "auto"]
