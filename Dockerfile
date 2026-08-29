# ==========================================
# BramTech VTU - Django Application
# ==========================================

FROM python:3.12-slim-bookworm AS base

# System dependencies
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    DJANGO_SETTINGS_MODULE=config.settings.dev

# Install OS-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user matching host UID for volume permissions
RUN groupadd -g 1000 django && useradd -u 1000 -g django -m django
# Create app directory
WORKDIR /app

# Install Python dependencies (cache-optimized layer)
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application source
COPY src/ /app/

# Ensure django user owns everything
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose Django port
EXPOSE 8000

# Default command (overridden by docker-compose for dev)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]